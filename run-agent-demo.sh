#!/bin/bash
# Agent Demo Runner Script
# Runs the comprehensive agent integration demonstration

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEMO_SCRIPT="$SCRIPT_DIR/examples/agent_demo.py"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "Activating virtual environment..."
        source "$SCRIPT_DIR/venv/bin/activate"
    fi
fi

# Run the demo
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                 ANTIGRAVITY AGENT FRAMEWORK INTEGRATION DEMO                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Starting comprehensive agent integration demonstration..."
echo "This will showcase Jules, Gemini, and all agents working together flawlessly."
echo ""

python3 "$DEMO_SCRIPT"
