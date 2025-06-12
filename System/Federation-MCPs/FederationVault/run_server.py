#!/usr/bin/env python3
"""
FederationVault MCP Server Runner
Wrapper script to run the FederationVault MCP server
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the server
from federation_vault_mcp import main
import asyncio

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())