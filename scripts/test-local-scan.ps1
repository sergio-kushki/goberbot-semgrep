# PowerShell version of the test script for Windows

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Semgrep MCP POC - Local Test" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if semgrep is installed
Write-Host "1. Checking Semgrep installation..." -ForegroundColor Yellow
try {
    $semgrepVersion = semgrep --version 2>&1
    Write-Host "✅ Semgrep installed: $semgrepVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Semgrep is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Run: pip install semgrep" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if semgrep-mcp is installed
Write-Host "2. Checking Semgrep MCP installation..." -ForegroundColor Yellow
try {
    $mcpCheck = Get-Command semgrep-mcp -ErrorAction Stop
    Write-Host "✅ Semgrep MCP installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Semgrep MCP is not installed. Please install it first." -ForegroundColor Red
    Write-Host "   Run: pipx install semgrep-mcp" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Test custom rules on sample code
Write-Host "3. Testing custom rules on sample vulnerable code..." -ForegroundColor Yellow
Write-Host ""

Write-Host "📂 Scanning JavaScript sample..." -ForegroundColor Cyan
semgrep --config custom-rules/ tests/sample-code/vulnerable.js --json | Out-File -FilePath tests/results-js.json -Encoding utf8
$jsContent = Get-Content tests/results-js.json -Raw
$jsFindings = ([regex]::Matches($jsContent, '"check_id"')).Count
Write-Host "   Found $jsFindings issues in JavaScript code" -ForegroundColor White
Write-Host ""

Write-Host "📂 Scanning Python sample..." -ForegroundColor Cyan
semgrep --config custom-rules/ tests/sample-code/vulnerable.py --json | Out-File -FilePath tests/results-py.json -Encoding utf8
$pyContent = Get-Content tests/results-py.json -Raw
$pyFindings = ([regex]::Matches($pyContent, '"check_id"')).Count
Write-Host "   Found $pyFindings issues in Python code" -ForegroundColor White
Write-Host ""

# Display summary
$totalFindings = $jsFindings + $pyFindings
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  Total findings: $totalFindings" -ForegroundColor White
Write-Host "  - JavaScript: $jsFindings" -ForegroundColor White
Write-Host "  - Python: $pyFindings" -ForegroundColor White
Write-Host ""
Write-Host "Results saved to:" -ForegroundColor Yellow
Write-Host "  - tests/results-js.json" -ForegroundColor White
Write-Host "  - tests/results-py.json" -ForegroundColor White
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Test MCP server
Write-Host "4. Testing MCP server connection..." -ForegroundColor Yellow
Write-Host "   To test the MCP server interactively, run:" -ForegroundColor White
Write-Host "   npx @modelcontextprotocol/inspector semgrep-mcp" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ All checks complete!" -ForegroundColor Green

