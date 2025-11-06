#!/bin/bash

# Test script to verify Semgrep installation and custom rules

echo "=================================="
echo "Semgrep MCP POC - Local Test"
echo "=================================="
echo ""

# Check if semgrep is installed
echo "1. Checking Semgrep installation..."
if ! command -v semgrep &> /dev/null; then
    echo "❌ Semgrep is not installed. Please install it first."
    echo "   Run: pip install semgrep"
    exit 1
fi

semgrep_version=$(semgrep --version)
echo "✅ Semgrep installed: $semgrep_version"
echo ""

# Check if semgrep-mcp is installed
echo "2. Checking Semgrep MCP installation..."
if ! command -v semgrep-mcp &> /dev/null; then
    echo "❌ Semgrep MCP is not installed. Please install it first."
    echo "   Run: pipx install semgrep-mcp"
    exit 1
fi

echo "✅ Semgrep MCP installed"
echo ""

# Test custom rules on sample code
echo "3. Testing custom rules on sample vulnerable code..."
echo ""

echo "📂 Scanning JavaScript sample..."
semgrep --config custom-rules/ tests/sample-code/vulnerable.js --json > tests/results-js.json
js_findings=$(cat tests/results-js.json | grep -o '"check_id"' | wc -l)
echo "   Found $js_findings issues in JavaScript code"
echo ""

echo "📂 Scanning Python sample..."
semgrep --config custom-rules/ tests/sample-code/vulnerable.py --json > tests/results-py.json
py_findings=$(cat tests/results-py.json | grep -o '"check_id"' | wc -l)
echo "   Found $py_findings issues in Python code"
echo ""

# Display summary
total_findings=$((js_findings + py_findings))
echo "=================================="
echo "Summary:"
echo "  Total findings: $total_findings"
echo "  - JavaScript: $js_findings"
echo "  - Python: $py_findings"
echo ""
echo "Results saved to:"
echo "  - tests/results-js.json"
echo "  - tests/results-py.json"
echo "=================================="
echo ""

# Test MCP server (if available)
echo "4. Testing MCP server connection..."
echo "   To test the MCP server interactively, run:"
echo "   npx @modelcontextprotocol/inspector semgrep-mcp"
echo ""

echo "✅ All checks complete!"

