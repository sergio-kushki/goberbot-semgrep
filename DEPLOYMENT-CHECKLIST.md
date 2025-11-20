# Goberbot-Semgrep MCP Server - Deployment Checklist

This checklist ensures the server is properly set up and ready for use.

## ✅ Pre-Deployment Checklist

### 1. System Requirements
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Cursor IDE installed (latest version)
- [ ] Git installed (for cloning)
- [ ] 4GB+ RAM available
- [ ] 2GB+ disk space available

### 2. Repository Setup
- [ ] Repository cloned to local machine
- [ ] Navigate to project root
- [ ] Verify custom rules exist in `custom-rules/`
- [ ] Check `mcp-server/` directory structure

### 3. Custom Rules Review
- [ ] Review `custom-rules/security.yaml`
- [ ] Review `custom-rules/code-quality.yaml`
- [ ] Add/modify rules as needed
- [ ] Test rules syntax (optional: run Semgrep locally)

## 🚀 Deployment Steps

### 4. Build and Start Server
```bash
# Navigate to project root
cd goberbot-semgrep

# Quick start (automated)
./start-server.sh

# OR manual start
cd mcp-server
docker-compose build
docker-compose up -d
```

**Verification:**
- [ ] Container is running: `docker ps | grep goberbot-semgrep-mcp-server`
- [ ] No error logs: `docker logs goberbot-semgrep-mcp-server --tail 50`
- [ ] Server shows "FastMCP 2.13.1" banner
- [ ] Server URL: `http://0.0.0.0:8000/mcp`

### 5. Verify Semgrep Installation
```bash
docker exec goberbot-semgrep-mcp-server semgrep --version
```

**Expected:** `1.144.0` (or similar version)

- [ ] Semgrep version displayed
- [ ] No "command not found" errors

### 6. Test Server Endpoints
```bash
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
      "clientInfo": {"name": "test", "version": "1.0"}
    }
  }'
```

**Expected:** JSON response with server capabilities

- [ ] HTTP 200 response
- [ ] JSON contains `"serverInfo"` and `"capabilities"`
- [ ] No 404 or 500 errors

## 🖥️ Cursor IDE Configuration

### 7. Configure MCP Settings

**File Location:**
- macOS/Linux: `~/.cursor/mcp.json`
- Windows: `%APPDATA%\.cursor\mcp.json`

**Required Configuration:**
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

**Checklist:**
- [ ] File created/edited at correct location
- [ ] JSON is valid (no syntax errors)
- [ ] URL includes `/mcp` path
- [ ] Uses `http://localhost:8000/mcp` (not `http://localhost:8000`)

### 8. Restart Cursor IDE
- [ ] Completely quit Cursor (not just close window)
- [ ] Reopen Cursor IDE
- [ ] Wait 10-15 seconds for MCP to initialize

### 9. Verify Cursor Connection

**Check MCP Logs/Status:**
- [ ] No 404 errors in MCP logs
- [ ] Connection status shows "Connected" or similar
- [ ] No "No server info found" errors

**If you see errors:**
- Double-check URL in `mcp.json` includes `/mcp`
- Restart Cursor completely
- Check server is still running: `docker ps`

## 🧪 Testing

### 10. Test from Cursor Chat

**Test 1: List Rules**
```
What Semgrep rules are available in the Goberbot MCP server?
```

**Expected:**
- [ ] Returns list of available rules
- [ ] Shows `security.yaml` and `code-quality.yaml`
- [ ] No errors or timeouts

**Test 2: Scan JavaScript**
```
Use Goberbot Semgrep to scan tests/sample-code/vulnerable.js
```

**Expected:**
- [ ] Returns ~10 findings
- [ ] Shows security issues (eval, XSS, weak crypto)
- [ ] Shows code quality issues (console.log, TODOs)
- [ ] Includes line numbers and severity

**Test 3: Scan Python**
```
Analyze tests/sample-code/vulnerable.py using Goberbot Semgrep
```

**Expected:**
- [ ] Returns ~7 findings
- [ ] Shows MD5 usage, print statements, TODOs
- [ ] No errors or crashes

### 11. Command Line Testing (Optional)

```bash
# Test with built-in script
cd mcp-server
./test-server.sh
```

- [ ] All tests pass
- [ ] No error messages

## 📊 Post-Deployment Validation

### 12. Performance Check
- [ ] Server responds in < 5 seconds
- [ ] Scans complete in < 10 seconds
- [ ] Container memory usage is reasonable (`docker stats`)

### 13. Resource Check
```bash
# Check container resources
docker stats goberbot-semgrep-mcp-server --no-stream
```

**Expected:**
- [ ] CPU: < 50% (idle), spikes during scans are normal
- [ ] Memory: < 500MB typical
- [ ] No constant high CPU/memory

### 14. Logging Check
```bash
# Check for errors
docker logs goberbot-semgrep-mcp-server | grep -i error
```

- [ ] No critical errors
- [ ] Only expected warnings (dependency conflicts are OK)

## 🛠️ Maintenance

### 15. Server Management Commands

**Know these commands:**

```bash
# View logs in real-time
docker logs -f goberbot-semgrep-mcp-server

# Restart server
cd mcp-server && docker-compose restart

# Stop server
./stop-server.sh
# OR
cd mcp-server && docker-compose down

# Rebuild (after rule changes)
cd mcp-server
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

- [ ] Tested restart command
- [ ] Tested stop command
- [ ] Know how to view logs

### 16. Backup Custom Rules
```bash
# Backup your custom rules
cp -r custom-rules/ custom-rules-backup-$(date +%Y%m%d)/
```

- [ ] Custom rules backed up
- [ ] Backup location documented

## 📚 Documentation Review

### 17. Documentation Check
- [ ] Read `SETUP.md` (comprehensive setup guide)
- [ ] Read `README.md` (project overview)
- [ ] Review `mcp-server/README.md` (server details)
- [ ] Check `EC2-DEPLOYMENT.md` if deploying to AWS

### 18. Troubleshooting Knowledge
- [ ] Know where logs are: `docker logs goberbot-semgrep-mcp-server`
- [ ] Know how to restart: `docker-compose restart`
- [ ] Know how to rebuild: `docker-compose build --no-cache`
- [ ] Read troubleshooting section in `SETUP.md`

## 🎯 Production Readiness (Optional)

### 19. Security Considerations
- [ ] Rules don't contain sensitive information
- [ ] Server running on localhost only (not exposed)
- [ ] Consider firewall rules for remote deployment
- [ ] Review what data is being scanned

### 20. Remote Deployment (Optional)
If deploying to remote server (EC2, VPS, etc.):

- [ ] Read `EC2-DEPLOYMENT.md`
- [ ] Set up SSL/TLS with reverse proxy
- [ ] Configure authentication if needed
- [ ] Set up monitoring/alerts
- [ ] Update Cursor config with remote URL

## ✨ Success Criteria

Your deployment is successful when:

✅ **Server is running:**
- Container shows as "Up" in `docker ps`
- Logs show "FastMCP 2.13.1" banner
- No critical errors in logs

✅ **Cursor is connected:**
- No 404 errors in MCP logs
- Can list rules successfully
- Can scan code and get results

✅ **Scans are working:**
- JavaScript test file returns ~10 findings
- Python test file returns ~7 findings
- Results include line numbers and severity

✅ **You understand maintenance:**
- Can restart the server
- Can view logs
- Can stop/start as needed

---

## 📞 Need Help?

If something isn't working:

1. **Check the logs:**
   ```bash
   docker logs goberbot-semgrep-mcp-server --tail 50
   ```

2. **Restart everything:**
   ```bash
   cd mcp-server
   docker-compose restart
   # Then restart Cursor IDE
   ```

3. **Review documentation:**
   - `SETUP.md` - Detailed setup and troubleshooting
   - Server logs - Often show the exact issue

4. **Common issues:**
   - 404 errors → Check URL includes `/mcp` path
   - Can't connect → Restart Cursor completely
   - No findings → Check rules are loaded in logs

---

**Deployment Date:** _____________  
**Deployed By:** _____________  
**Server URL:** `http://localhost:8000/mcp`  
**Status:** ⬜ In Progress  ⬜ Complete  ⬜ Issues

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

