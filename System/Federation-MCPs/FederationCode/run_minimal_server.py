#!/usr/bin/env python3
"""Minimal Federation Code MCP server based on working patterns."""

import asyncio
import sys
import json
import logging
from typing import Dict, Any

# MCP imports - using the exact same pattern as working servers
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError as e:
    print(f"ERROR: MCP SDK not installed or incompatible version: {e}", file=sys.stderr)
    sys.exit(1)

# Configure logging exactly like working servers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("federation_code_minimal")

# Initialize MCP server
server = Server("federation-code-minimal")

@server.list_tools()
async def list_tools() -> types.ListToolsResult:
    """List available tools."""
    logger.info("Listing tools")
    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="fc_analyze",
                description="Analyze code for issues (demo version)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "string",
                            "description": "File to analyze"
                        }
                    },
                    "required": ["files"]
                }
            )
        ]
    )

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> types.CallToolResult:
    """Execute a tool."""
    logger.info(f"Calling tool: {name} with args: {arguments}")
    
    try:
        if name == "fc_analyze":
            files = arguments.get("files", "unknown")
            
            result = {
                "status": "success",
                "message": f"Analyzed {files}",
                "demo": True,
                "issues_found": 0
            }
            
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text", 
                        text=json.dumps(result, indent=2)
                    )
                ]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text", 
                    text=f"Error: {str(e)}"
                )
            ],
            isError=True
        )

async def main():
    """Run the Federation Code MCP server - minimal version."""
    logger.info("Starting Federation Code MCP Server (Minimal)")
    
    try:
        # Use the exact same pattern as working federation servers
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="federation-code-minimal",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        # Don't re-raise to avoid confusing Claude Desktop
        
if __name__ == "__main__":
    asyncio.run(main())