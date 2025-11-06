# Quick Start Guide

Get up and running with Semgrep MCP in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- pip or pipx installed

## Installation (5 minutes)

### Step 1: Install Semgrep
```bash
pip install semgrep
```

### Step 2: Install Semgrep MCP
```bash
pipx install semgrep-mcp
```

### Step 3: Verify Installation
```bash
semgrep --version
# Should show 1.138.0 or higher

semgrep-mcp --help
# Should show MCP server options
```

## Quick Test (2 minutes)

### Test custom rules on sample code:
```bash
# Unix/Linux/macOS
bash scripts/test-local-scan.sh

# Windows PowerShell
powershell scripts/test-local-scan.ps1
```

Expected output:
```
✅ Semgrep installed: 1.xx.x
✅ Semgrep MCP installed
📂 Scanning JavaScript sample...
   Found X issues in JavaScript code
📂 Scanning Python sample...
   Found Y issues in Python code
```

## Start MCP Server

### Run in STDIO mode:
```bash
semgrep-mcp
```

The server is now running and waiting for MCP requests on stdin/stdout.

## Test with MCP Inspector (Optional)

In a new terminal:
```bash
npx @modelcontextprotocol/inspector semgrep-mcp
```

This opens a web interface to interact with the MCP server.

## Integrate with Claude Desktop

1. **Find your config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Add this configuration:**
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

3. **Restart Claude Desktop**

4. **Test it:** Ask Claude to "Scan this code with Semgrep" and paste some code.

## What's Next?

- ✅ Phase 1 complete! You have a working local MCP server.
- 📦 Next: Check out `PHASE2-CHECKLIST.md` for Docker deployment
- 🔧 Customize rules in `custom-rules/` directory
- 📚 Read the full `README.md` for detailed information

## Troubleshooting

**Command not found?**
```bash
pipx ensurepath
# Then restart your terminal
```

**Permission denied on scripts?**
```bash
chmod +x scripts/test-local-scan.sh
```

**Need help?** Check `PHASE1-CHECKLIST.md` for detailed troubleshooting.

