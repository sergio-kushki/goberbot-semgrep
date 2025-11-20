#!/bin/bash
# Quick start script for Semgrep MCP Server

set -e

echo "🚀 Starting Semgrep MCP Server..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "   Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ docker-compose is not available!"
    echo "   Please install docker-compose or use Docker with Compose V2"
    exit 1
fi

cd "$(dirname "$0")"

echo "📦 Building Docker image..."
$COMPOSE_CMD build

echo ""
echo "🏃 Starting server..."
$COMPOSE_CMD up -d

echo ""
echo "⏳ Waiting for server to be ready..."
sleep 3

# Check if server is healthy
MAX_RETRIES=10
RETRY_COUNT=0
SERVER_URL="http://localhost:8000"

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s -f "${SERVER_URL}/health" > /dev/null 2>&1; then
        echo "✅ Server is healthy and ready!"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Waiting... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Server failed to start!"
    echo ""
    echo "Checking logs:"
    $COMPOSE_CMD logs --tail=50
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Semgrep MCP Server is running!"
echo "======================================"
echo ""
echo "🔗 Server URL: ${SERVER_URL}"
echo ""
echo "📝 To add to Cursor IDE, edit ~/.cursor/mcp.json:"
echo ""
echo '{
  "mcpServers": {
    "semgrep_custom": {
      "type": "streamable-http",
      "url": "http://localhost:8000"
    }
  }
}'
echo ""
echo "📊 Useful commands:"
echo "  - View logs:     $COMPOSE_CMD logs -f"
echo "  - Stop server:   $COMPOSE_CMD down"
echo "  - Restart:       $COMPOSE_CMD restart"
echo "  - Run tests:     ./test-server.sh"
echo ""

