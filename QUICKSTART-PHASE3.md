# 🚀 Phase 3 Quick Start Guide

Your custom Semgrep MCP Server is ready to deploy!

---

## ✅ What's Been Built

```
✅ Custom MCP Server (FastMCP 2.0)
✅ Semgrep CLI Wrapper
✅ Docker Configuration
✅ Hybrid Rules Loading (URL → Bundled → S3-ready)
✅ EC2 Deployment Guide
✅ Testing Suite
✅ Complete Documentation
```

---

## 🎯 Three Ways to Use It

### Option 1: Local Development (Fastest)

```bash
cd mcp-server
./quick-start.sh
```

Then add to `~/.cursor/mcp.json`:
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

**Restart Cursor** and you're done! ✨

---

### Option 2: EC2 Deployment (Team Access)

Follow `EC2-DEPLOYMENT.md`:

```bash
# On EC2
cd mcp-server
docker-compose up -d
```

Then in Cursor:
```json
{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://YOUR_EC2_IP:8000"
    }
  }
}
```

---

### Option 3: Manual Docker (Any Platform)

```bash
# Build
docker build -t semgrep-mcp -f mcp-server/Dockerfile .

# Run
docker run -d -p 8000:8000 semgrep-mcp

# Test
curl http://localhost:8000/health
```

---

## 🧪 Quick Test

```bash
cd mcp-server
./test-server.sh
```

Should show:
```
✅ Health check passed
✅ Tools list includes scan_code
✅ Found 1 security issue(s)
✅ Python scan completed
✅ All tests passed!
```

---

## 🔧 Configuration Options

### Environment Variables

```bash
# Custom rules from URL
docker run -d -p 8000:8000 \
  -e CUSTOM_RULES_URL="https://your-domain.com/rules.yaml" \
  semgrep-mcp

# Different port
docker run -d -p 9000:9000 \
  -e MCP_PORT=9000 \
  semgrep-mcp
```

### Volume Mount (Local Rules)

```bash
docker run -d -p 8000:8000 \
  -v ./custom-rules:/app/custom-rules:ro \
  semgrep-mcp
```

---

## 📊 MCP Tools Available

### 1. `scan_code`
Scan code for vulnerabilities.

**Usage in Cursor:**
> "Scan this code for security issues"

**Direct API:**
```bash
curl -X POST http://localhost:8000/mcp/v1/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scan_code",
    "arguments": {
      "code": "eval(userInput);",
      "language": "javascript"
    }
  }'
```

### 2. `list_available_rules`
Show available rule files.

### 3. `reload_rules`
Refresh rules from source.

---

## 📁 Project Structure

```
goberbot-semgrep/
├── mcp-server/              ← Your new server! 🎉
│   ├── server.py            ← FastMCP implementation
│   ├── semgrep_runner.py    ← Semgrep wrapper
│   ├── Dockerfile           ← Container config
│   ├── docker-compose.yml   ← Easy deployment
│   ├── quick-start.sh       ← One-command start
│   └── test-server.sh       ← Automated tests
├── custom-rules/            ← Your security rules
│   ├── security.yaml        ← 10 security rules
│   └── code-quality.yaml    ← 7 quality rules
├── EC2-DEPLOYMENT.md        ← Cloud deployment guide
└── PHASE3-IMPLEMENTATION.md ← Technical details
```

---

## 🐛 Troubleshooting

### Issue: Port 8000 already in use

```bash
# Use different port
docker run -d -p 8001:8000 semgrep-mcp

# Then in Cursor use :8001
```

### Issue: Rules not found

```bash
# Check rules in container
docker exec -it <container-id> ls /app/custom-rules/

# Check health endpoint
curl http://localhost:8000/health | jq .rules_source
```

### Issue: Cursor can't connect

1. Check server is running: `docker ps`
2. Check health: `curl http://localhost:8000/health`
3. Restart Cursor after config change
4. Check Cursor logs (Help → Show Logs)

---

## 📚 Next Steps

### Today
- [ ] Test locally with `./quick-start.sh`
- [ ] Scan your actual code files
- [ ] Verify custom rules work

### This Week
- [ ] Deploy to EC2 (if needed for team)
- [ ] Share endpoint with team
- [ ] Add your own custom rules

### This Month
- [ ] Set up S3 rules storage
- [ ] Add authentication
- [ ] Monitor usage and performance

---

## 🎓 Learn More

| Document | Purpose |
|----------|---------|
| `mcp-server/README.md` | Server usage & API reference |
| `EC2-DEPLOYMENT.md` | Complete AWS deployment |
| `PHASE3-IMPLEMENTATION.md` | Technical deep-dive |
| `STRATEGIC-SUMMARY.md` | Why we built this |

---

## 💡 Tips

**For Best Performance:**
- Use local deployment for personal use
- Use EC2 for team access
- Cache rules locally (bundled in Docker)
- Run on fast SSD storage

**For Security:**
- Use SSH tunnels for EC2 access
- Add authentication for production
- Keep rules in private repository
- Regularly update Semgrep CLI

**For Maintenance:**
- Check logs: `docker logs -f <container>`
- Update image: Rebuild with `--no-cache`
- Backup custom rules regularly
- Monitor disk space on EC2

---

## 🎉 Success!

You now have a **production-ready** custom Semgrep MCP server that:

- ✅ Works with Cursor IDE
- ✅ Uses your custom rules
- ✅ Gives you full privacy & control
- ✅ Can be deployed anywhere
- ✅ Is fast, reliable, and maintainable

**Ready to scan some code?** Run `./quick-start.sh` and let's go! 🚀

---

**Questions?** Check the docs or open an issue!

