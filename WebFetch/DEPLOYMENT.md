# WebFetch MCP Server Deployment Guide

This guide shows you how to deploy the WebFetch MCP Server for internet access by your agents.

## Deployment Options

### Option 1: HTTP REST API (Recommended for Agents)

The HTTP REST API makes your MCP server accessible over the internet via standard HTTP requests.

#### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start HTTP server
python http_server.py --host 0.0.0.0 --port 8000
```

#### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose-http.yml up --build

# Or build manually
docker build -f Dockerfile.http -t webfetch-mcp-http .
docker run -p 8000:8000 webfetch-mcp-http
```

#### Production Deployment

##### Using Docker on VPS/Cloud Server
```bash
# On your server
git clone https://github.com/Satcomx00-x00/Orbital-mcp.git
cd Orbital-mcp/WebFetch

# Build and run
docker-compose -f docker-compose-http.yml up -d

# Check status
docker-compose -f docker-compose-http.yml ps
```

##### Using Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

##### SSL/HTTPS with Let's Encrypt
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

### Option 2: WebSocket Server

For real-time communication:

```python
# websocket_server.py (example)
import websockets
import json
import asyncio
from main import WebFetchMCP

async def handle_websocket(websocket, path):
    mcp_server = WebFetchMCP()
    
    async for message in websocket:
        try:
            data = json.loads(message)
            tool_name = data.get('tool')
            args = data.get('args', {})
            
            # Call appropriate MCP method
            if tool_name == 'fetch_webpage':
                result = await mcp_server._fetch_webpage(args)
            # ... other tools
            
            await websocket.send(json.dumps({'success': True, 'result': result}))
        except Exception as e:
            await websocket.send(json.dumps({'success': False, 'error': str(e)}))

# Start WebSocket server
start_server = websockets.serve(handle_websocket, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

### Option 3: Message Queue Integration

For scalable agent communication:

```python
# rabbitmq_server.py (example)
import pika
import json
import asyncio
from main import WebFetchMCP

def on_request(ch, method, props, body):
    try:
        data = json.loads(body)
        # Process MCP request
        # ... 
        
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(result)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Handle error
        pass

# Setup RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='webfetch_requests')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='webfetch_requests', on_message_callback=on_request)
channel.start_consuming()
```

## API Endpoints

### Base URL
- **Local**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

### Available Endpoints

#### Health Check
```http
GET /health
```

#### List Tools
```http
GET /tools
```

#### Fetch Webpage
```http
POST /fetch
Content-Type: application/json

{
    "url": "https://example.com",
    "extract_content": true,
    "include_metadata": true,
    "timeout": 30
}
```

#### Fetch Multiple Pages
```http
POST /fetch-multiple
Content-Type: application/json

{
    "urls": ["https://site1.com", "https://site2.com"],
    "extract_content": true,
    "max_concurrent": 5
}
```

#### Search Content
```http
POST /search
Content-Type: application/json

{
    "url": "https://example.com",
    "search_terms": ["API", "documentation"],
    "case_sensitive": false,
    "context_chars": 200
}
```

#### Extract Links
```http
POST /links
Content-Type: application/json

{
    "url": "https://example.com",
    "filter_external": true,
    "include_anchors": false
}
```

#### Get Metadata
```http
POST /metadata
Content-Type: application/json

{
    "url": "https://example.com"
}
```

#### Generic Tool Call
```http
POST /tools/call
Content-Type: application/json

{
    "tool_name": "fetch_webpage",
    "arguments": {
        "url": "https://example.com"
    }
}
```

## Agent Integration Examples

### Discord Bot Integration

```python
# In your Discord bot
import aiohttp

class WebFetchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.webfetch_url = "https://your-webfetch-server.com"
    
    @commands.command()
    async def fetch(self, ctx, url: str):
        async with aiohttp.ClientSession() as session:
            data = {"url": url, "extract_content": True}
            async with session.post(f"{self.webfetch_url}/fetch", json=data) as response:
                result = await response.json()
                
                if result['success']:
                    content = result['result']['content'][:2000]  # Discord limit
                    await ctx.send(f"```{content}```")
                else:
                    await ctx.send(f"Error: {result['error']}")
```

### Orbital-Bot Integration

Add to your Discord-Support-AI bot:

```python
# cogs/WebFetch/webfetch_cog.py
import aiohttp
import discord
from discord.ext import commands

class WebFetchCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_base = "https://your-webfetch-server.com"
    
    async def fetch_webpage_data(self, url: str):
        """Fetch webpage data via HTTP API"""
        async with aiohttp.ClientSession() as session:
            data = {"url": url, "extract_content": True, "include_metadata": True}
            async with session.post(f"{self.api_base}/fetch", json=data) as response:
                return await response.json()
    
    @commands.slash_command(description="Fetch content from a webpage")
    async def webfetch(self, ctx, url: str):
        await ctx.defer()
        
        result = await self.fetch_webpage_data(url)
        
        if result['success']:
            data = result['result']
            
            embed = discord.Embed(
                title=data.get('metadata', {}).get('title', 'Web Content'),
                url=url,
                color=0x00ff00
            )
            
            content = data.get('content', '')
            if len(content) > 4000:
                content = content[:4000] + "..."
            
            embed.description = content
            embed.add_field(name="Status", value=data.get('status_code'))
            embed.add_field(name="Content Length", value=f"{data.get('content_length'):,} chars")
            
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send(f"❌ Error: {result['error']}")

def setup(bot):
    bot.add_cog(WebFetchCog(bot))
```

## Security Considerations

### Authentication
Add API key authentication:

```python
# In http_server.py
from fastapi import HTTPException, Depends, Header

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != "your-secret-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Add to endpoints
@app.post("/fetch", dependencies=[Depends(verify_api_key)])
async def fetch_endpoint(request: Dict[str, Any]):
    # ...
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
    # ...
```

### HTTPS Only
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

## Monitoring & Logging

### Health Checks
The server includes built-in health checks at `/health`

### Logging
```python
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webfetch.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics (Prometheus)
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('webfetch_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('webfetch_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Cloud Deployment Options

### AWS
- **ECS/Fargate**: Container deployment
- **Lambda**: Serverless (with API Gateway)
- **EC2**: Traditional VPS

### Google Cloud
- **Cloud Run**: Serverless containers
- **GKE**: Kubernetes deployment
- **Compute Engine**: VPS

### Digital Ocean
- **App Platform**: Simple container deployment
- **Droplets**: VPS deployment

### Heroku
```bash
# Create Procfile
echo "web: python http_server.py --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git init
git add .
git commit -m "Initial commit"
heroku create your-webfetch-app
git push heroku main
```

## Testing Deployment

```bash
# Test health endpoint
curl https://your-domain.com/health

# Test tool listing
curl https://your-domain.com/tools

# Test webpage fetch
curl -X POST https://your-domain.com/fetch \
     -H "Content-Type: application/json" \
     -d '{"url": "https://httpbin.org/html"}'

# Load test
ab -n 100 -c 10 https://your-domain.com/health
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if server is running
   - Verify port binding
   - Check firewall rules

2. **CORS Issues**
   - Update CORS configuration in `http_server.py`
   - Add allowed origins

3. **Memory Issues**
   - Increase Docker memory limits
   - Optimize concurrent request limits

4. **SSL Certificate Issues**
   - Verify certificate installation
   - Check domain DNS configuration

### Debug Mode
```bash
python http_server.py --log-level DEBUG
```

### Container Logs
```bash
docker-compose -f docker-compose-http.yml logs -f
```

This deployment guide provides multiple options for making your WebFetch MCP server accessible to your agents over the internet. Choose the option that best fits your infrastructure and requirements.
