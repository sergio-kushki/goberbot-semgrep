#!/usr/bin/env python3
"""
Custom Goberbot-Semgrep MCP Server
FastMCP 2.0 implementation with streamable HTTP transport
"""

import asyncio
import json
import logging
import os
from typing import Optional

from fastmcp import FastMCP

from semgrep_runner import SemgrepRunner, ScanResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("goberbot-semgrep-mcp-server")

# Initialize FastMCP server
mcp = FastMCP("goberbot-semgrep-mcp-server")

# Initialize Semgrep runner
semgrep = SemgrepRunner()


@mcp.tool()
async def scan_code(
    code: str,
    language: Optional[str] = None,
    rules_file: str = "security.yaml"
) -> dict:
    """
    Scan code for security vulnerabilities and code quality issues using Goberbot-Semgrep integration.
    
    Args:
        code: The code snippet to scan
        language: Programming language (e.g., 'javascript', 'python'). Auto-detected if not provided.
        rules_file: Which rules file to use: 'security.yaml', 'code-quality.yaml', or 'all'
    
    Returns:
        Dictionary with scan results including findings, scan time, and summary
    """
    logger.info(f"Scanning code with rules: {rules_file}")
    
    try:
        result: ScanResult = await semgrep.scan(
            code=code,
            language=language,
            rules_file=rules_file
        )
        
        return {
            "findings": result.findings,
            "scan_time_ms": result.scan_time_ms,
            "rules_used": result.rules_used,
            "summary": result.summary,
            "success": True
        }
    except Exception as e:
        logger.error(f"Scan failed: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "success": False
        }


@mcp.tool()
async def list_available_rules() -> dict:
    """
    List all available Goberbot rule files and their descriptions.
    
    Returns:
        Dictionary with list of available rules and their metadata
    """
    logger.info("Listing available rules")
    
    try:
        rules_info = await semgrep.get_rules_info()
        return {
            "success": True,
            "rules": rules_info
        }
    except Exception as e:
        logger.error(f"Failed to list rules: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "success": False
        }


@mcp.tool()
async def reload_rules() -> dict:
    """
    Reload Goberbot rules from the configured source (URL or local files).
    
    Returns:
        Dictionary with reload status and rules source
    """
    logger.info("Reloading rules")
    
    try:
        await semgrep.reload_rules()
        return {
            "success": True,
            "message": "Rules reloaded successfully",
            "rules_source": semgrep.rules_source
        }
    except Exception as e:
        logger.error(f"Failed to reload rules: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "success": False
        }


async def initialize_server():
    """Initialize Goberbot rules on server startup"""
    logger.info("Initializing Goberbot rules...")
    await semgrep.initialize()
    logger.info(f"Rules initialized from: {semgrep.rules_source}")


def main():
    """Start the MCP server"""
    host = os.getenv("MCP_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_PORT", "8000"))
    
    logger.info("=" * 60)
    logger.info("Goberbot-Semgrep MCP Server (FastMCP 2.3+)")
    logger.info("=" * 60)
    logger.info(f"Host: {host}:{port}")
    logger.info(f"Path: /mcp")
    logger.info(f"Transport: streamable-http (native FastMCP)")
    logger.info(f"Tools: scan_code, list_available_rules, reload_rules")
    logger.info("=" * 60)
    
    # Initialize rules before starting server
    asyncio.run(initialize_server())
    
    # Use FastMCP's native streamable-http transport
    # This is the correct way according to FastMCP 2.3+ documentation
    logger.info("Starting FastMCP with native streamable-http transport...")
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        path="/mcp"  # MCP protocol endpoints will be at /mcp
    )


if __name__ == "__main__":
    main()
