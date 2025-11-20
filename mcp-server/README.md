# Custom Semgrep MCP Server

A production-ready MCP 2.0 server that wraps Semgrep CLI for AI-powered code scanning in Cursor IDE and other MCP clients.

## Features

✅ **FastMCP 2.0** - Modern MCP implementation with streamable HTTP  
✅ **Hybrid Rules Loading** - URL → Bundled → S3 (future)  
✅ **Docker Native** - No venv needed, optimized image  
✅ **Production Ready** - Health checks, logging, error handling  
✅ **Custom Rules** - Uses your custom security & quality rules  

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server locally
python server.py

# Server will start on http://0.0.0.0:8000
```

### Docker (Recommended)

```bash
# Build and run with docker-compose
cd mcp-server
docker-compose up --build

# Or build and run manually
docker build -t semgrep-mcp-server -f Dockerfile ..
docker run -p 8000:8000 semgrep-mcp-server
```

### Test the Server

```bash
# Check health
curl http://localhost:8000/health

# List available tools (MCP)
curl http://localhost:8000/mcp/list_tools

# Scan code
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "scan_code",
    "args": {
      "code": "eval(userInput);",
      "language": "javascript"
    }
  }'
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_HOST` | `0.0.0.0` | Server host binding |
| `MCP_PORT` | `8000` | Server port |
| `CUSTOM_RULES_URL` | `""` | URL to fetch rules from (optional) |

### Rules Loading Priority

1. **URL** (if `CUSTOM_RULES_URL` is set)
2. **Bundled** (rules copied into Docker image)
3. **Mounted Volume** (if using docker-compose with volumes)

### Example: Using External Rules

```bash
# Start with remote rules
docker run -p 8000:8000 \
  -e CUSTOM_RULES_URL="https://raw.githubusercontent.com/yourorg/rules/main/security.yaml" \
  semgrep-mcp-server
```

### Example: Using Local Rules Volume

```bash
# Mount local rules directory
docker run -p 8000:8000 \
  -v ./custom-rules:/app/custom-rules:ro \
  semgrep-mcp-server
```

## Available Tools

### 1. `scan_code`

Scan code for vulnerabilities and code quality issues.

**Input:**
```json
{
  "code": "eval(userInput);",
  "language": "javascript",
  "rules_file": "security.yaml"
}
```

**Output:**
```json
{
  "findings": [
    {
      "rule_id": "eval-usage",
      "severity": "ERROR",
      "message": "Dangerous eval() usage detected",
      "line": 1,
      "cwe": "CWE-95"
    }
  ],
  "scan_time_ms": 142,
  "rules_used": "/app/custom-rules/security.yaml",
  "summary": {
    "ERROR": 1,
    "WARNING": 0,
    "INFO": 0,
    "total": 1
  }
}
```

### 2. `list_available_rules`

List all available Semgrep rules and their metadata.

**Output:**
```json
{
  "success": true,
  "rules": [
    {
      "file": "security.yaml",
      "path": "/app/custom-rules/security.yaml",
      "source": "bundled"
    }
  ]
}
```

### 3. `reload_rules`

Reload rules from the configured source (useful after rules update).

**Output:**
```json
{
  "success": true,
  "message": "Rules reloaded successfully",
  "rules_source": "url:https://..."
}
```

## Integration with Cursor IDE

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://localhost:8000"
    }
  }
}
```

**For EC2 deployment:**
```json
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://your-ec2-ip:8000"
    }
  }
}
```

## EC2 Deployment

### 1. Launch EC2 Instance

```bash
# Recommended: t3.small or t3.medium
# OS: Amazon Linux 2023 or Ubuntu 22.04
# Security Group: Allow port 8000 from your IP
```

### 2. Install Docker

```bash
# Amazon Linux 2023
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu
```

### 3. Deploy Container

```bash
# Copy project files to EC2
scp -i your-key.pem -r mcp-server/ ec2-user@your-ec2-ip:/home/ec2-user/

# SSH into EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Build and run
cd mcp-server
docker-compose up -d

# Check logs
docker-compose logs -f
```

### 4. Configure Security Group

```
Inbound Rules:
- Port 8000: Your IP address (or VPN CIDR)
- Port 22: Your IP address (SSH)
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Container Logs

```bash
# Docker compose
docker-compose logs -f

# Docker run
docker logs -f semgrep-mcp-server
```

### Metrics

The server logs include:
- Scan duration
- Finding counts
- Error rates
- Rules source status

## Troubleshooting

### Issue: Rules not found

```bash
# Check rules are bundled
docker exec semgrep-mcp-server ls -la /app/custom-rules/

# Check rules source
docker logs semgrep-mcp-server | grep "Rules source"
```

### Issue: Connection refused

```bash
# Check container is running
docker ps | grep semgrep

# Check port binding
docker port semgrep-mcp-server

# Test locally on EC2
curl http://localhost:8000/health
```

### Issue: Slow scans

```bash
# Check Semgrep version
docker exec semgrep-mcp-server semgrep --version

# Check container resources
docker stats semgrep-mcp-server
```

## Development

### Project Structure

```
mcp-server/
├── server.py              # FastMCP server implementation
├── semgrep_runner.py      # Semgrep CLI wrapper
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Local testing setup
├── .dockerignore         # Docker build exclusions
└── README.md             # This file
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements.txt pytest pytest-asyncio

# Run tests (when implemented)
pytest tests/
```

## Roadmap

- [ ] Add authentication (JWT tokens)
- [ ] Implement S3 rules fetching
- [ ] Add caching for repeated scans
- [ ] Git diff scanning integration
- [ ] Metrics dashboard endpoint
- [ ] Rate limiting
- [ ] WebSocket support for streaming results

## License

[Your License Here]

