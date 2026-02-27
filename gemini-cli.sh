#!/bin/bash
# Gemini CLI Wrapper Script
# Provides easy access to Gemini CLI from project root

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CLI_SCRIPT="$SCRIPT_DIR/backend/cli/gemini_cli.py"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "Activating virtual environment..."
        source "$SCRIPT_DIR/venv/bin/activate"
    fi
fi

# Run the CLI
python3 "$CLI_SCRIPT" "$@"
