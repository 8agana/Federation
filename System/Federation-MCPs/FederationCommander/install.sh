#!/bin/bash
# Federation Commander MCP Installation Script

set -e

echo "🚀 Installing Federation Commander MCP..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📦 Installing Federation Commander..."
pip install -e "$SCRIPT_DIR"

# Create config directory
CONFIG_DIR="$HOME/.federation"
mkdir -p "$CONFIG_DIR"

# Create default config if it doesn't exist
CONFIG_FILE="$CONFIG_DIR/commander_config.json"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 Creating default configuration..."
    cat > "$CONFIG_FILE" << EOF
{
  "default_timeout": 30,
  "shell": "/bin/bash",
  "max_retries": 3,
  "max_file_size": 10485760,
  "excluded_patterns": [
    "*.pyc",
    "__pycache__",
    "node_modules",
    ".git",
    ".DS_Store",
    "*.swp",
    "*.swo",
    "*~"
  ],
  "preview_edits": true,
  "search_extensions": [
    ".py",
    ".js",
    ".ts",
    ".json",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".sh",
    ".tsx",
    ".jsx"
  ],
  "max_search_results": 50,
  "ripgrep_path": "rg",
  "auto_stage": true,
  "commit_template": "Federation update {timestamp}",
  "default_branch": "main",
  "federation_root": "/Users/samuelatagana/Documents/Federation",
  "memory_path": "/Users/samuelatagana/Documents/Federation/System/Memory",
  "task_path": "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault/📋 TaskTracker"
}
EOF
fi

# Get Claude config path
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"

# Check if Claude config exists
if [ ! -f "$CLAUDE_CONFIG" ]; then
    echo "⚠️  Claude config not found at: $CLAUDE_CONFIG"
    echo "   Please ensure Claude is installed and has been run at least once."
    exit 1
fi

# Create MCP configuration
echo ""
echo "📋 Add the following to your Claude configuration:"
echo "   Location: $CLAUDE_CONFIG"
echo ""
echo '  "federation-commander": {'
echo '    "command": "python",'
echo '    "args": ["'$SCRIPT_DIR'/src/federation_commander/server.py"],'
echo '    "env": {'
echo '      "PYTHONPATH": "'$SCRIPT_DIR'/src"'
echo '    }'
echo '  }'
echo ""
echo "Make sure to add it within the \"mcpServers\" section and include a comma if needed."
echo ""

# Test import
echo "🧪 Testing installation..."
if python -c "import federation_commander" 2>/dev/null; then
    echo "✅ Federation Commander installed successfully!"
else
    echo "❌ Installation test failed. Please check for errors above."
    exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Add the configuration above to your Claude config"
echo "2. Restart Claude"
echo "3. Federation Commander tools will be available in Claude"
echo ""
echo "Available tools:"
echo "  • run    - Execute commands"
echo "  • file   - File operations"
echo "  • edit   - Smart editing"
echo "  • find   - Search files/content"
echo "  • git    - Git operations"
echo "  • watch  - Monitor files"
echo "  • task   - Task management"
echo "  • memory - Memory storage"
echo "  • config - Configuration"
echo "  • ps     - Process management"