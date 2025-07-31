#!/usr/bin/env python3
"""
Example usage of WebFetch MCP Server
Shows how to interact with the MCP server programmatically
"""

import asyncio
import json
import subprocess
import sys
from typing import Dict, Any

class MCPClient:
    """Simple MCP client for demonstration"""
    
    def __init__(self, server_command: list):
        self.server_command = server_command
        self.process = None
        self.request_id = 0
    
    async def start(self):
        """Start the MCP server process"""
        self.process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "example-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_request(init_request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"Initialization failed: {response['error']}")
        
        print("✅ MCP Server initialized successfully")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self._send_request(request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }
        
        await self._send_request(request)
        response = await self._read_response()
        
        if response.get("error"):
            raise Exception(f"List tools failed: {response['error']}")
        
        return response.get("result", {})
    
    async def close(self):
        """Close the MCP server process"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
    
    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id
    
    async def _send_request(self, request: Dict[str, Any]):
        """Send a request to the server"""
        if not self.process:
            raise Exception("Server not started")
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
    
    async def _read_response(self) -> Dict[str, Any]:
        """Read a response from the server"""
        if not self.process:
            raise Exception("Server not started")
        
        line = await self.process.stdout.readline()
        if not line:
            raise Exception("Server closed unexpectedly")
        
        try:
            return json.loads(line.decode().strip())
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {e}")

async def demo_webfetch_tools():
    """Demonstrate WebFetch MCP tools"""
    
    print("🌐 WebFetch MCP Server Demo")
    print("=" * 50)
    
    # Use Docker command (adjust path as needed)
    server_command = ["python3", "/workspace/Orbital-mcp/WebFetch/main.py"]
    
    try:
        client = MCPClient(server_command)
        await client.start()
        
        # List available tools
        print("\n📋 Available Tools:")
        tools_result = await client.list_tools()
        for tool in tools_result.get("tools", []):
            print(f"   • {tool['name']}: {tool['description']}")
        
        # Demo 1: Fetch a simple webpage
        print("\n🔍 Demo 1: Fetching a webpage...")
        result1 = await client.call_tool("fetch_webpage", {
            "url": "https://httpbin.org/html",
            "extract_content": True,
            "include_metadata": True
        })
        
        print("   Result preview:")
        content = result1.get("content", [{}])
        if isinstance(content, list) and content:
            content_text = content[0].get("text", "")
            preview = content_text[:200] + "..." if len(content_text) > 200 else content_text
            print(f"   Content: {preview}")
        
        # Demo 2: Get page metadata
        print("\n📊 Demo 2: Getting page metadata...")
        result2 = await client.call_tool("get_page_metadata", {
            "url": "https://httpbin.org/html"
        })
        
        print("   Metadata:")
        content = result2.get("content", [{}])
        if isinstance(content, list) and content:
            metadata_str = content[0].get("text", "{}")
            try:
                metadata = json.loads(metadata_str)
                print(f"   Title: {metadata.get('title', 'N/A')}")
                print(f"   URL: {metadata.get('url', 'N/A')}")
                print(f"   Status: {metadata.get('status_code', 'N/A')}")
            except json.JSONDecodeError:
                print(f"   Raw response: {metadata_str[:100]}...")
        
        # Demo 3: Search for content
        print("\n🔎 Demo 3: Searching webpage content...")
        result3 = await client.call_tool("search_webpage_content", {
            "url": "https://httpbin.org/html",
            "search_terms": ["html", "test"],
            "case_sensitive": False
        })
        
        print("   Search results:")
        content = result3.get("content", [{}])
        if isinstance(content, list) and content:
            search_str = content[0].get("text", "{}")
            try:
                search_data = json.loads(search_str)
                print(f"   Total matches: {search_data.get('total_matches', 0)}")
                for i, match in enumerate(search_data.get('matches', [])[:3]):
                    print(f"   Match {i+1}: '{match.get('term')}' at position {match.get('position')}")
            except json.JSONDecodeError:
                print(f"   Raw response: {search_str[:100]}...")
        
        await client.close()
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Ensure the MCP server is built: docker build -t webfetch-mcp .")
        print("2. Check that all dependencies are installed")
        print("3. Verify the server command path is correct")

def demo_integration_patterns():
    """Show different integration patterns"""
    
    print("\n🔗 Integration Patterns")
    print("=" * 50)
    
    print("\n1. Docker Integration:")
    print("   server_command = ['docker', 'run', '-i', 'webfetch-mcp']")
    
    print("\n2. Local Python Integration:")
    print("   server_command = ['python3', 'main.py']")
    
    print("\n3. Claude Desktop Integration:")
    claude_config = {
        "mcpServers": {
            "webfetch": {
                "command": "docker",
                "args": ["run", "-i", "--rm", "webfetch-mcp:latest"]
            }
        }
    }
    print(f"   {json.dumps(claude_config, indent=3)}")
    
    print("\n4. Custom Application Integration:")
    print("""   
   from mcp.client.stdio import stdio_client
   
   async with stdio_client(['python3', 'main.py']) as client:
       result = await client.call_tool('fetch_webpage', {
           'url': 'https://example.com'
       })
   """)

async def main():
    """Main demo function"""
    
    print("🚀 WebFetch MCP Server Usage Examples")
    print("=" * 60)
    
    # Show integration patterns first
    demo_integration_patterns()
    
    # Ask user if they want to run live demo
    try:
        response = input("\n🤔 Would you like to run a live demo? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            await demo_webfetch_tools()
        else:
            print("\n📖 Live demo skipped. Review the integration patterns above.")
    except KeyboardInterrupt:
        print("\n\n👋 Demo cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print("\n📚 Next Steps:")
    print("1. Build the Docker image: docker build -t webfetch-mcp .")
    print("2. Test the server: python test_webfetch.py")
    print("3. Integrate with your MCP client")
    print("4. Check the full documentation in README.md")

if __name__ == "__main__":
    asyncio.run(main())
