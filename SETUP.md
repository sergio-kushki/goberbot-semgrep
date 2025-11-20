# Goberbot-Semgrep MCP Server Setup Guide

Complete setup instructions for deploying the Goberbot-Semgrep MCP server from scratch on a new machine.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Cursor IDE Configuration](#cursor-ide-configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Architecture Overview](#architecture-overview)

---

## 🔧 Prerequisites

### Required Software

1. **Docker & Docker Compose**
   - macOS/Linux: Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Verify installation:
     ```bash
     docker --version
     docker-compose --version
     ```

2. **Cursor IDE**
   - Download from [cursor.sh](https://cursor.sh)
   - Version: Latest (with MCP support)

3. **Git** (to clone the repository)
   ```bash
   git --version
   ```

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 2GB free space
- **OS**: macOS, Linux, or Windows with WSL2

---

## 🚀 Quick Start

For the impatient - get up and running in 2 commands:

```bash
# 1. Clone the repository
git clone <your-repo-url> goberbot-semgrep
cd goberbot-semgrep

# 2. Start the MCP server (automatically builds on first run)
./start-server.sh

# 3. Configure Cursor (see Cursor IDE Configuration section)
```

**What happens on first run:**
- Detects this is a fresh machine
- Automatically builds the Docker image (2-5 minutes)
- Installs all dependencies (Python, Semgrep, FastMCP, etc.)
- Starts the server
- No manual installation needed!

The server will be running at `http://localhost:8000/mcp`

---

## 📖 Detailed Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url> goberbot-semgrep
cd goberbot-semgrep

# Verify project structure
ls -la
# You should see: custom-rules/, mcp-server/, tests/, README.md, etc.
```

### Step 2: Review Custom Semgrep Rules

The project includes custom security and code quality rules:

```bash
# View available rules
ls -la custom-rules/
# security.yaml       - Security vulnerability detection
# code-quality.yaml   - Code quality and best practices
```

**Optional:** Edit or add your own rules in `custom-rules/`. Rules are automatically loaded by the server.

### Step 3: Build and Start the MCP Server

```bash
# Navigate to the MCP server directory
cd mcp-server

# Build the Docker image (first time only, or after changes)
docker-compose build

# Start the server in detached mode
docker-compose up -d

# Verify the server is running
docker ps
# You should see: goberbot-semgrep-mcp-server

# Check server logs
docker logs goberbot-semgrep-mcp-server --tail 50
```

**Expected output:**
```
╭──────────────────────────────────────────────────────────────────────────────╮
│                                FastMCP 2.13.1                                │
│                 Server name: goberbot-semgrep-mcp-server                     │
│                 Transport:   HTTP                                            │
│                 Server URL:  http://0.0.0.0:8000/mcp                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### Step 4: Verify Server Health

```bash
# Test the server endpoint
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test-client", "version": "1.0"}
    }
  }'
```

**Expected:** You should see a JSON response with server capabilities.

### Step 5: Verify Semgrep Installation

```bash
# Check Semgrep version inside the container
docker exec goberbot-semgrep-mcp-server semgrep --version
# Expected: 1.144.0 (or similar)
```

---

## 🖥️ Cursor IDE Configuration

### Configure MCP Server in Cursor

1. **Open Cursor Settings**
   - macOS: `Cmd + Shift + J` or `Cursor > Settings`
   - Windows/Linux: `Ctrl + Shift + J`

2. **Edit MCP Configuration File**
   
   The MCP config file location depends on your OS:
   - **macOS**: `~/.cursor/mcp.json`
   - **Linux**: `~/.cursor/mcp.json`
   - **Windows**: `%APPDATA%\.cursor\mcp.json`

3. **Add Goberbot Server Configuration**

   ```bash
   # macOS/Linux - edit the config file
   nano ~/.cursor/mcp.json
   ```

   Add this configuration:

   ```json
   {
     "mcpServers": {
       "semgrep_custom_local": {
         "type": "streamable-http",
         "url": "http://localhost:8000/mcp"
       }
     }
   }
   ```

   **⚠️ Important:** 
   - Make sure the URL includes `/mcp` at the end
   - Use `http://localhost:8000/mcp` (not `http://localhost:8000`)

4. **Restart Cursor IDE**
   
   Completely quit and restart Cursor for changes to take effect.

5. **Verify Connection**

   Open Cursor's MCP panel or check the MCP logs:
   - Look for: `MCP user-semgrep_custom_local` 
   - Should show: "Connected" status (not 404 errors)

---

## 🧪 Testing

### Test the Server from Command Line

```bash
# Run the built-in test script
cd mcp-server
./test-server.sh
```

### Test from Cursor IDE

Open Cursor and try these commands in the chat:

1. **List available rules:**
   ```
   What Semgrep rules are available in the Goberbot MCP server?
   ```

2. **Scan test files:**
   ```
   Use Goberbot Semgrep to scan tests/sample-code/vulnerable.js
   ```

3. **Expected results:**
   - JavaScript: ~10 issues (eval usage, XSS, console.log, etc.)
   - Python: ~7 issues (MD5 usage, print statements, etc.)

### Test with Sample Files

The repository includes vulnerable test files:

```bash
# View test files
cat tests/sample-code/vulnerable.js
cat tests/sample-code/vulnerable.py
```

These files intentionally contain security issues and code quality problems for testing.

---

## 🛠️ Troubleshooting

### Server Won't Start

**Problem:** Docker container fails to start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# If something is using port 8000, kill it or change the port in docker-compose.yml
```

**Problem:** Build fails with dependency errors

```bash
# Clean rebuild
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### Cursor Can't Connect (404 Errors)

**Problem:** Getting "404 Not Found" or "No server info found"

**Solution:** Check your `mcp.json` URL:

```json
// ❌ WRONG - missing /mcp path
"url": "http://localhost:8000"

// ✅ CORRECT - includes /mcp path
"url": "http://localhost:8000/mcp"
```

**Problem:** Getting "Bad Request: No valid session ID provided"

**Solution:** This usually resolves after restarting Cursor completely (quit and reopen).

### Semgrep Not Finding Issues

**Problem:** Scans return no results or fewer results than expected

```bash
# Check if rules are loaded
docker exec goberbot-semgrep-mcp-server ls -la /app/custom-rules/

# Check server logs for rule loading errors
docker logs goberbot-semgrep-mcp-server | grep -i error

# Verify Semgrep is working
docker exec goberbot-semgrep-mcp-server semgrep --version
```

### View Logs

```bash
# View all logs
docker logs goberbot-semgrep-mcp-server

# Follow logs in real-time
docker logs -f goberbot-semgrep-mcp-server

# View last 50 lines
docker logs goberbot-semgrep-mcp-server --tail 50
```

### Restart the Server

```bash
# Simple restart (keeps existing image)
./start-server.sh

# Or using docker-compose directly
cd mcp-server
docker-compose restart
```

### Rebuild After Changes

If you've modified rules, Dockerfile, or requirements:

```bash
# Force a complete rebuild
./start-server.sh --rebuild

# Or manually
cd mcp-server
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**When to rebuild:**
- After adding/modifying custom rules in `custom-rules/`
- After updating `requirements.txt`
- After changing `Dockerfile`
- When dependencies need updating

### Reset Everything

```bash
# Complete reset - stops containers, removes images
cd mcp-server
docker-compose down
docker rmi mcp-server-goberbot-semgrep-mcp:latest
docker-compose build --no-cache
docker-compose up -d
```

---

## 📦 Architecture Overview

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Cursor IDE (Client)                     │
│                    MCP Protocol Client                       │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP (streamable-http)
                       │ http://localhost:8000/mcp
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Goberbot-Semgrep MCP Server                     │
│                   (Docker Container)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FastMCP 2.13.1 (Native streamable-http transport)    │ │
│  │  - server.py (MCP tools handler)                      │ │
│  │  - semgrep_runner.py (Semgrep wrapper)                │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Semgrep CLI 1.144.0                                   │ │
│  │  (Installed as system binary)                          │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Custom Rules                                          │ │
│  │  - /app/custom-rules/security.yaml                     │ │
│  │  - /app/custom-rules/code-quality.yaml                 │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### MCP Tools Exposed

1. **`scan_code`** - Scan code snippets for security and quality issues
   - Parameters: `code`, `language`, `rules_file`
   - Returns: List of findings with severity, line numbers, CWE info

2. **`list_available_rules`** - List all loaded Semgrep rules
   - Returns: Available rule files and their sources

3. **`reload_rules`** - Reload rules from disk or URL
   - Useful for updating rules without restarting the server

### Technology Stack

- **MCP Protocol**: Model Context Protocol for AI-IDE integration
- **FastMCP**: Native Python MCP server framework (v2.13.1)
- **Semgrep**: Static analysis tool (v1.144.0)
- **Docker**: Containerization for consistent deployment
- **Python**: 3.11-slim base image

### File Structure

```
goberbot-semgrep/
├── custom-rules/              # Custom Semgrep rules
│   ├── security.yaml          # Security vulnerability rules
│   └── code-quality.yaml      # Code quality rules
├── mcp-server/                # MCP server implementation
│   ├── Dockerfile             # Docker image definition
│   ├── docker-compose.yml     # Docker Compose configuration
│   ├── server.py              # Main MCP server with FastMCP
│   ├── semgrep_runner.py      # Semgrep CLI wrapper
│   ├── requirements.txt       # Python dependencies
│   └── test-server.sh         # Testing script
├── tests/                     # Test files and results
│   └── sample-code/           # Vulnerable code samples
│       ├── vulnerable.js      # JavaScript test file
│       └── vulnerable.py      # Python test file
├── SETUP.md                   # This file
└── README.md                  # Project overview
```

---

## 🔄 Updating Rules

### Add or Modify Rules

1. Edit rule files:
   ```bash
   nano custom-rules/security.yaml
   nano custom-rules/code-quality.yaml
   ```

2. Restart the server to load new rules:
   ```bash
   cd mcp-server
   docker-compose restart
   ```

### Rule File Format

Rules use standard Semgrep YAML format:

```yaml
rules:
  - id: rule-name
    pattern: |
      code_pattern(...)
    message: "Description of the issue"
    languages: [javascript, python]
    severity: ERROR  # ERROR, WARNING, or INFO
    metadata:
      category: security
      cwe: "CWE-XXX: Description"
```

See [Semgrep documentation](https://semgrep.dev/docs/writing-rules/overview/) for more details.

---

## 🚀 Production Deployment

### Deploy to Remote Server

See `EC2-DEPLOYMENT.md` for AWS deployment instructions.

Quick steps:

1. Copy the project to your server
2. Install Docker and Docker Compose
3. Update `docker-compose.yml` to bind to public interface (optional)
4. Set up firewall rules (allow port 8000)
5. Use a reverse proxy (nginx) with SSL for production

### Environment Variables

Configure via `docker-compose.yml`:

```yaml
environment:
  - MCP_HOST=0.0.0.0
  - MCP_PORT=8000
  - CUSTOM_RULES_URL=https://your-domain.com/rules/  # Optional: Load rules from URL
```

---

## 📚 Additional Resources

- **MCP Protocol**: [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- **FastMCP**: [FastMCP Documentation](https://gofastmcp.com)
- **Semgrep**: [Semgrep Documentation](https://semgrep.dev/docs/)
- **Docker**: [Docker Documentation](https://docs.docker.com/)

---

## 💡 Tips & Best Practices

1. **Keep Rules Updated**: Regularly review and update your custom rules
2. **Monitor Logs**: Check logs periodically for errors or issues
3. **Resource Limits**: Set Docker memory/CPU limits for production
4. **Backups**: Back up your custom rules regularly
5. **Version Control**: Keep your rules in git for change tracking
6. **Testing**: Always test rules on sample code before deploying

---

## 📞 Support

For issues or questions:
1. Check the logs: `docker logs goberbot-semgrep-mcp-server`
2. Review this SETUP.md troubleshooting section
3. Check existing documentation in the repository

---

**Last Updated:** November 2025  
**Version:** 1.0.0

