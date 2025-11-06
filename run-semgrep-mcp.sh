#!/bin/bash
# Wrapper script to run semgrep-mcp with venv activated

cd /Users/sergio.arancibia/CursorProjects/goberbot-semgrep
source venv/bin/activate
exec semgrep-mcp "$@"

