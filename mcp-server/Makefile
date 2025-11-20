.PHONY: help build start stop restart logs test clean

help:
	@echo "Semgrep MCP Server - Available Commands:"
	@echo ""
	@echo "  make build    - Build Docker image"
	@echo "  make start    - Start server"
	@echo "  make stop     - Stop server"
	@echo "  make restart  - Restart server"
	@echo "  make logs     - View server logs"
	@echo "  make test     - Run tests against server"
	@echo "  make clean    - Clean up containers and images"
	@echo ""

build:
	@echo "📦 Building Docker image..."
	docker-compose build

start:
	@echo "🚀 Starting Semgrep MCP Server..."
	docker-compose up -d
	@echo "⏳ Waiting for server to be ready..."
	@sleep 3
	@echo "✅ Server started at http://localhost:8000"

stop:
	@echo "🛑 Stopping server..."
	docker-compose down

restart:
	@echo "🔄 Restarting server..."
	docker-compose restart

logs:
	docker-compose logs -f

test:
	@echo "🧪 Running tests..."
	@./test-server.sh

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker rmi semgrep-mcp-server || true

