#!/bin/bash
# Goberbot-Semgrep MCP Server - Stop Script

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Goberbot-Semgrep MCP Server - Stop                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Navigate to mcp-server directory
cd "$(dirname "$0")/mcp-server"

# Check if container is running
if docker ps | grep -q goberbot-semgrep-mcp-server; then
    echo "🛑 Stopping Goberbot-Semgrep MCP Server..."
    docker-compose down
    echo ""
    echo "✅ Server stopped successfully"
else
    echo "ℹ️  Server is not running"
fi

echo ""

