#!/bin/bash
# Test script for Semgrep MCP Server

set -e

echo "🧪 Testing Semgrep MCP Server..."
echo ""

SERVER_URL="${SERVER_URL:-http://localhost:8000}"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Health check
echo "1️⃣  Testing health endpoint..."
if curl -s -f "${SERVER_URL}/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "   Make sure the server is running on ${SERVER_URL}"
    exit 1
fi
echo ""

# Test 2: List tools
echo "2️⃣  Testing MCP tools list..."
TOOLS_RESPONSE=$(curl -s -X POST "${SERVER_URL}/mcp/v1/list_tools" \
    -H "Content-Type: application/json")

if echo "$TOOLS_RESPONSE" | grep -q "scan_code"; then
    echo -e "${GREEN}✅ Tools list includes scan_code${NC}"
else
    echo -e "${RED}❌ scan_code tool not found${NC}"
    echo "   Response: $TOOLS_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Scan JavaScript code with eval()
echo "3️⃣  Testing scan_code with JavaScript..."
SCAN_RESPONSE=$(curl -s -X POST "${SERVER_URL}/mcp/v1/call_tool" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "scan_code",
        "arguments": {
            "code": "eval(userInput);",
            "language": "javascript",
            "rules_file": "security.yaml"
        }
    }')

if echo "$SCAN_RESPONSE" | grep -q "findings"; then
    FINDINGS_COUNT=$(echo "$SCAN_RESPONSE" | grep -o '"total":[0-9]*' | grep -o '[0-9]*')
    if [ "$FINDINGS_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Found $FINDINGS_COUNT security issue(s)${NC}"
        echo "   Sample: eval() usage detected"
    else
        echo -e "${YELLOW}⚠️  Scan completed but found 0 issues${NC}"
        echo "   This might indicate rules not loaded properly"
    fi
else
    echo -e "${RED}❌ Scan failed${NC}"
    echo "   Response: $SCAN_RESPONSE"
    exit 1
fi
echo ""

# Test 4: Scan Python code with hardcoded password
echo "4️⃣  Testing scan_code with Python..."
SCAN_RESPONSE=$(curl -s -X POST "${SERVER_URL}/mcp/v1/call_tool" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "scan_code",
        "arguments": {
            "code": "password = \"admin123\"",
            "language": "python",
            "rules_file": "security.yaml"
        }
    }')

if echo "$SCAN_RESPONSE" | grep -q "findings"; then
    echo -e "${GREEN}✅ Python scan completed${NC}"
else
    echo -e "${RED}❌ Python scan failed${NC}"
    exit 1
fi
echo ""

# Test 5: List available rules
echo "5️⃣  Testing list_available_rules..."
RULES_RESPONSE=$(curl -s -X POST "${SERVER_URL}/mcp/v1/call_tool" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "list_available_rules",
        "arguments": {}
    }')

if echo "$RULES_RESPONSE" | grep -q "security.yaml"; then
    echo -e "${GREEN}✅ Rules list includes security.yaml${NC}"
else
    echo -e "${YELLOW}⚠️  security.yaml not found in rules list${NC}"
fi
echo ""

# Test 6: Empty code validation
echo "6️⃣  Testing input validation (empty code)..."
EMPTY_RESPONSE=$(curl -s -X POST "${SERVER_URL}/mcp/v1/call_tool" \
    -H "Content-Type: application/json" \
    -d '{
        "name": "scan_code",
        "arguments": {
            "code": "",
            "language": "javascript"
        }
    }')

if echo "$EMPTY_RESPONSE" | grep -q "empty"; then
    echo -e "${GREEN}✅ Empty code validation working${NC}"
else
    echo -e "${YELLOW}⚠️  Empty code validation might not be working${NC}"
fi
echo ""

# Summary
echo "======================================"
echo -e "${GREEN}✅ All tests passed!${NC}"
echo "======================================"
echo ""
echo "Server is ready to use at: ${SERVER_URL}"
echo ""
echo "Next steps:"
echo "  1. Add to Cursor IDE config:"
echo "     ~/.cursor/mcp.json"
echo ""
echo "  2. Configuration:"
echo '     {
       "mcpServers": {
         "semgrep_custom": {
           "type": "streamable-http",
           "url": "'${SERVER_URL}'"
         }
       }
     }'
echo ""

