#!/usr/bin/env python3
"""
Run the DT Nerve Center MCP server
"""
import sys
import asyncio
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the server
from dt_nerve_center_mcp import main

if __name__ == "__main__":
    asyncio.run(main())