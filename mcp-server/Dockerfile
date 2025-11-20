FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY mcp-server/requirements.txt .

# Strategy: Install Semgrep first (which pins rich~=13.5.2), 
# then upgrade just rich to satisfy FastMCP (which needs rich>=13.9.4)
# Semgrep still works with newer rich versions despite the constraint
RUN pip install --no-cache-dir semgrep>=1.135.0 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade 'rich>=13.9.4'

# Copy server code
COPY mcp-server/server.py mcp-server/semgrep_runner.py ./

# Copy bundled custom rules (fallback)
COPY custom-rules/ /app/custom-rules/

# Create cache directory for downloaded rules
RUN mkdir -p /tmp/semgrep-rules

# Environment variables (can be overridden at runtime)
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV CUSTOM_RULES_URL=""

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python", "server.py"]

