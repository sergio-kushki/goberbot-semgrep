# Semgrep MCP POC

A proof-of-concept for using Semgrep's official MCP server with custom configurations and deployment options.

## Project Phases

### Phase 1: Local STDIO Setup ✅ (Current)
Set up and test the existing Semgrep MCP with stdio communication locally.

### Phase 2: Dockerization & Remote Deployment 🔄 (Next)
Containerize and deploy Semgrep MCP for remote access.

### Phase 3: Custom Wrapper 📋 (Future)
Build wrapper code to accommodate specific use cases.

---

## Phase 1: Local STDIO Setup

### Prerequisites
- Python 3.8+
- pipx (recommended) or pip
- Semgrep CLI (version 1.138.0+)

### Installation

1. **Install Semgrep CLI:**
```bash
# Using Homebrew (macOS/Linux)
brew install semgrep

# Or using pip
pip install semgrep

# Verify installation
semgrep --version
```

2. **Install Semgrep MCP:**
```bash
# Recommended: Using pipx for isolated environment
pipx install semgrep-mcp

# Alternative: Using pip
pip install semgrep-mcp
```

3. **Login to Semgrep (Optional - for Pro features):**
```bash
semgrep login
```

### Running the MCP Server (STDIO Mode)

**Default STDIO mode:**
```bash
semgrep-mcp
```

**Explicit STDIO specification:**
```bash
semgrep-mcp -t stdio
```

The server will:
- Read from **stdin** (standard input)
- Write to **stdout** (standard output)
- Log errors to **stderr** (standard error)

### Testing the MCP Server

#### Option 1: Using MCP Inspector (Recommended)
```bash
npx @modelcontextprotocol/inspector semgrep-mcp
```

#### Option 2: Manual Testing with curl
Create a test request file `test-request.json`:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

Send request:
```bash
cat test-request.json | semgrep-mcp
```

### MCP Configuration for Clients

#### For Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "semgrep-mcp",
      "args": []
    }
  }
}
```

#### For Cursor IDE
Add to Cursor MCP settings:
```json
{
  "mcpServers": {
    "semgrep": {
      "command": "semgrep-mcp",
      "args": []
    }
  }
}
```

### Custom Rules Setup

1. **Create a rules directory:**
```bash
mkdir -p custom-rules
```

2. **Add custom rules** (example: `custom-rules/security.yaml`):
```yaml
rules:
  - id: detect-eval-usage
    pattern: eval(...)
    message: "Dangerous use of eval() detected"
    languages: [javascript, typescript]
    severity: ERROR
    
  - id: hardcoded-secrets
    pattern: |
      password = "..."
    message: "Potential hardcoded password detected"
    languages: [python, javascript]
    severity: WARNING
```

3. **Test rules locally:**
```bash
semgrep --config custom-rules/ path/to/code
```

### Available MCP Tools

The Semgrep MCP server provides tools for:
- **Code scanning**: Analyze code snippets or files
- **Vulnerability detection**: Identify security issues
- **Custom rule enforcement**: Apply organization-specific rules
- **Multiple language support**: JavaScript, Python, Java, Go, and more

### Troubleshooting

**Issue: Command not found**
```bash
# Ensure pipx bin directory is in PATH
pipx ensurepath
```

**Issue: Semgrep version too old**
```bash
# Upgrade Semgrep
pip install --upgrade semgrep
```

**Issue: MCP server not responding**
```bash
# Check if server is running
ps aux | grep semgrep-mcp

# Check logs
semgrep-mcp 2> debug.log
```

---

## Phase 2: Docker & Remote Deployment (WIP)

### Docker Setup

**Pull official image:**
```bash
docker pull ghcr.io/semgrep/mcp
```

**Run with STDIO:**
```bash
docker run -i --rm ghcr.io/semgrep/mcp -t stdio
```

**Run with HTTP transport:**
```bash
docker run -p 8000:8000 --rm ghcr.io/semgrep/mcp -t streamable-http
```

### Deployment Options

#### Option A: Cloud Run / ECS / Similar
- Best for stateful container services
- Supports both HTTP and STDIO
- Easy scaling and management

#### Option B: Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly launch
```

#### Option C: Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway up
```

**Note**: Cloudflare Wrangler is designed for Workers (JS/WASM), not ideal for Python containers. Consider Cloudflare's container platform or alternatives.

---

## Phase 3: Custom Wrapper (Planned)

Future enhancements:
- Git commit range analysis
- Team-specific rule management
- Enhanced reporting and dashboards
- CI/CD pipeline integration
- Custom preprocessing logic

---

## Project Structure

```
goberbot-semgrep/
├── README.md                 # This file
├── custom-rules/            # Custom Semgrep rules
│   └── security.yaml
├── docker/                  # Docker configurations (Phase 2)
│   ├── Dockerfile
│   └── docker-compose.yml
├── tests/                   # Test files and scripts
│   ├── test-requests/
│   └── sample-code/
└── wrapper/                 # Custom wrapper code (Phase 3)
    └── (TBD)
```

## Resources

- [Semgrep MCP Documentation](https://semgrep.dev/docs/mcp)
- [Semgrep MCP GitHub](https://github.com/semgrep/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Semgrep Rules Registry](https://semgrep.dev/r)

## Next Steps

1. ✅ Install and test Semgrep MCP locally with STDIO
2. ⬜ Create custom rules for your use case
3. ⬜ Test with an MCP client (Claude, Cursor, etc.)
4. ⬜ Dockerize and deploy to remote server
5. ⬜ Build custom wrapper for specific workflows

