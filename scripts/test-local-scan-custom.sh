#!/bin/bash

# Test script to verify Semgrep with CUSTOM RULES ONLY

echo "=================================="
echo "Semgrep - Custom Rules Test"
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

# Test custom rules on sample code
echo "2. Testing CUSTOM RULES on sample vulnerable code..."
echo ""

echo "📂 Scanning JavaScript sample..."
semgrep --config custom-rules/ tests/sample-code/vulnerable.js --json > tests/results-custom-js.json
js_findings=$(cat tests/results-custom-js.json | grep -o '"check_id"' | wc -l)
echo "   Found $js_findings issues in JavaScript code"
echo ""

echo "📂 Scanning Python sample..."
semgrep --config custom-rules/ tests/sample-code/vulnerable.py --json > tests/results-custom-py.json
py_findings=$(cat tests/results-custom-py.json | grep -o '"check_id"' | wc -l)
echo "   Found $py_findings issues in Python code"
echo ""

# Display summary
total_findings=$((js_findings + py_findings))
echo "=================================="
echo "Summary (Custom Rules Only):"
echo "  Total findings: $total_findings"
echo "  - JavaScript: $js_findings"
echo "  - Python: $py_findings"
echo ""
echo "Results saved to:"
echo "  - tests/results-custom-js.json"
echo "  - tests/results-custom-py.json"
echo "=================================="
echo ""

echo "✅ Custom rules test complete!"


