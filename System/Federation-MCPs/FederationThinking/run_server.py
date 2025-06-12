#!/usr/bin/env python3
"""
Entry point for Federation Thinking MCP server
Ensures proper module loading and import paths
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Import and run the server
if __name__ == "__main__":
    import asyncio
    from federation_thinking.server import main
    asyncio.run(main())