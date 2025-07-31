#!/usr/bin/env python3
"""
Quick verification script for WebFetch MCP Server
Tests basic functionality without full client implementation
"""

import asyncio
import json
import subprocess
import sys

async def test_mcp_server():
    """Test that the MCP server responds correctly to basic requests"""
    
    print("🧪 Verifying WebFetch MCP Server...")
    print("=" * 50)
    
    # Start the server process
    process = await asyncio.create_subprocess_exec(
        sys.executable, "main.py", "--log-level", "INFO",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "verify-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        # Read the response with timeout
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(), timeout=10.0
            )
            response = json.loads(response_line.decode().strip())
            
            if response.get("id") == 1 and "result" in response:
                print("✅ Server initialization: SUCCESS")
                print(f"   Protocol version: {response['result'].get('protocolVersion', 'unknown')}")
                print(f"   Server name: {response['result'].get('serverInfo', {}).get('name', 'unknown')}")
            else:
                print("❌ Server initialization: FAILED")
                print(f"   Response: {response}")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Server initialization: TIMEOUT")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Server initialization: JSON decode error - {e}")
            return False
        
        # Test listing tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        request_json = json.dumps(list_tools_request) + "\n"
        process.stdin.write(request_json.encode())
        await process.stdin.drain()
        
        try:
            response_line = await asyncio.wait_for(
                process.stdout.readline(), timeout=10.0
            )
            response = json.loads(response_line.decode().strip())
            
            if response.get("id") == 2 and "result" in response:
                tools = response["result"].get("tools", [])
                print(f"✅ Tools listing: SUCCESS ({len(tools)} tools found)")
                
                expected_tools = [
                    "fetch_webpage",
                    "fetch_multiple_pages", 
                    "search_webpage_content",
                    "extract_links",
                    "get_page_metadata"
                ]
                
                found_tools = [tool["name"] for tool in tools]
                
                for expected_tool in expected_tools:
                    if expected_tool in found_tools:
                        print(f"   ✅ {expected_tool}")
                    else:
                        print(f"   ❌ {expected_tool} (missing)")
                
                # Check if all expected tools are present
                if all(tool in found_tools for tool in expected_tools):
                    print("✅ All expected tools are available")
                    return True
                else:
                    print("❌ Some expected tools are missing")
                    return False
                    
            else:
                print("❌ Tools listing: FAILED")
                print(f"   Response: {response}")
                return False
                
        except asyncio.TimeoutError:
            print("❌ Tools listing: TIMEOUT")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Tools listing: JSON decode error - {e}")
            return False
    
    finally:
        # Clean up the process
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

async def main():
    """Main verification function"""
    
    print("🚀 WebFetch MCP Server Verification")
    print("=" * 60)
    
    success = await test_mcp_server()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: WebFetch MCP Server is working correctly!")
        print("\nNext steps:")
        print("1. Build Docker image: docker build -t webfetch-mcp .")
        print("2. Run with Docker: docker run -i webfetch-mcp")
        print("3. Integrate with your preferred MCP client")
        print("4. Test with real web URLs")
    else:
        print("❌ FAILED: WebFetch MCP Server has issues")
        print("\nTroubleshooting:")
        print("1. Check that all dependencies are installed")
        print("2. Review error messages above")
        print("3. Ensure Python version compatibility")
        print("4. Check the server logs for more details")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
