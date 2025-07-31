# Agent Access Guide for WebFetch MCP Server

## 🌐 Making Your MCP Server Internet-Accessible

Your WebFetch MCP server is now ready to be accessed by agents over the internet! Here are the different ways your agents can connect:

## 🚀 Quick Start for Agents

### Option 1: HTTP REST API (Recommended)

**Start the HTTP server:**
```bash
cd /workspace/Orbital-mcp/WebFetch
python http_server.py --host 0.0.0.0 --port 8000
```

**Or with Docker:**
```bash
docker-compose -f docker-compose-http.yml up -d
```

**Access via HTTP endpoints:**
- **Health Check**: `GET http://your-server:8000/health`
- **List Tools**: `GET http://your-server:8000/tools`
- **Fetch Webpage**: `POST http://your-server:8000/fetch`
- **API Documentation**: `http://your-server:8000/docs` (Auto-generated)

## 🤖 Agent Integration Examples

### Python Agents (Discord Bots, AI Agents, etc.)

```python
import aiohttp
import asyncio

async def fetch_webpage_content(url: str, server_url="http://localhost:8000"):
    """Fetch webpage content for your agent"""
    async with aiohttp.ClientSession() as session:
        data = {
            "url": url,
            "extract_content": True,
            "include_metadata": True
        }
        
        async with session.post(f"{server_url}/fetch", json=data) as response:
            result = await response.json()
            
            if result['success']:
                return {
                    'content': result['result']['content'],
                    'title': result['result']['metadata']['title'],
                    'status': result['result']['status_code']
                }
            else:
                print(f"Error: {result['error']}")
                return None

# Example usage in your Discord bot
async def web_command(ctx, url: str):
    content = await fetch_webpage_content(url)
    if content:
        await ctx.send(f"**{content['title']}**\n{content['content'][:2000]}...")
```

### JavaScript/Node.js Agents

```javascript
const axios = require('axios');

class WebFetchClient {
    constructor(serverUrl = 'http://localhost:8000') {
        this.serverUrl = serverUrl;
    }
    
    async fetchWebpage(url) {
        try {
            const response = await axios.post(`${this.serverUrl}/fetch`, {
                url: url,
                extract_content: true,
                include_metadata: true
            });
            
            return response.data.success ? response.data.result : null;
        } catch (error) {
            console.error('WebFetch error:', error.message);
            return null;
        }
    }
    
    async searchContent(url, searchTerms) {
        try {
            const response = await axios.post(`${this.serverUrl}/search`, {
                url: url,
                search_terms: searchTerms,
                case_sensitive: false
            });
            
            return response.data.success ? response.data.result : null;
        } catch (error) {
            console.error('Search error:', error.message);
            return null;
        }
    }
}

// Usage
const webFetch = new WebFetchClient('http://your-server:8000');
const content = await webFetch.fetchWebpage('https://example.com');
```

### Go Agents

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
)

type WebFetchClient struct {
    BaseURL string
}

type FetchRequest struct {
    URL            string `json:"url"`
    ExtractContent bool   `json:"extract_content"`
    IncludeMetadata bool  `json:"include_metadata"`
}

type WebFetchResponse struct {
    Success bool        `json:"success"`
    Result  interface{} `json:"result,omitempty"`
    Error   string      `json:"error,omitempty"`
}

func (c *WebFetchClient) FetchWebpage(url string) (*WebFetchResponse, error) {
    request := FetchRequest{
        URL:            url,
        ExtractContent: true,
        IncludeMetadata: true,
    }
    
    jsonData, _ := json.Marshal(request)
    resp, err := http.Post(c.BaseURL+"/fetch", "application/json", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    var result WebFetchResponse
    json.NewDecoder(resp.Body).Decode(&result)
    return &result, nil
}

// Usage
func main() {
    client := &WebFetchClient{BaseURL: "http://your-server:8000"}
    result, err := client.FetchWebpage("https://example.com")
    if err == nil && result.Success {
        fmt.Println("Content fetched successfully!")
    }
}
```

### Rust Agents

```rust
use reqwest::Client;
use serde_json::{json, Value};
use std::error::Error;

pub struct WebFetchClient {
    client: Client,
    base_url: String,
}

impl WebFetchClient {
    pub fn new(base_url: String) -> Self {
        Self {
            client: Client::new(),
            base_url,
        }
    }
    
    pub async fn fetch_webpage(&self, url: &str) -> Result<Value, Box<dyn Error>> {
        let response = self
            .client
            .post(&format!("{}/fetch", self.base_url))
            .json(&json!({
                "url": url,
                "extract_content": true,
                "include_metadata": true
            }))
            .send()
            .await?;
        
        let result: Value = response.json().await?;
        Ok(result)
    }
    
    pub async fn search_content(&self, url: &str, terms: Vec<&str>) -> Result<Value, Box<dyn Error>> {
        let response = self
            .client
            .post(&format!("{}/search", self.base_url))
            .json(&json!({
                "url": url,
                "search_terms": terms,
                "case_sensitive": false
            }))
            .send()
            .await?;
        
        let result: Value = response.json().await?;
        Ok(result)
    }
}

// Usage
#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let client = WebFetchClient::new("http://your-server:8000".to_string());
    let result = client.fetch_webpage("https://example.com").await?;
    println!("Result: {}", result);
    Ok(())
}
```

## 🌍 Deployment Options

### Local Development
```bash
# Start HTTP server locally
python http_server.py --host 0.0.0.0 --port 8000
```

### Cloud Deployment

#### Docker on VPS
```bash
# On your server
git clone https://github.com/Satcomx00-x00/Orbital-mcp.git
cd Orbital-mcp/WebFetch
docker-compose -f docker-compose-http.yml up -d
```

#### Heroku
```bash
echo "web: python http_server.py --host 0.0.0.0 --port \$PORT" > Procfile
git init
git add .
git commit -m "Initial commit"
heroku create your-webfetch-app
git push heroku main
```

#### AWS ECS/Fargate
```yaml
# ecs-task-definition.json
{
  "family": "webfetch-mcp",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "webfetch",
      "image": "your-account.dkr.ecr.region.amazonaws.com/webfetch-mcp:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "essential": true
    }
  ]
}
```

## 🔒 Security for Production

### API Key Authentication
```python
# Add to your http_server.py
from fastapi import HTTPException, Depends, Header

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != "your-secret-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Use on endpoints
@app.post("/fetch", dependencies=[Depends(verify_api_key)])
async def fetch_endpoint(request: Dict[str, Any]):
    # Your endpoint logic
```

### Rate Limiting
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/fetch")
@limiter.limit("10/minute")
async def fetch_endpoint(request: Request, data: Dict[str, Any]):
    # Your endpoint logic
```

## 📊 Available Tools & Endpoints

| Tool | Endpoint | Description |
|------|----------|-------------|
| `fetch_webpage` | `POST /fetch` | Fetch and extract content from a single webpage |
| `fetch_multiple_pages` | `POST /fetch-multiple` | Fetch content from multiple pages in parallel |
| `search_webpage_content` | `POST /search` | Search for specific terms within webpage content |
| `extract_links` | `POST /links` | Extract and categorize links from a webpage |
| `get_page_metadata` | `POST /metadata` | Extract detailed metadata from a webpage |

### Example API Calls

**Fetch a webpage:**
```bash
curl -X POST "http://your-server:8000/fetch" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "extract_content": true,
       "include_metadata": true
     }'
```

**Search webpage content:**
```bash
curl -X POST "http://your-server:8000/search" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "search_terms": ["API", "documentation"],
       "case_sensitive": false
     }'
```

**Extract links:**
```bash
curl -X POST "http://your-server:8000/links" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com",
       "filter_external": true
     }'
```

## 🚀 Integration with Orbital-Bot

Add to your Discord-Support-AI bot:

```python
# cogs/WebFetch/webfetch_cog.py
import aiohttp
import discord
from discord.ext import commands

class WebFetchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webfetch_api = "http://your-webfetch-server:8000"
    
    @discord.slash_command(description="Fetch content from a webpage")
    async def webfetch(self, ctx, url: str):
        await ctx.defer()
        
        async with aiohttp.ClientSession() as session:
            data = {"url": url, "extract_content": True, "include_metadata": True}
            async with session.post(f"{self.webfetch_api}/fetch", json=data) as response:
                result = await response.json()
        
        if result['success']:
            data = result['result']
            embed = discord.Embed(
                title=data.get('metadata', {}).get('title', 'Web Content'),
                url=url,
                color=0x00ff00
            )
            
            content = data.get('content', '')[:4000]  # Discord limit
            embed.description = content
            embed.add_field(name="Status", value=data.get('status_code'))
            
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"❌ Error: {result['error']}")

def setup(bot):
    bot.add_cog(WebFetchCog(bot))
```

## 🔍 Testing Your Deployment

```bash
# Health check
curl http://your-server:8000/health

# List available tools
curl http://your-server:8000/tools

# Test webpage fetch
curl -X POST http://your-server:8000/fetch \
     -H "Content-Type: application/json" \
     -d '{"url": "https://httpbin.org/html"}'

# Load test
ab -n 100 -c 10 http://your-server:8000/health
```

## 📈 Monitoring

- **Health Endpoint**: `GET /health` - Use for health checks
- **Metrics**: Integrate with Prometheus/Grafana
- **Logs**: Check server logs for errors and performance
- **Alerts**: Set up alerts for downtime or errors

## 🎯 Next Steps

1. **Deploy the HTTP server** to your preferred cloud platform
2. **Configure your agents** to use the HTTP endpoints
3. **Add authentication** and rate limiting for production
4. **Monitor performance** and scale as needed
5. **Integrate with your existing bot/agent infrastructure**

Your WebFetch MCP server is now ready to serve your agents over the internet! 🚀
