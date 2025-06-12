#!/bin/bash

# Federation Code MCP Installation Script

set -e

echo "🚀 Installing Federation Code MCP..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python 3.10+ is required, found $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "📦 Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ Poetry found"

# Install dependencies
echo "📦 Installing dependencies..."
poetry install

# Build the package
echo "🔨 Building package..."
poetry build

# Install in development mode
echo "🔧 Installing in development mode..."
poetry install

echo "✅ Federation Code MCP installed successfully!"

# Check if MCP config directory exists
MCP_CONFIG_DIR="$HOME/.config/mcp"
if [ ! -d "$MCP_CONFIG_DIR" ]; then
    echo "📁 Creating MCP config directory..."
    mkdir -p "$MCP_CONFIG_DIR"
fi

# Generate MCP server configuration
CONFIG_FILE="$MCP_CONFIG_DIR/federation-code.json"
cat > "$CONFIG_FILE" << EOF
{
  "federation-code": {
    "command": "poetry",
    "args": ["run", "federation-code"],
    "cwd": "$(pwd)",
    "env": {
      "PYTHONPATH": "$(pwd)/src"
    }
  }
}
EOF

echo "✅ MCP configuration written to $CONFIG_FILE"

# Test the installation
echo "🧪 Testing installation..."
if poetry run python -c "from federation_code import FederationCodeServer; print('✅ Import successful')"; then
    echo "✅ Installation test passed"
else
    echo "❌ Installation test failed"
    exit 1
fi

echo ""
echo "🎉 Federation Code MCP is ready!"
echo ""
echo "Next steps:"
echo "1. Add the server to your MCP client configuration"
echo "2. Use the generated config at: $CONFIG_FILE"
echo "3. Start using the fc_analyze, fc_status, fc_get, and fc_cancel tools"
echo ""
echo "Example configuration for Claude Desktop (~/.claude/mcp_servers.json):"
echo "{"
echo '  "federation-code": {'
echo '    "command": "poetry",'
echo '    "args": ["run", "federation-code"],'
echo "    \"cwd\": \"$(pwd)\""
echo "  }"
echo "}"