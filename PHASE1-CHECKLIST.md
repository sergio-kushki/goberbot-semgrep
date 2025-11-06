# Phase 1: Local STDIO Setup - Checklist

## Installation Steps

- [ ] **Install Semgrep CLI**
  ```bash
  # Choose one:
  brew install semgrep          # macOS/Linux
  pip install semgrep           # Any platform
  ```

- [ ] **Verify Semgrep version** (must be 1.138.0+)
  ```bash
  semgrep --version
  ```

- [ ] **Install Semgrep MCP**
  ```bash
  pipx install semgrep-mcp
  ```

- [ ] **Verify MCP installation**
  ```bash
  semgrep-mcp --help
  ```

## Testing Steps

- [ ] **Test custom rules locally**
  ```bash
  # Unix/Linux/macOS
  bash scripts/test-local-scan.sh
  
  # Windows PowerShell
  powershell scripts/test-local-scan.ps1
  ```

- [ ] **Run Semgrep on sample code**
  ```bash
  semgrep --config custom-rules/ tests/sample-code/
  ```

- [ ] **Start MCP server in STDIO mode**
  ```bash
  semgrep-mcp
  ```

- [ ] **Test MCP with Inspector** (optional but recommended)
  ```bash
  npx @modelcontextprotocol/inspector semgrep-mcp
  ```

## Integration Steps

- [ ] **Configure MCP client** (choose one or more):

  ### Claude Desktop
  - [ ] Edit config file:
    - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
    - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
  - [ ] Add Semgrep MCP configuration
  - [ ] Restart Claude Desktop
  - [ ] Test: Ask Claude to scan code

  ### Cursor IDE
  - [ ] Open Cursor settings
  - [ ] Navigate to MCP configuration
  - [ ] Add Semgrep MCP server
  - [ ] Test: Use Cursor's AI with Semgrep

  ### Custom Client
  - [ ] Implement JSON-RPC over STDIO
  - [ ] Send `tools/list` request
  - [ ] Parse and use available tools

## Verification

- [ ] **Confirm findings are reported correctly**
  - Check that vulnerable.js triggers expected rules
  - Check that vulnerable.py triggers expected rules
  - Verify severity levels are appropriate

- [ ] **Test custom rule creation**
  - [ ] Create a new rule in `custom-rules/`
  - [ ] Test it with Semgrep CLI
  - [ ] Verify it works via MCP

- [ ] **Document any issues encountered**
  - [ ] Installation problems
  - [ ] Configuration challenges
  - [ ] Rule effectiveness

## Expected Outcomes

After completing Phase 1, you should be able to:

✅ Run Semgrep MCP locally with STDIO communication
✅ Apply custom rules to code
✅ Integrate with at least one MCP client
✅ See security and code quality findings in real-time
✅ Understand the MCP request/response format

## Known Issues & Solutions

### Issue: `semgrep-mcp` command not found
**Solution**: Ensure pipx bin directory is in PATH
```bash
pipx ensurepath
# Restart terminal
```

### Issue: Permission denied
**Solution**: Make scripts executable
```bash
chmod +x scripts/test-local-scan.sh
```

### Issue: Semgrep version too old
**Solution**: Upgrade Semgrep
```bash
pip install --upgrade semgrep
```

## Next Steps

Once Phase 1 is complete:
- [ ] Move to `PHASE2-CHECKLIST.md` for Docker deployment
- [ ] Document lessons learned
- [ ] Identify areas for custom wrapper development

## Notes

_Add any observations, issues, or ideas here:_

