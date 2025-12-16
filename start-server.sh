#!/bin/bash
# Goberbot-Semgrep MCP Server - Quick Start Script
# This script starts the MCP server and verifies it's running correctly
#
# Build Strategy:
#   - FastMCP 2.3+ in main Python environment (for streamable-http support)
#   - Semgrep isolated in separate venv (/opt/semgrep-venv) to avoid dependency conflicts
#   - This approach resolves rich & opentelemetry version incompatibilities
#
# Usage:
#   ./start-server.sh          # Normal start (builds if needed)
#   ./start-server.sh --rebuild # Force rebuild from scratch

set -e  # Exit on error

FORCE_REBUILD=false

# Parse arguments
if [ "$1" == "--rebuild" ] || [ "$1" == "-r" ]; then
    FORCE_REBUILD=true
fi

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

# Verify Dockerfile has the correct venv isolation setup
if ! grep -q "/opt/semgrep-venv" Dockerfile; then
    echo "❌ Error: Dockerfile is missing the venv isolation setup!"
    echo "   The Dockerfile should create a separate virtual environment for Semgrep."
    echo "   Please ensure you're using the correct version of the Dockerfile."
    exit 1
fi

echo "✅ Dockerfile verified (venv isolation enabled)"
echo ""

echo "📦 Starting Goberbot-Semgrep MCP Server..."
echo ""

# Force rebuild if requested
if [ "$FORCE_REBUILD" = true ]; then
    echo "🔨 Force rebuild requested - cleaning and rebuilding..."
    echo ""
    docker-compose down 2>/dev/null || true
    docker-compose build --no-cache
    echo ""
    echo "✅ Fresh build completed!"
    echo ""
# Check if image exists (first time setup)
elif ! docker images | grep -q "mcp-server-goberbot-semgrep-mcp"; then
    echo "🏗️  First time setup detected - building Docker image..."
    echo "   This may take 2-5 minutes..."
    echo ""
    docker-compose build
    echo ""
    echo "✅ Image built successfully!"
    echo ""
fi

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
    # Start the server (will build if needed, but we already built above for first-time)
    echo "🚀 Starting server container..."
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
echo "   - Stop server:  ./stop-server.sh"
echo "   - Restart:      ./start-server.sh"
echo "   - Rebuild:      ./start-server.sh --rebuild"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

