#!/bin/bash

# Test script to verify Semgrep with NATIVE/BUILT-IN RULES ONLY

echo "=================================="
echo "Semgrep - Native Rules Test"
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

# Test native rules on sample code
echo "2. Testing NATIVE RULES on sample vulnerable code..."
echo "   Using: p/security-audit (Semgrep's security ruleset)"
echo ""

echo "📂 Scanning JavaScript sample..."
semgrep --config p/security-audit tests/sample-code/vulnerable.js --json > tests/results-native-js.json
js_findings=$(cat tests/results-native-js.json | grep -o '"check_id"' | wc -l)
echo "   Found $js_findings issues in JavaScript code"
echo ""

echo "📂 Scanning Python sample..."
semgrep --config p/security-audit tests/sample-code/vulnerable.py --json > tests/results-native-py.json
py_findings=$(cat tests/results-native-py.json | grep -o '"check_id"' | wc -l)
echo "   Found $py_findings issues in Python code"
echo ""

# Display summary
total_findings=$((js_findings + py_findings))
echo "=================================="
echo "Summary (Native Rules Only):"
echo "  Total findings: $total_findings"
echo "  - JavaScript: $js_findings"
echo "  - Python: $py_findings"
echo ""
echo "Results saved to:"
echo "  - tests/results-native-js.json"
echo "  - tests/results-native-py.json"
echo "=================================="
echo ""

echo "ℹ️  Note: Native rules use 'p/security-audit' ruleset"
echo "   Other available rulesets:"
echo "   - p/owasp-top-ten"
echo "   - p/ci"
echo "   - p/javascript"
echo "   - p/python"
echo ""

echo "✅ Native rules test complete!"


