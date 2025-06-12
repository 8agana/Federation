#!/bin/bash

# FederationThinking MCP Installation Script
# Enhanced sequential thinking for the Federation

set -e

echo "🧠 Installing FederationThinking MCP..."

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create virtual environment if it doesn't exist
if [ ! -d "$DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$DIR/venv"
fi

# Activate virtual environment
source "$DIR/venv/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Create necessary directories
echo "Creating directories..."
mkdir -p ~/.federation/thinking_sessions
mkdir -p ~/Documents/Federation/Output/Thinking/Visualizations

# Initialize ChromaDB if needed
echo "Initializing memory system..."
python3 -c "
from src.federation_thinking.config import Config
from src.federation_thinking.memory import ThinkingMemory

config = Config()
memory = ThinkingMemory(config)
print('Memory system initialized successfully')
"

echo "✅ FederationThinking MCP installed successfully!"
echo ""
echo "Next steps:"
echo "1. Add to your Claude Desktop config:"
echo "   \"federation-thinking\": {"
echo "     \"command\": \"$DIR/venv/bin/python\","
echo "     \"args\": [\"$DIR/src/federation_thinking/server.py\"],"
echo "     \"env\": {"
echo "       \"PYTHONPATH\": \"$DIR/src\","
echo "       \"PYTHONUNBUFFERED\": \"1\""
echo "     }"
echo "   }"
echo ""
echo "2. Restart Claude Desktop"
echo "3. Use ft_think, ft_session, and ft_visualize tools"