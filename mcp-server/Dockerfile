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

# Install FastMCP and dependencies in the main Python environment
RUN pip install --no-cache-dir -r requirements.txt

# Create a separate virtual environment for Semgrep to avoid dependency conflicts
RUN python -m venv /opt/semgrep-venv && \
    /opt/semgrep-venv/bin/pip install --no-cache-dir 'semgrep>=1.135.0'

# Create wrapper script to call Semgrep from its isolated venv
RUN echo '#!/bin/bash\nexec /opt/semgrep-venv/bin/semgrep "$@"' > /usr/local/bin/semgrep && \
    chmod +x /usr/local/bin/semgrep

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
# Semgrep telemetry/metrics settings
ENV SEMGREP_SEND_METRICS=off
ENV SEMGREP_ENABLE_VERSION_CHECK=false

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run server
CMD ["python", "server.py"]

