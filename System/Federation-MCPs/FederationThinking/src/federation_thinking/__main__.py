"""
Entry point for FederationThinking MCP server
"""
import asyncio
from federation_thinking.server import main

if __name__ == "__main__":
    asyncio.run(main())