#!/usr/bin/env python3
"""
Example HTTP client for WebFetch MCP Server
Shows how agents can access the MCP functionality via HTTP
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List

class WebFetchHTTPClient:
    """HTTP client for WebFetch MCP Server"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the server is healthy"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def list_tools(self) -> Dict[str, Any]:
        """Get list of available tools"""
        async with self.session.get(f"{self.base_url}/tools") as response:
            return await response.json()
    
    async def fetch_webpage(self, url: str, extract_content: bool = True, 
                           include_metadata: bool = True, timeout: int = 30) -> Dict[str, Any]:
        """Fetch content from a webpage"""
        data = {
            "url": url,
            "extract_content": extract_content,
            "include_metadata": include_metadata,
            "timeout": timeout
        }
        
        async with self.session.post(f"{self.base_url}/fetch", json=data) as response:
            return await response.json()
    
    async def fetch_multiple_pages(self, urls: List[str], extract_content: bool = True,
                                  include_metadata: bool = True, max_concurrent: int = 5,
                                  timeout: int = 30) -> Dict[str, Any]:
        """Fetch content from multiple webpages"""
        data = {
            "urls": urls,
            "extract_content": extract_content,
            "include_metadata": include_metadata,
            "max_concurrent": max_concurrent,
            "timeout": timeout
        }
        
        async with self.session.post(f"{self.base_url}/fetch-multiple", json=data) as response:
            return await response.json()
    
    async def search_webpage_content(self, url: str, search_terms: List[str],
                                   case_sensitive: bool = False, context_chars: int = 200) -> Dict[str, Any]:
        """Search for content in a webpage"""
        data = {
            "url": url,
            "search_terms": search_terms,
            "case_sensitive": case_sensitive,
            "context_chars": context_chars
        }
        
        async with self.session.post(f"{self.base_url}/search", json=data) as response:
            return await response.json()
    
    async def extract_links(self, url: str, filter_internal: bool = False,
                           filter_external: bool = False, include_anchors: bool = False) -> Dict[str, Any]:
        """Extract links from a webpage"""
        data = {
            "url": url,
            "filter_internal": filter_internal,
            "filter_external": filter_external,
            "include_anchors": include_anchors
        }
        
        async with self.session.post(f"{self.base_url}/links", json=data) as response:
            return await response.json()
    
    async def get_page_metadata(self, url: str) -> Dict[str, Any]:
        """Get metadata from a webpage"""
        data = {"url": url}
        
        async with self.session.post(f"{self.base_url}/metadata", json=data) as response:
            return await response.json()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Generic tool calling method"""
        data = {
            "tool_name": tool_name,
            "arguments": arguments
        }
        
        async with self.session.post(f"{self.base_url}/tools/call", json=data) as response:
            return await response.json()

async def demo_http_client():
    """Demonstrate the HTTP client"""
    
    print("🌐 WebFetch MCP HTTP Client Demo")
    print("=" * 50)
    
    try:
        async with WebFetchHTTPClient() as client:
            # Health check
            print("🏥 Health Check:")
            health = await client.health_check()
            print(f"   Status: {health.get('status', 'unknown')}")
            
            # List tools
            print("\n📋 Available Tools:")
            tools_response = await client.list_tools()
            tools = tools_response.get('tools', [])
            for tool in tools:
                print(f"   • {tool['name']}: {tool['description']}")
            
            # Demo 1: Fetch a webpage
            print("\n🔍 Demo 1: Fetching a webpage...")
            result = await client.fetch_webpage("https://httpbin.org/html")
            
            if result.get('success'):
                data = result.get('result', {})
                print(f"   ✅ Status: {data.get('status_code')}")
                print(f"   📄 Title: {data.get('metadata', {}).get('title', 'N/A')}")
                content = data.get('content', '')
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    print(f"   📝 Content preview: {preview}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
            
            # Demo 2: Search content
            print("\n🔎 Demo 2: Searching webpage content...")
            search_result = await client.search_webpage_content(
                "https://httpbin.org/html", 
                ["html", "test", "example"]
            )
            
            if search_result.get('success'):
                data = search_result.get('result', {})
                print(f"   🎯 Found {data.get('total_matches', 0)} matches")
                for i, match in enumerate(data.get('matches', [])[:3]):
                    print(f"   Match {i+1}: '{match.get('term')}' at position {match.get('position')}")
            else:
                print(f"   ❌ Error: {search_result.get('error')}")
            
            # Demo 3: Extract links
            print("\n🔗 Demo 3: Extracting links...")
            links_result = await client.extract_links("https://httpbin.org/links/3")
            
            if links_result.get('success'):
                data = links_result.get('result', {})
                print(f"   🔗 Found {data.get('total_links', 0)} links")
                for i, link in enumerate(data.get('links', [])[:3]):
                    print(f"   Link {i+1}: {link.get('text')} -> {link.get('url')}")
            else:
                print(f"   ❌ Error: {links_result.get('error')}")
    
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {str(e)}")
        print("   Make sure the HTTP server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_integration_examples():
    """Show integration examples for different agent types"""
    
    print("\n🤖 Agent Integration Examples")
    print("=" * 60)
    
    print("\n1. 🐍 Python Agent:")
    print("""
    import aiohttp
    
    async def agent_fetch_webpage(url: str):
        async with aiohttp.ClientSession() as session:
            data = {"url": url, "extract_content": True}
            async with session.post("http://your-server:8000/fetch", json=data) as response:
                result = await response.json()
                return result['result'] if result['success'] else None
    """)
    
    print("\n2. 🟨 JavaScript/Node.js Agent:")
    print("""
    const axios = require('axios');
    
    async function agentFetchWebpage(url) {
        try {
            const response = await axios.post('http://your-server:8000/fetch', {
                url: url,
                extract_content: true
            });
            return response.data.success ? response.data.result : null;
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }
    """)
    
    print("\n3. 🦀 Rust Agent:")
    print("""
    use reqwest::Client;
    use serde_json::json;
    
    async fn agent_fetch_webpage(url: &str) -> Result<serde_json::Value, Box<dyn std::error::Error>> {
        let client = Client::new();
        let response = client
            .post("http://your-server:8000/fetch")
            .json(&json!({
                "url": url,
                "extract_content": true
            }))
            .send()
            .await?;
        
        let result: serde_json::Value = response.json().await?;
        Ok(result)
    }
    """)
    
    print("\n4. 🔗 cURL Command:")
    print("""
    curl -X POST "http://your-server:8000/fetch" \\
         -H "Content-Type: application/json" \\
         -d '{"url": "https://example.com", "extract_content": true}'
    """)

async def main():
    """Main demo function"""
    
    print("🚀 WebFetch MCP HTTP Integration Guide")
    print("=" * 60)
    
    # Show integration examples
    show_integration_examples()
    
    # Ask if user wants to run live demo
    try:
        response = input("\n🤔 Would you like to run a live demo? (Server must be running on localhost:8000) (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            await demo_http_client()
        else:
            print("📖 Live demo skipped.")
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled.")
    
    print("\n📚 Next Steps:")
    print("1. Start the HTTP server: python http_server.py")
    print("2. Or use Docker: docker-compose -f docker-compose-http.yml up")
    print("3. Access via HTTP at: http://localhost:8000")
    print("4. View API docs at: http://localhost:8000/docs (FastAPI auto-docs)")
    print("5. Integrate with your agents using the examples above")

if __name__ == "__main__":
    asyncio.run(main())
