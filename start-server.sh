#!/bin/bash
# Goberbot-Semgrep MCP Server - Quick Start Script
# This script starts the MCP server and verifies it's running correctly

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Goberbot-Semgrep MCP Server - Quick Start                ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "   Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "   Please install Docker Compose"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is installed"
echo ""

# Navigate to mcp-server directory
cd "$(dirname "$0")/mcp-server"

echo "📦 Starting Goberbot-Semgrep MCP Server..."
echo ""

# Check if container is already running
if docker ps | grep -q goberbot-semgrep-mcp-server; then
    echo "⚠️  Server is already running"
    echo ""
    read -p "Do you want to restart it? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔄 Restarting server..."
        docker-compose restart
    else
        echo "ℹ️  Keeping existing server running"
    fi
else
    # Start the server
    docker-compose up -d
fi

echo ""
echo "⏳ Waiting for server to start..."
sleep 5

# Check if container is running
if docker ps | grep -q goberbot-semgrep-mcp-server; then
    echo "✅ Server is running!"
else
    echo "❌ Server failed to start"
    echo "   Check logs with: docker logs goberbot-semgrep-mcp-server"
    exit 1
fi

echo ""
echo "🔍 Server Status:"
docker ps --filter "name=goberbot-semgrep-mcp-server" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📋 Recent Logs:"
docker logs goberbot-semgrep-mcp-server --tail 20

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Server is ready!"
echo ""
echo "📍 Server URL: http://localhost:8000/mcp"
echo ""
echo "🔧 Next Steps:"
echo "   1. Configure Cursor IDE (~/.cursor/mcp.json)"
echo "   2. Add this to your mcp.json:"
echo ""
echo '      {' 
echo '        "mcpServers": {'
echo '          "semgrep_custom_local": {'
echo '            "type": "streamable-http",'
echo '            "url": "http://localhost:8000/mcp"'
echo '          }'
echo '        }'
echo '      }'
echo ""
echo "   3. Restart Cursor IDE"
echo "   4. Test: 'What Semgrep rules are available?'"
echo ""
echo "📚 Full documentation: See SETUP.md"
echo ""
echo "🛠️  Useful Commands:"
echo "   - View logs:    docker logs -f goberbot-semgrep-mcp-server"
echo "   - Stop server:  cd mcp-server && docker-compose down"
echo "   - Restart:      cd mcp-server && docker-compose restart"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

