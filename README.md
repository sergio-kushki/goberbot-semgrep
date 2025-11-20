# Goberbot-Semgrep MCP Server

A production-ready Model Context Protocol (MCP) server that integrates Semgrep static analysis with Cursor IDE and other MCP-compatible clients. Features custom security and code quality rules with Docker-based deployment.

## 🚀 Quick Start (New Machine Setup)

**Get up and running in 3 commands:**

```bash
# 1. Clone and navigate
git clone <repo-url> goberbot-semgrep && cd goberbot-semgrep

# 2. Start the server
./start-server.sh

# 3. Configure Cursor IDE (see SETUP.md)
```

📚 **Complete setup guide:** See [`SETUP.md`](./SETUP.md) for detailed instructions

## 📖 What's Included

- **Custom MCP Server** - FastMCP 2.13.1 with native streamable-http transport
- **Semgrep Integration** - Version 1.144.0 with full CLI support
- **Custom Rules** - 14 security and code quality rules
- **Docker Deployment** - One-command startup with `docker-compose`
- **Test Files** - Vulnerable code samples for validation

## Project Phases

### Phase 1: Local STDIO Setup ✅ **COMPLETE**
Set up and test Semgrep integrations locally.

**Results:**
- ✅ **Semgrep CLI** - Fully functional with custom rules
- ✅ **Custom Rules** - 17 vulnerabilities detected in test files
- ✅ **Remote MCP** - Working at `https://mcp.semgrep.ai/mcp`
- ❌ **Local MCP** - Deprecated package (no scanning tools)

**Key Finding:** Custom MCP server needed for production use (Phase 3)

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

## Phase 3: Custom MCP Server ✅ **COMPLETE** - **RECOMMENDED PATH**

**Why Custom?** After Phase 1 testing, we discovered:
- ❌ Local `semgrep-mcp` package is deprecated (no scanning tools)
- ⚠️ Remote server (`mcp.semgrep.ai`) works but has risks:
  - External dependency (could be shut down)
  - Privacy concerns (code sent to external server)
  - No customization possible
  - Can't use custom rules from `custom-rules/`

**Solution:** Built custom MCP server wrapping Semgrep CLI ✅

**Implemented Features:**
- ✅ FastMCP 2.0 with streamable HTTP
- ✅ Full control over functionality
- ✅ Local execution (privacy & security)
- ✅ Custom rule integration (`custom-rules/`)
- ✅ Hybrid rules loading (URL → Bundled → S3 ready)
- ✅ Docker native deployment
- ✅ EC2 deployment ready
- ✅ Health checks & monitoring
- ✅ Three MCP tools: scan_code, list_available_rules, reload_rules

**Quick Start:**
```bash
cd mcp-server
./quick-start.sh
```

**See:** 
- `mcp-server/README.md` for usage
- `EC2-DEPLOYMENT.md` for cloud deployment

---

## Project Structure

```
goberbot-semgrep/
├── README.md                    # This file
├── EC2-DEPLOYMENT.md            # AWS EC2 deployment guide
├── PHASE1-CHECKLIST.md          # Phase 1 testing results
├── PHASE3-ARCHITECTURE.md       # Phase 3 technical design
├── STRATEGIC-SUMMARY.md         # Strategic analysis
├── custom-rules/                # Custom Semgrep rules
│   ├── security.yaml            # Security vulnerability rules
│   └── code-quality.yaml        # Code quality rules
├── mcp-server/                  # Custom MCP Server (Phase 3) ✅
│   ├── server.py                # FastMCP 2.0 server
│   ├── semgrep_runner.py        # Semgrep CLI wrapper
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Container definition
│   ├── docker-compose.yml       # Local testing setup
│   ├── Makefile                 # Convenience commands
│   ├── quick-start.sh           # One-command startup
│   ├── test-server.sh           # Integration tests
│   └── README.md                # Server documentation
├── scripts/                     # Test and utility scripts
│   ├── test-local-scan-custom.sh
│   ├── test-local-scan-native.sh
│   └── test-local-scan-all.sh
└── tests/                       # Test files and results
    ├── sample-code/
    │   ├── vulnerable.js
    │   └── vulnerable.py
    └── results-*.json
```

## Resources

- [Semgrep MCP Documentation](https://semgrep.dev/docs/mcp)
- [Semgrep MCP GitHub](https://github.com/semgrep/mcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Semgrep Rules Registry](https://semgrep.dev/r)

## Next Steps

### Completed (Phase 1)
1. ✅ Install and test Semgrep CLI locally
2. ✅ Create custom security & code quality rules
3. ✅ Test with Cursor IDE (remote MCP server)
4. ✅ Validate custom rules (17 findings in test files)
5. ✅ Document learnings and limitations

### Completed (Phase 3) ✅
6. ✅ **Built Custom MCP Server** - DONE
   - FastMCP 2.0 implementation with HTTP transport
   - Semgrep CLI wrapper with hybrid rules loading
   - Dockerized for easy deployment
   - EC2 deployment guide created

### Next Steps (Production Ready)
7. **Deploy to EC2** (See `EC2-DEPLOYMENT.md`)
   - Launch EC2 instance
   - Deploy Docker container
   - Configure Cursor IDE

8. **Team Integration**
   - Share EC2 endpoint with team
   - Set up VPN or SSH tunnels for security
   - Consider multiple instances for availability

### Optional Enhancements
- Add authentication (JWT tokens)
- Implement S3 rules fetching
- Add caching for performance
- Git diff scanning integration
- Metrics dashboard

