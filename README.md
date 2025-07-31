# Orbital-MCP

A collection of Model Context Protocol (MCP) servers providing specialized capabilities for AI assistants and automation tools.

## Overview

This repository contains MCP servers designed to extend the capabilities of AI assistants like Claude, providing them with access to external data sources and services. Each server is containerized for easy deployment and integration.

## Available MCP Servers

### 🌐 WebFetch MCP Server

**Location**: `/WebFetch/`

A comprehensive web data fetching and content extraction server with advanced capabilities:

- **Smart Content Extraction**: Intelligent main content extraction using trafilatura
- **Metadata Extraction**: Complete metadata extraction (Open Graph, Twitter Cards, etc.)
- **Parallel Processing**: Concurrent fetching of multiple pages
- **Content Search**: Search for specific terms within web content
- **Link Analysis**: Extract and categorize internal/external links
- **Robust Error Handling**: Comprehensive error handling and logging

**Tools Available:**
- `fetch_webpage` - Extract content from a single webpage
- `fetch_multiple_pages` - Fetch content from multiple pages in parallel
- `search_webpage_content` - Search for specific content within pages
- `extract_links` - Extract and categorize links from pages
- `get_page_metadata` - Extract detailed page metadata

[📖 Full WebFetch Documentation](WebFetch/README.md)

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/Satcomx00-x00/Orbital-mcp.git
cd Orbital-mcp
```

2. **Build and run WebFetch MCP:**
```bash
cd WebFetch
docker-compose up --build
```

3. **Or build manually:**
```bash
docker build -t webfetch-mcp .
docker run -i webfetch-mcp
```

### Local Development

1. **Install dependencies:**
```bash
cd WebFetch
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python main.py --log-level INFO
```

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "webfetch": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "webfetch-mcp:latest"]
    }
  }
}
```

### Other MCP Clients

These servers follow the standard MCP protocol and can be integrated with any MCP-compatible client.

## Architecture

Each MCP server in this repository follows a consistent structure:

```
ServerName/
├── main.py              # Main server implementation
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker Compose setup
├── README.md           # Server-specific documentation
└── test_*.py           # Test scripts
```

## Development

### Adding a New MCP Server

1. Create a new directory for your server
2. Implement the MCP server following the existing patterns
3. Add proper containerization (Dockerfile, docker-compose.yml)
4. Include comprehensive documentation and tests
5. Update this main README

### Testing

Each server includes test scripts for validation:

```bash
cd WebFetch
python test_webfetch.py
```

## Security

- All containers run as non-root users
- Read-only filesystems where possible
- Resource limits and security options configured
- No unnecessary network exposure

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your MCP server following the established patterns
4. Add tests and documentation
5. Submit a pull request

## Future MCP Servers

Planned additions to this repository:

- **Database MCP**: Connect to various databases (MySQL, PostgreSQL, MongoDB)
- **API MCP**: Generic REST API client with authentication
- **File System MCP**: File operations and content analysis
- **Email MCP**: Email sending and IMAP/POP3 access
- **Social Media MCP**: Twitter, Reddit, and other social platform integration
- **Document MCP**: PDF, Word, and other document processing
- **Image MCP**: Image analysis and processing capabilities

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Each server has detailed documentation in its directory
- **Testing**: Use provided test scripts to validate functionality

## Related Projects

- [Model Context Protocol](https://github.com/modelcontextprotocol/python-sdk) - Official MCP Python SDK
- [Claude Desktop](https://claude.ai/desktop) - AI assistant with MCP support
- [Orbital-Bot](https://github.com/Satcomx00-x00/Orbital-Bot) - Discord bot utilizing these MCP servers
