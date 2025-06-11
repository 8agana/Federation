#!/bin/bash
# Install dependencies for DevTools MCP

echo "Installing DevTools MCP dependencies..."

# Install Python packages
pip3 install mcp docker PyGithub

echo "Dependencies installed!"
echo ""
echo "Don't forget to set your GitHub Personal Access Token:"
echo "export GITHUB_PERSONAL_ACCESS_TOKEN='your-token-here'"
echo ""
echo "Make sure Docker Desktop is running for Docker tools to work."