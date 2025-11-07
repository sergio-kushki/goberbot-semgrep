# Phase 3: Custom MCP Server - Architecture

## Overview

Build a custom MCP server that wraps Semgrep CLI to provide:
- Full control over functionality
- Custom rule integration
- Team-specific enhancements
- No external dependencies
- Privacy and security

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Cursor IDE / AI                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ MCP Protocol (stdio/http)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Custom MCP Server (Python)                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Protocol Handler                                │  │
│  │  - tools/list                                        │  │
│  │  - tools/call                                        │  │
│  │  - resources/list (custom rules schema)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Custom Business Logic Layer                         │  │
│  │  - Git diff analysis                                 │  │
│  │  - Result filtering/aggregation                      │  │
│  │  - Custom rule selection                             │  │
│  │  - Team-specific preprocessing                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Semgrep CLI Wrapper                                 │  │
│  │  - Execute semgrep commands                          │  │
│  │  - Parse JSON output                                 │  │
│  │  - Handle errors                                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ↓
                    ┌──────────────────┐
                    │   Semgrep CLI    │
                    │   + Custom Rules │
                    └──────────────────┘
```

---

## Components

### 1. **MCP Server Core** (`mcp_server.py`)
- Implements MCP protocol (JSON-RPC 2.0)
- Handles stdio/http transport
- Routes tool calls to handlers

### 2. **Tool Handlers** (`tools/`)
- `security_scan.py` - Fast security scanning
- `full_scan.py` - Comprehensive code analysis
- `custom_rule_scan.py` - Use custom rules
- `git_diff_scan.py` - Scan only changed files
- `ast_generator.py` - Generate ASTs

### 3. **Semgrep Wrapper** (`semgrep_wrapper.py`)
- Execute semgrep CLI commands
- Parse JSON output
- Handle errors and timeouts
- Manage custom rule paths

### 4. **Custom Features** (`custom/`)
- `result_filter.py` - Filter/aggregate findings
- `rule_selector.py` - Smart rule selection
- `git_integration.py` - Git diff analysis
- `metrics.py` - Track scan statistics

---

## MCP Tools to Expose

### Core Tools
1. **`security_scan`**
   - Quick security check using built-in rules
   - Input: code files
   - Output: Security findings

2. **`custom_scan`**
   - Scan with custom rules from `custom-rules/`
   - Input: code files, rule path (optional)
   - Output: Findings with custom rule matches

3. **`git_diff_scan`**
   - Scan only changed files in git diff
   - Input: git ref (default: HEAD)
   - Output: Findings in changed code only

4. **`validate_rule`**
   - Test a custom Semgrep rule
   - Input: rule YAML, test code
   - Output: Validation results

### Advanced Tools
5. **`get_ast`**
   - Generate Abstract Syntax Tree
   - Input: code, language
   - Output: AST in JSON format

6. **`rule_search`**
   - Search Semgrep rule registry
   - Input: query, language, category
   - Output: Matching rules

---

## Implementation Plan

### Phase 3.1: Basic MCP Server
- [ ] Set up Python MCP server skeleton
- [ ] Implement stdio transport
- [ ] Add `security_scan` tool
- [ ] Test with Cursor

### Phase 3.2: Custom Rules Integration
- [ ] Add `custom_scan` tool
- [ ] Load rules from `custom-rules/`
- [ ] Support rule validation
- [ ] Add rule schema resources

### Phase 3.3: Git Integration
- [ ] Implement `git_diff_scan`
- [ ] Parse git diff output
- [ ] Filter results to changed lines
- [ ] Support commit range analysis

### Phase 3.4: Advanced Features
- [ ] Result filtering/aggregation
- [ ] Metrics dashboard
- [ ] Caching for performance
- [ ] HTTP transport support

---

## Technology Stack

**Server:**
- **Language:** Python 3.13+
- **MCP Library:** `mcp` package (Model Context Protocol SDK)
- **Semgrep:** Existing CLI installation
- **Git:** `GitPython` for git operations

**Key Dependencies:**
```python
mcp>=1.0.0              # MCP protocol implementation
pydantic>=2.0           # Data validation
gitpython>=3.1          # Git integration
uvicorn>=0.27           # HTTP server (optional)
```

---

## File Structure

```
goberbot-semgrep/
├── custom-mcp/
│   ├── __init__.py
│   ├── server.py              # MCP server entry point
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── handler.py         # MCP protocol handler
│   │   └── transport.py       # stdio/http transport
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── security_scan.py
│   │   ├── custom_scan.py
│   │   ├── git_diff_scan.py
│   │   └── validate_rule.py
│   ├── semgrep/
│   │   ├── __init__.py
│   │   ├── wrapper.py         # CLI wrapper
│   │   └── parser.py          # Result parser
│   └── custom/
│       ├── __init__.py
│       ├── filters.py
│       └── metrics.py
├── tests/
│   └── test_custom_mcp.py
└── requirements-mcp.txt
```

---

## Benefits

### 1. **Full Control**
- Customize every aspect of functionality
- Add team-specific features
- No dependency on external services

### 2. **Privacy & Security**
- Code stays local
- No data sent to external servers
- Custom compliance rules

### 3. **Custom Rules**
- Direct integration with `custom-rules/`
- Real-time rule validation
- Team-specific rule library

### 4. **Enhanced Features**
- Git diff scanning (only changed code)
- Result aggregation
- Custom preprocessing
- Performance metrics

### 5. **Flexibility**
- Easy to extend
- Can add new tools
- Custom output formats
- Integration with CI/CD

---

## Success Criteria

- ✅ MCP server runs locally
- ✅ Exposes security scanning via MCP
- ✅ Uses custom rules from `custom-rules/`
- ✅ Integrates with Cursor AI
- ✅ Faster than remote server (local execution)
- ✅ Supports git diff scanning
- ✅ No external dependencies for core functionality

---

## Estimated Effort

- **Phase 3.1:** 4-6 hours (basic server + security_scan)
- **Phase 3.2:** 2-3 hours (custom rules integration)
- **Phase 3.3:** 3-4 hours (git integration)
- **Phase 3.4:** 4-6 hours (advanced features)

**Total:** ~13-19 hours for full implementation

---

## Next Steps

1. Review architecture and provide feedback
2. Set up Python project structure
3. Implement basic MCP server
4. Test with Cursor
5. Iterate and add features

---

**Status:** 📋 Planning Phase  
**Priority:** HIGH - Addresses core project goals  
**Risk:** LOW - All components proven separately

