# Phase 1: Local STDIO Setup - Checklist

## Installation Steps

- [x] **Install Semgrep CLI** ✅
  ```bash
  # Used virtual environment approach
  python3 -m venv venv
  source venv/bin/activate
  pip install semgrep
  ```
  **Result:** Semgrep 1.135.0 installed successfully

- [x] **Verify Semgrep version** ✅
  ```bash
  semgrep --version
  ```
  **Result:** Version 1.135.0 (slightly below 1.138.0 but functional)

- [x] **Install Semgrep MCP** ✅
  ```bash
  pip install semgrep-mcp
  ```
  **Result:** Installed successfully but deprecated (see notes below)

- [x] **Verify MCP installation** ✅
  ```bash
  semgrep-mcp --help
  ```
  **Result:** Command works, shows help output

## Testing Steps

- [x] **Test custom rules locally** ✅
  ```bash
  bash scripts/test-local-scan.sh
  ```
  **Result:** Successfully detected 17 issues (10 in JavaScript, 7 in Python)
  - Fixed YAML syntax errors in `security.yaml` (regex escaping)
  - All custom rules working correctly

- [x] **Run Semgrep on sample code** ✅
  ```bash
  semgrep --config custom-rules/ tests/sample-code/
  ```
  **Result:** Detected all intentional vulnerabilities:
  - eval() usage, hardcoded passwords, XSS, insecure random, MD5, etc.
  - Results saved to `tests/results-js.json` and `tests/results-py.json`

- [x] **Start MCP server in STDIO mode** ⚠️ **PARTIAL**
  ```bash
  semgrep-mcp
  ```
  **Result:** Server starts but only provides deprecation notice tool
  - MCP Inspector shows server running
  - No actual scanning tools available (requires Semgrep Pro)

- [x] **Test MCP with Inspector** ✅
  ```bash
  npx @modelcontextprotocol/inspector semgrep-mcp
  ```
  **Result:** Inspector connected successfully, proper protocol handshake

## Integration Steps

- [x] **Configure MCP client** ⚠️ **PARTIAL SUCCESS**

  ### Cursor IDE (Tested)
  - [x] Created wrapper script: `run-semgrep-mcp.sh`
  - [x] Configured `~/.cursor/mcp.json` with semgrep server
  - [x] Server connects and runs successfully
  - [x] MCP protocol handshake works
  - ❌ **No scanning tools available** (only deprecation notice)
  
  **Configuration used:**
  ```json
  {
    "mcpServers": {
      "semgrep": {
        "command": "/Users/sergio.arancibia/CursorProjects/goberbot-semgrep/run-semgrep-mcp.sh",
        "args": []
      }
    }
  }
  ```

  ### Claude Desktop (Not Tested)
  - [ ] Not tested in this phase

  ### Custom Client (Not Tested)
  - [ ] Not tested in this phase

## Verification

- [x] **Confirm findings are reported correctly** ✅
  - ✅ vulnerable.js triggers 10 expected rules
  - ✅ vulnerable.py triggers 7 expected rules
  - ✅ Severity levels appropriate (ERROR/WARNING/INFO)
  - ✅ CWE mappings included in metadata

- [x] **Test custom rule creation** ✅
  - ✅ Fixed YAML syntax issues in existing rules
  - ✅ Rules validated with Semgrep CLI
  - ❌ Cannot verify via MCP (no tools available)

- [x] **Document any issues encountered** ✅
  - ✅ Installation problems documented below
  - ✅ Configuration challenges documented
  - ✅ Rule effectiveness confirmed

## Expected Outcomes

After completing Phase 1, you should be able to:

✅ **Run Semgrep CLI locally** - Successfully working with custom rules
✅ **Apply custom rules to code** - 17 findings detected across JS and Python
⚠️ **MCP Server STDIO** - Server runs but deprecated package has no tools
❌ **Full MCP Integration** - Requires Semgrep Pro Engine
✅ **Understand MCP protocol** - Successfully tested initialization and handshake

## Known Issues & Solutions

### Issue: Python externally-managed-environment error
**Problem**: macOS Python 3.13+ prevents system-wide pip installs
**Solution**: Use virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install semgrep semgrep-mcp
```

### Issue: urllib3 metadata corruption
**Problem**: System urllib3 has corrupted metadata preventing Semgrep install
**Solution**: Use `--ignore-installed` flag or venv (recommended)
```bash
pip install --ignore-installed urllib3
pip install semgrep
```

### Issue: YAML syntax errors in custom rules
**Problem**: Special characters in regex patterns (brackets, braces) break YAML parsing
**Solution**: Use double quotes with proper escaping
```yaml
# Bad:
pattern-regex: '(password)\s*=\s*["'][^"\']+["\']'

# Good:
pattern-regex: "(password)\\s*=\\s*[\"'][^\"']+[\"']"
```

### Issue: MCP server "Connection closed" error (-32000)
**Problem**: MCP server crashes immediately when spawned by Cursor
**Solution**: Create wrapper script that activates venv first
```bash
#!/bin/bash
cd /path/to/project
source venv/bin/activate
exec semgrep-mcp "$@"
```

### Issue: Semgrep MCP requires Pro Engine
**Problem**: `semgrep mcp` command requires proprietary Semgrep Pro
**Solution**: Use deprecated `semgrep-mcp` package (limited functionality) or upgrade to Pro
```bash
# Open-source (deprecated, no scanning tools):
pip install semgrep-mcp

# Pro version (requires license):
# Install proprietary semgrep binary
semgrep mcp  # Full MCP functionality
```

### Issue: Homebrew taking too long (30+ minutes)
**Problem**: Homebrew compiles dependencies from source (cmake, llvm, rust, etc.)
**Solution**: Use pip with virtual environment instead (1-2 minutes)
```bash
python3 -m venv venv
source venv/bin/activate
pip install semgrep
```

## Next Steps

Once Phase 1 is complete:
- [x] Phase 1 completed with partial MCP success
- [ ] **Decision Required**: Proceed with Phase 2 (Docker) or acquire Semgrep Pro for full MCP?
- [ ] Document lessons learned ✅ (see notes below)
- [ ] Consider alternative approaches (custom wrapper without MCP)

## Phase 1 Summary

### ✅ **What Worked**
1. **Semgrep CLI**: Fully functional with custom rules
2. **Custom Rules**: Successfully created and tested 15+ security & code quality rules
3. **Test Framework**: Automated testing with sample vulnerable code
4. **Results**: Detected 17 intentional vulnerabilities across JavaScript and Python
5. **MCP Protocol**: Successfully understood and tested MCP handshake/initialization

### ❌ **What Didn't Work**
1. **Full MCP Integration**: `semgrep-mcp` package is deprecated stub with no scanning tools
2. **Semgrep Pro Requirement**: New `semgrep mcp` command requires proprietary license
3. **Direct AI Integration**: Cannot expose Semgrep tools to Cursor AI without Pro version

### ⚠️ **Blockers for Full MCP**
- **Semgrep Pro Engine** required for `semgrep mcp` command
- **Open-source limitation**: OSS version lacks MCP scanning capabilities
- **Deprecated package**: `semgrep-mcp` only shows deprecation notice, no actual tools

## Notes

### Installation Observations
- **Virtual environment essential** on macOS 13+ due to PEP 668
- **pip faster than Homebrew** (2 mins vs 30+ mins for same result)
- **urllib3 corruption common** on systems with multiple Python versions

### Custom Rules Lessons
- **YAML syntax critical**: Regex patterns need careful escaping in double quotes
- **Rule testing workflow**: CLI testing faster than MCP for rule development
- **CWE mappings valuable**: Adds context and professionalism to findings

### MCP Integration Insights
- **Wrapper script necessary**: Cursor doesn't activate venv automatically
- **Protocol complexity**: MCP requires proper initialization sequence
- **Tool availability**: MCP tools may not be exposed to all conversation contexts
- **Semgrep strategy**: Phasing out OSS MCP support to promote Pro version

### Recommendations for Phase 2
1. **Option A**: Proceed with Docker deployment of Semgrep CLI (skip MCP)
2. **Option B**: Acquire Semgrep Pro for full MCP functionality
3. **Option C**: Build custom wrapper that exposes Semgrep CLI as simple HTTP API
4. **Option D**: Use GitHub Actions for automated Semgrep scans instead of real-time

### Files Created
- `venv/` - Python virtual environment (not in git)
- `run-semgrep-mcp.sh` - Wrapper script for MCP server
- `tests/results-js.json` - JavaScript scan results
- `tests/results-py.json` - Python scan results
- `~/.cursor/mcp.json` - Cursor MCP configuration

### Key Findings
- **17 total vulnerabilities detected** in test files
- **10 JavaScript issues**: eval(), XSS, weak crypto, console.log, TODOs, magic numbers
- **7 Python issues**: hardcoded secrets, exec(), weak crypto, insecure random, print statements
- **Rule precision**: No false positives in sample code
- **Performance**: Sub-second scans on small test files

**Date Completed**: November 6, 2025  
**Status**: ✅ Phase 1 Complete (CLI Success, MCP Partial)

