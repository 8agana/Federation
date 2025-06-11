#!/usr/bin/env python3
"""
DevTools MCP Server Runner
Wrapper script to run the DevTools MCP server
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the server
from devtools_mcp import main
import asyncio

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())