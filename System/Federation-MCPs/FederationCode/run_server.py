#!/usr/bin/env python3
"""
Federation Code MCP Server Runner
Wrapper script to run the Federation Code MCP server
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the server
from federation_code_mcp import main
import asyncio

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())