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
    rules_file: str = "all"
) -> dict:
    """
    Scan source code for security vulnerabilities, code quality issues, and best practice violations using custom Semgrep rules.
    
    Use this tool to analyze any code snippet for common security flaws like SQL injection, XSS, hardcoded credentials, 
    weak cryptography (MD5), dangerous functions (eval), and code quality issues like console.log statements, 
    TODO comments, magic numbers, and empty catch blocks.
    
    The tool supports JavaScript, TypeScript, Python, Java, Go, and Rust. It will automatically detect the language 
    if not specified. Results include detailed findings with line numbers, severity levels (ERROR/WARNING/INFO), 
    CWE classifications for security issues, and actionable remediation guidance.
    
    Args:
        code: The complete source code to analyze. Can be a function, class, file, or multi-file snippet.
              The code will be written to a temporary file and scanned using Semgrep CLI.
        
        language: (Optional) Programming language identifier. Supported values: 'javascript', 'typescript', 'python', 
                  'java', 'go', 'rust', 'js', 'ts', 'py'. If omitted, Semgrep will attempt auto-detection based on 
                  syntax patterns. Providing the language improves accuracy and scan speed.
        
        rules_file: Which rule set to apply. Options:
                    - 'all' (default): Scan with both security and code-quality rules (recommended for comprehensive analysis)
                    - 'security.yaml': Only security rules (use when focusing on vulnerabilities like injection, XSS, crypto issues)
                    - 'code-quality.yaml': Only code quality rules (use for style checks, TODOs, console statements)
    
    Returns:
        Dictionary containing:
        - findings: List of detected issues with rule_id, message, severity, line/column, code_snippet, CWE mapping
        - summary: Count of findings by severity (ERROR, WARNING, INFO, total)
        - scan_time_ms: Execution time in milliseconds
        - rules_used: Path to the rule files that were applied
        - success: Boolean indicating if scan completed without errors
        
    Example use cases:
    - "Scan this JavaScript function for security issues"
    - "Check if this Python code has any vulnerabilities"
    - "Analyze this file for code quality problems"
    - "Review this code snippet for best practices violations"
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
    List all available Semgrep rules with detailed metadata including descriptions, severity levels, 
    supported languages, CWE classifications, and categorization.
    
    Use this tool to discover what security vulnerabilities and code quality issues can be detected.
    Each rule includes its ID, human-readable description, severity level (ERROR/WARNING/INFO), 
    supported programming languages, and security metadata like CWE identifiers. This is essential 
    for understanding scan capabilities, explaining what issues were found, or deciding which 
    rules_file parameter to use with scan_code.
    
    The server loads rules from three possible sources (in priority order):
    1. External URL (if CUSTOM_RULES_URL environment variable is set) - for centralized rule management
    2. Bundled rules in the Docker container (/app/custom-rules/) - default, always available
    3. AWS S3 bucket (if configured) - for enterprise deployments
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if the operation succeeded
        - rules_files: List of rule file objects, each containing:
          - file: Filename (e.g., 'security.yaml', 'code-quality.yaml')
          - path: Absolute filesystem path
          - source: Source location (e.g., 'bundled:/app/custom-rules', 'url:https://...')
          - rule_count: Number of rules in this file
          - rules: Array of individual rule objects with:
            - id: Unique rule identifier (e.g., 'dangerous-eval-usage')
            - message: Human-readable description of what the rule detects
            - severity: ERROR (critical security issues), WARNING (important issues), or INFO (suggestions)
            - languages: Array of supported languages (e.g., ['javascript', 'typescript', 'python'])
            - cwe: CWE identifier if this is a security rule (e.g., 'CWE-95: Code Injection')
            - category: Rule category (e.g., 'security', 'code-quality')
            - confidence: Detection confidence level (e.g., 'HIGH', 'MEDIUM')
        - summary: Aggregate statistics including:
          - total_rules: Total number of rules across all files
          - total_files: Number of rule files loaded
          - by_severity: Count of rules by severity level (ERROR, WARNING, INFO)
          - by_category: Count of rules by category (security, code-quality, etc.)
          - supported_languages: Array of all languages covered by the rule set
        
    Example use cases:
    - "What security vulnerabilities can Goberbot detect?"
    - "Show me all available Semgrep rules with descriptions"
    - "What programming languages are supported?"
    - "List rules by severity level"
    - "What CWE categories are covered?"
    - "How many code quality rules are there?"
    """
    logger.info("Listing available rules")
    
    try:
        rules_info = await semgrep.get_rules_info()
        
        # Build summary statistics
        total_rules = sum(file_info.get('rule_count', 0) for file_info in rules_info)
        
        # Count by severity and category
        severity_counts = {'ERROR': 0, 'WARNING': 0, 'INFO': 0}
        category_counts = {}
        languages_set = set()
        
        for file_info in rules_info:
            for rule in file_info.get('rules', []):
                # Count severity
                severity = rule.get('severity', 'INFO')
                if severity in severity_counts:
                    severity_counts[severity] += 1
                
                # Count category
                category = rule.get('category', 'unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
                
                # Collect languages
                for lang in rule.get('languages', []):
                    languages_set.add(lang)
        
        return {
            "success": True,
            "rules_files": rules_info,
            "summary": {
                "total_rules": total_rules,
                "total_files": len(rules_info),
                "by_severity": severity_counts,
                "by_category": category_counts,
                "supported_languages": sorted(list(languages_set))
            }
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
    Reload Semgrep rules from their configured source without restarting the server.
    
    Use this tool to refresh rule definitions after they've been updated externally. This is particularly useful 
    when rules are hosted at a remote URL or S3 bucket and have been modified. The reload fetches the latest 
    version and applies them to subsequent scans immediately.
    
    The reload process attempts to fetch rules from these sources in order:
    1. CUSTOM_RULES_URL environment variable (if set) - typically a GitHub raw URL or internal rule repository
    2. Bundled rules in /app/custom-rules/ - the default fallback included in the Docker image
    3. AWS S3 bucket (if AWS credentials and bucket are configured)
    
    After reload, use list_available_rules() to verify the updated rules are loaded correctly.
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating if reload completed successfully
        - message: Human-readable status message (e.g., "Rules reloaded successfully")
        - rules_source: String describing where rules were loaded from (e.g., 'bundled:/app/custom-rules', 'url:https://...')
        - error: (only if success=false) Error message describing what went wrong
    
    Example use cases:
    - "Reload the Semgrep rules" (after updating rules in GitHub/S3)
    - "Refresh security rules"
    - "Update scan rules from the repository"
    - "Fetch latest rule definitions"
    
    Note: This operation typically completes in under 2 seconds for remote URLs, instantly for bundled rules.
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
