#!/usr/bin/env python3
"""
WebFetch MCP Server
A Model Context Protocol server for fetching web data with various capabilities.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
import sys
import argparse

import aiohttp
import trafilatura
from bs4 import BeautifulSoup
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("webfetch-mcp")

class WebFetchMCP:
    """WebFetch MCP Server implementation"""
    
    def __init__(self):
        self.server = Server("webfetch-mcp")
        self.session: Optional[aiohttp.ClientSession] = None
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="fetch_webpage",
                    description="Fetch and extract content from a webpage with smart content extraction",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch content from"
                            },
                            "extract_content": {
                                "type": "boolean",
                                "description": "Whether to extract main content using intelligent parsing (default: true)",
                                "default": True
                            },
                            "include_metadata": {
                                "type": "boolean", 
                                "description": "Whether to include page metadata (title, description, etc.)",
                                "default": True
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Request timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="fetch_multiple_pages",
                    description="Fetch content from multiple webpages in parallel",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "urls": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of URLs to fetch"
                            },
                            "extract_content": {
                                "type": "boolean",
                                "description": "Whether to extract main content (default: true)",
                                "default": True
                            },
                            "include_metadata": {
                                "type": "boolean",
                                "description": "Whether to include page metadata",
                                "default": True
                            },
                            "max_concurrent": {
                                "type": "number",
                                "description": "Maximum concurrent requests (default: 5)",
                                "default": 5
                            },
                            "timeout": {
                                "type": "number",
                                "description": "Request timeout in seconds (default: 30)",
                                "default": 30
                            }
                        },
                        "required": ["urls"]
                    }
                ),
                Tool(
                    name="search_webpage_content",
                    description="Fetch a webpage and search for specific content or patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to fetch and search"
                            },
                            "search_terms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Terms to search for in the content"
                            },
                            "case_sensitive": {
                                "type": "boolean",
                                "description": "Whether search should be case sensitive (default: false)",
                                "default": False
                            },
                            "context_chars": {
                                "type": "number",
                                "description": "Number of characters to include around matches (default: 200)",
                                "default": 200
                            }
                        },
                        "required": ["url", "search_terms"]
                    }
                ),
                Tool(
                    name="extract_links",
                    description="Extract all links from a webpage with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to extract links from"
                            },
                            "filter_internal": {
                                "type": "boolean",
                                "description": "Only return internal links (same domain)",
                                "default": False
                            },
                            "filter_external": {
                                "type": "boolean", 
                                "description": "Only return external links (different domain)",
                                "default": False
                            },
                            "include_anchors": {
                                "type": "boolean",
                                "description": "Include anchor links (#fragments)",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="get_page_metadata",
                    description="Extract detailed metadata from a webpage (title, description, Open Graph, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "The URL to extract metadata from"
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
            """Handle tool calls"""
            try:
                if request.name == "fetch_webpage":
                    result = await self._fetch_webpage(request.arguments)
                elif request.name == "fetch_multiple_pages":
                    result = await self._fetch_multiple_pages(request.arguments)
                elif request.name == "search_webpage_content":
                    result = await self._search_webpage_content(request.arguments)
                elif request.name == "extract_links":
                    result = await self._extract_links(request.arguments)
                elif request.name == "get_page_metadata":
                    result = await self._get_page_metadata(request.arguments)
                else:
                    raise ValueError(f"Unknown tool: {request.name}")
                
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])
                
            except Exception as e:
                logger.error(f"Error in tool {request.name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=headers,
                connector=aiohttp.TCPConnector(limit=50, limit_per_host=10)
            )
        return self.session
    
    async def _fetch_webpage(self, args: dict) -> dict:
        """Fetch content from a single webpage"""
        url = args["url"]
        extract_content = args.get("extract_content", True)
        include_metadata = args.get("include_metadata", True)
        timeout = args.get("timeout", 30)
        
        session = await self._get_session()
        session._timeout = aiohttp.ClientTimeout(total=timeout)
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
                result = {
                    "url": url,
                    "status_code": response.status,
                    "content_type": response.headers.get("content-type", ""),
                    "content_length": len(html_content)
                }
                
                if include_metadata:
                    metadata = self._extract_metadata(html_content, url)
                    result["metadata"] = metadata
                
                if extract_content:
                    # Use trafilatura for intelligent content extraction
                    extracted = trafilatura.extract(html_content, include_links=True, include_images=True)
                    if extracted:
                        result["content"] = extracted
                    else:
                        # Fallback to BeautifulSoup
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.extract()
                        
                        # Get text content
                        text = soup.get_text()
                        
                        # Clean up text
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        result["content"] = '\n'.join(chunk for chunk in chunks if chunk)
                else:
                    result["raw_html"] = html_content
                
                return result
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }
    
    async def _fetch_multiple_pages(self, args: dict) -> dict:
        """Fetch content from multiple webpages in parallel"""
        urls = args["urls"]
        extract_content = args.get("extract_content", True)
        include_metadata = args.get("include_metadata", True)
        max_concurrent = args.get("max_concurrent", 5)
        timeout = args.get("timeout", 30)
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_single(url):
            async with semaphore:
                return await self._fetch_webpage({
                    "url": url,
                    "extract_content": extract_content,
                    "include_metadata": include_metadata,
                    "timeout": timeout
                })
        
        tasks = [fetch_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "total_urls": len(urls),
            "successful": len([r for r in results if isinstance(r, dict) and "error" not in r]),
            "failed": len([r for r in results if isinstance(r, dict) and "error" in r or isinstance(r, Exception)]),
            "results": [r if isinstance(r, dict) else {"error": str(r)} for r in results]
        }
    
    async def _search_webpage_content(self, args: dict) -> dict:
        """Search for specific content in a webpage"""
        url = args["url"]
        search_terms = args["search_terms"]
        case_sensitive = args.get("case_sensitive", False)
        context_chars = args.get("context_chars", 200)
        
        # First fetch the webpage
        webpage_result = await self._fetch_webpage({
            "url": url,
            "extract_content": True,
            "include_metadata": False
        })
        
        if "error" in webpage_result:
            return webpage_result
        
        content = webpage_result.get("content", "")
        if not case_sensitive:
            search_content = content.lower()
            search_terms = [term.lower() for term in search_terms]
        else:
            search_content = content
        
        matches = []
        for term in search_terms:
            start = 0
            while True:
                pos = search_content.find(term, start)
                if pos == -1:
                    break
                
                # Get context around the match
                context_start = max(0, pos - context_chars // 2)
                context_end = min(len(content), pos + len(term) + context_chars // 2)
                context = content[context_start:context_end]
                
                matches.append({
                    "term": term,
                    "position": pos,
                    "context": context,
                    "context_start": context_start,
                    "context_end": context_end
                })
                
                start = pos + 1
        
        return {
            "url": url,
            "search_terms": args["search_terms"],
            "total_matches": len(matches),
            "matches": matches,
            "content_length": len(content)
        }
    
    async def _extract_links(self, args: dict) -> dict:
        """Extract links from a webpage"""
        url = args["url"]
        filter_internal = args.get("filter_internal", False)
        filter_external = args.get("filter_external", False)
        include_anchors = args.get("include_anchors", False)
        
        # Fetch the webpage
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                base_domain = urlparse(url).netloc
                
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Skip anchor links if not requested
                    if href.startswith('#') and not include_anchors:
                        continue
                    
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    link_domain = urlparse(absolute_url).netloc
                    
                    is_internal = link_domain == base_domain
                    is_external = link_domain != base_domain and link_domain != ''
                    
                    # Apply filters
                    if filter_internal and not is_internal:
                        continue
                    if filter_external and not is_external:
                        continue
                    
                    link_info = {
                        "url": absolute_url,
                        "text": link.get_text(strip=True),
                        "title": link.get('title', ''),
                        "is_internal": is_internal,
                        "is_external": is_external
                    }
                    
                    links.append(link_info)
                
                return {
                    "source_url": url,
                    "total_links": len(links),
                    "internal_count": len([l for l in links if l["is_internal"]]),
                    "external_count": len([l for l in links if l["is_external"]]),
                    "links": links
                }
                
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return {
                "source_url": url,
                "error": str(e),
                "status": "failed"
            }
    
    async def _get_page_metadata(self, args: dict) -> dict:
        """Extract detailed metadata from a webpage"""
        url = args["url"]
        
        session = await self._get_session()
        
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                html_content = await response.text()
                
                metadata = self._extract_metadata(html_content, url)
                metadata["url"] = url
                metadata["status_code"] = response.status
                metadata["content_type"] = response.headers.get("content-type", "")
                metadata["content_length"] = len(html_content)
                
                return metadata
                
        except Exception as e:
            logger.error(f"Error getting metadata from {url}: {str(e)}")
            return {
                "url": url,
                "error": str(e),
                "status": "failed"
            }
    
    def _extract_metadata(self, html_content: str, url: str) -> dict:
        """Extract metadata from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        metadata = {}
        
        # Basic metadata
        title_tag = soup.find('title')
        metadata["title"] = title_tag.get_text(strip=True) if title_tag else ""
        
        # Meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            name = meta.get('name', '').lower()
            property_name = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata["description"] = content
            elif name == 'keywords':
                metadata["keywords"] = content
            elif name == 'author':
                metadata["author"] = content
            elif property_name == 'og:title':
                metadata["og_title"] = content
            elif property_name == 'og:description':
                metadata["og_description"] = content
            elif property_name == 'og:image':
                metadata["og_image"] = content
            elif property_name == 'og:url':
                metadata["og_url"] = content
            elif property_name == 'og:type':
                metadata["og_type"] = content
            elif name == 'twitter:card':
                metadata["twitter_card"] = content
            elif name == 'twitter:title':
                metadata["twitter_title"] = content
            elif name == 'twitter:description':
                metadata["twitter_description"] = content
            elif name == 'twitter:image':
                metadata["twitter_image"] = content
        
        # Canonical URL
        canonical = soup.find('link', rel='canonical')
        if canonical:
            metadata["canonical_url"] = canonical.get('href', '')
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            metadata["language"] = html_tag.get('lang', '')
        
        return metadata
    
    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="webfetch-mcp",
                    server_version="1.0.0",
                    capabilities={}
                )
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WebFetch MCP Server")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Set the logging level")
    args = parser.parse_args()
    
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    mcp_server = WebFetchMCP()
    
    try:
        await mcp_server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await mcp_server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
