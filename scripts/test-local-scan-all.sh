#!/bin/bash

# Test script to verify Semgrep with CUSTOM + NATIVE RULES COMBINED

echo "=================================="
echo "Semgrep - All Rules Test"
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

# Test all rules on sample code
echo "2. Testing ALL RULES (Custom + Native) on sample vulnerable code..."
echo "   Using: custom-rules/ + p/security-audit"
echo ""

echo "📂 Scanning JavaScript sample..."
semgrep --config custom-rules/ --config p/security-audit tests/sample-code/vulnerable.js --json > tests/results-all-js.json
js_findings=$(cat tests/results-all-js.json | grep -o '"check_id"' | wc -l)
echo "   Found $js_findings issues in JavaScript code"
echo ""

echo "📂 Scanning Python sample..."
semgrep --config custom-rules/ --config p/security-audit tests/sample-code/vulnerable.py --json > tests/results-all-py.json
py_findings=$(cat tests/results-all-py.json | grep -o '"check_id"' | wc -l)
echo "   Found $py_findings issues in Python code"
echo ""

# Display summary
total_findings=$((js_findings + py_findings))
echo "=================================="
echo "Summary (Custom + Native Rules):"
echo "  Total findings: $total_findings"
echo "  - JavaScript: $js_findings"
echo "  - Python: $py_findings"
echo ""
echo "Results saved to:"
echo "  - tests/results-all-js.json"
echo "  - tests/results-all-py.json"
echo "=================================="
echo ""

echo "ℹ️  This combines:"
echo "   - Your custom rules (custom-rules/)"
echo "   - Semgrep's security-audit ruleset"
echo ""

echo "✅ Combined rules test complete!"


