# WebFetch MCP Server

A Model Context Protocol (MCP) server for intelligent web data fetching and content extraction. This server provides advanced capabilities for retrieving, parsing, and analyzing web content.

## Features

### 🌐 Web Content Fetching
- **Smart Content Extraction**: Uses trafilatura for intelligent main content extraction
- **Metadata Extraction**: Extracts titles, descriptions, Open Graph, Twitter Card data
- **Multiple Format Support**: Handles various content types and encodings
- **Parallel Processing**: Fetch multiple pages concurrently with configurable limits

### 🔍 Content Analysis
- **Search Functionality**: Search for specific terms within webpage content
- **Link Extraction**: Extract and categorize internal/external links
- **Content Filtering**: Filter results based on various criteria
- **Context Preservation**: Maintain context around search matches

### 🛡️ Robust & Reliable
- **Error Handling**: Comprehensive error handling and logging
- **Timeout Management**: Configurable request timeouts
- **Rate Limiting**: Built-in concurrency controls
- **Resource Management**: Proper HTTP session management

## Available Tools

### 1. `fetch_webpage`
Fetch and extract content from a single webpage with intelligent parsing.

**Parameters:**
- `url` (required): The URL to fetch
- `extract_content` (optional): Whether to extract main content (default: true)
- `include_metadata` (optional): Whether to include page metadata (default: true)  
- `timeout` (optional): Request timeout in seconds (default: 30)

**Example:**
```json
{
  "url": "https://example.com/article",
  "extract_content": true,
  "include_metadata": true,
  "timeout": 30
}
```

### 2. `fetch_multiple_pages`
Fetch content from multiple webpages in parallel with concurrency control.

**Parameters:**
- `urls` (required): Array of URLs to fetch
- `extract_content` (optional): Whether to extract main content (default: true)
- `include_metadata` (optional): Whether to include metadata (default: true)
- `max_concurrent` (optional): Maximum concurrent requests (default: 5)
- `timeout` (optional): Request timeout in seconds (default: 30)

**Example:**
```json
{
  "urls": ["https://site1.com", "https://site2.com", "https://site3.com"],
  "max_concurrent": 3,
  "extract_content": true
}
```

### 3. `search_webpage_content`
Fetch a webpage and search for specific content or patterns.

**Parameters:**
- `url` (required): The URL to fetch and search
- `search_terms` (required): Array of terms to search for
- `case_sensitive` (optional): Whether search is case sensitive (default: false)
- `context_chars` (optional): Characters to include around matches (default: 200)

**Example:**
```json
{
  "url": "https://example.com",
  "search_terms": ["API", "documentation", "tutorial"],
  "case_sensitive": false,
  "context_chars": 150
}
```

### 4. `extract_links`
Extract all links from a webpage with optional filtering.

**Parameters:**
- `url` (required): The URL to extract links from
- `filter_internal` (optional): Only return internal links (default: false)
- `filter_external` (optional): Only return external links (default: false)
- `include_anchors` (optional): Include anchor links (default: false)

**Example:**
```json
{
  "url": "https://example.com",
  "filter_external": true,
  "include_anchors": false
}
```

### 5. `get_page_metadata`
Extract detailed metadata from a webpage (title, description, Open Graph, etc.).

**Parameters:**
- `url` (required): The URL to extract metadata from

**Example:**
```json
{
  "url": "https://example.com"
}
```

## Installation & Usage

### Using Docker (Recommended)

1. **Build the container:**
```bash
docker build -t webfetch-mcp .
```

2. **Run the MCP server:**
```bash
docker run -i webfetch-mcp
```

### Local Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python main.py --log-level INFO
```

## Integration with MCP Clients

This server follows the Model Context Protocol standard and can be integrated with any MCP-compatible client. Common integration patterns:

### Claude Desktop
Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "webfetch": {
      "command": "docker",
      "args": ["run", "-i", "webfetch-mcp"]
    }
  }
}
```

### Python MCP Client
```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async with stdio_client(["python", "main.py"]) as client:
    result = await client.call_tool("fetch_webpage", {
        "url": "https://example.com"
    })
    print(result)
```

## Configuration

### Environment Variables
- `PYTHONUNBUFFERED=1`: Ensures output is not buffered
- `PYTHONPATH=/app`: Sets the Python path for imports

### Logging Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only

### Command Line Options
```bash
python main.py --log-level DEBUG
```

## Output Format

All tools return structured JSON data with consistent formatting:

```json
{
  "url": "https://example.com",
  "status_code": 200,
  "content_type": "text/html",
  "content_length": 12345,
  "metadata": {
    "title": "Page Title",
    "description": "Page description",
    "og_title": "Open Graph title",
    "keywords": "keyword1, keyword2"
  },
  "content": "Extracted main content..."
}
```

## Error Handling

The server provides comprehensive error handling:

- **Network Errors**: Connection timeouts, DNS failures
- **HTTP Errors**: 404, 500, etc. with detailed status information  
- **Parsing Errors**: Invalid HTML, encoding issues
- **Rate Limiting**: Automatic retry with backoff (future feature)

Error responses follow this format:
```json
{
  "url": "https://example.com",
  "error": "Connection timeout after 30 seconds",
  "status": "failed"
}
```

## Performance & Limits

- **Concurrent Requests**: Configurable (default: 5 for batch operations)
- **Request Timeout**: Configurable (default: 30 seconds)
- **Memory Usage**: Optimized with streaming and chunked processing
- **Connection Pooling**: Efficient HTTP connection reuse

## Security Considerations

- **User Agent**: Uses a standard browser user agent
- **SSL Verification**: Enabled by default
- **Resource Limits**: Built-in protections against large responses
- **Non-root Container**: Docker container runs as non-root user

## Dependencies

- **mcp**: Model Context Protocol implementation
- **aiohttp**: Asynchronous HTTP client
- **trafilatura**: Intelligent content extraction
- **beautifulsoup4**: HTML parsing and manipulation
- **lxml**: Fast XML/HTML processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the logs for detailed error information
- Ensure all dependencies are properly installed
