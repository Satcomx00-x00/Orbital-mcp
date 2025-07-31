#!/usr/bin/env python3
"""
HTTP REST API wrapper for WebFetch MCP Server
Allows agents to access MCP functionality via HTTP requests
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import argparse

# Import our MCP server
from main import WebFetchMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webfetch-http")

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class ToolCallResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class WebFetchHTTPServer:
    """HTTP wrapper for WebFetch MCP Server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="WebFetch MCP HTTP API",
            description="HTTP REST API for WebFetch MCP Server",
            version="1.0.0"
        )
        self.mcp_server = WebFetchMCP()
        self.setup_routes()
        self.setup_middleware()
    
    def setup_middleware(self):
        """Setup CORS and other middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def setup_routes(self):
        """Setup HTTP routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "service": "WebFetch MCP HTTP API",
                "version": "1.0.0",
                "status": "running"
            }
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}
        
        @self.app.get("/tools")
        async def list_tools():
            """List available tools"""
            try:
                # Get tools from MCP server
                tools = [
                    {
                        "name": "fetch_webpage",
                        "description": "Fetch and extract content from a webpage with smart content extraction",
                        "parameters": {
                            "url": {"type": "string", "required": True, "description": "The URL to fetch"},
                            "extract_content": {"type": "boolean", "default": True},
                            "include_metadata": {"type": "boolean", "default": True},
                            "timeout": {"type": "number", "default": 30}
                        }
                    },
                    {
                        "name": "fetch_multiple_pages",
                        "description": "Fetch content from multiple webpages in parallel",
                        "parameters": {
                            "urls": {"type": "array", "required": True, "description": "List of URLs to fetch"},
                            "extract_content": {"type": "boolean", "default": True},
                            "include_metadata": {"type": "boolean", "default": True},
                            "max_concurrent": {"type": "number", "default": 5},
                            "timeout": {"type": "number", "default": 30}
                        }
                    },
                    {
                        "name": "search_webpage_content",
                        "description": "Search for specific content in a webpage",
                        "parameters": {
                            "url": {"type": "string", "required": True},
                            "search_terms": {"type": "array", "required": True, "description": "Terms to search for"},
                            "case_sensitive": {"type": "boolean", "default": False},
                            "context_chars": {"type": "number", "default": 200}
                        }
                    },
                    {
                        "name": "extract_links",
                        "description": "Extract links from a webpage",
                        "parameters": {
                            "url": {"type": "string", "required": True},
                            "filter_internal": {"type": "boolean", "default": False},
                            "filter_external": {"type": "boolean", "default": False},
                            "include_anchors": {"type": "boolean", "default": False}
                        }
                    },
                    {
                        "name": "get_page_metadata",
                        "description": "Extract metadata from a webpage",
                        "parameters": {
                            "url": {"type": "string", "required": True}
                        }
                    }
                ]
                
                return {"tools": tools, "count": len(tools)}
                
            except Exception as e:
                logger.error(f"Error listing tools: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tools/{tool_name}")
        async def call_tool(tool_name: str, request: Dict[str, Any]):
            """Call a specific tool"""
            try:
                # Validate tool exists
                valid_tools = [
                    "fetch_webpage", "fetch_multiple_pages", "search_webpage_content",
                    "extract_links", "get_page_metadata"
                ]
                
                if tool_name not in valid_tools:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                # Call the appropriate MCP method
                if tool_name == "fetch_webpage":
                    result = await self.mcp_server._fetch_webpage(request)
                elif tool_name == "fetch_multiple_pages":
                    result = await self.mcp_server._fetch_multiple_pages(request)
                elif tool_name == "search_webpage_content":
                    result = await self.mcp_server._search_webpage_content(request)
                elif tool_name == "extract_links":
                    result = await self.mcp_server._extract_links(request)
                elif tool_name == "get_page_metadata":
                    result = await self.mcp_server._get_page_metadata(request)
                
                return {"success": True, "result": result}
                
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {str(e)}")
                return {"success": False, "error": str(e)}
        
        @self.app.post("/tools/call")
        async def call_tool_generic(request: ToolCallRequest):
            """Generic tool calling endpoint"""
            try:
                return await call_tool(request.tool_name, request.arguments)
            except Exception as e:
                logger.error(f"Error in generic tool call: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Convenience endpoints for each tool
        @self.app.post("/fetch")
        async def fetch_webpage_endpoint(request: Dict[str, Any]):
            """Convenience endpoint for fetching a single webpage"""
            return await call_tool("fetch_webpage", request)
        
        @self.app.post("/fetch-multiple")
        async def fetch_multiple_endpoint(request: Dict[str, Any]):
            """Convenience endpoint for fetching multiple webpages"""
            return await call_tool("fetch_multiple_pages", request)
        
        @self.app.post("/search")
        async def search_endpoint(request: Dict[str, Any]):
            """Convenience endpoint for searching webpage content"""
            return await call_tool("search_webpage_content", request)
        
        @self.app.post("/links")
        async def links_endpoint(request: Dict[str, Any]):
            """Convenience endpoint for extracting links"""
            return await call_tool("extract_links", request)
        
        @self.app.post("/metadata")
        async def metadata_endpoint(request: Dict[str, Any]):
            """Convenience endpoint for getting page metadata"""
            return await call_tool("get_page_metadata", request)
    
    async def startup(self):
        """Startup tasks"""
        logger.info(f"Starting WebFetch HTTP server on {self.host}:{self.port}")
        
    async def shutdown(self):
        """Cleanup tasks"""
        await self.mcp_server.cleanup()
        logger.info("WebFetch HTTP server shutdown complete")
    
    def run(self):
        """Run the HTTP server"""
        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="WebFetch MCP HTTP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="Set the logging level")
    args = parser.parse_args()
    
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    server = WebFetchHTTPServer(args.host, args.port)
    
    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Shutting down HTTP server...")

if __name__ == "__main__":
    main()
