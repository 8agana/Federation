#!/usr/bin/env python3
"""Simple Federation Code MCP server for testing."""

import sys
import os
import asyncio
import logging

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("federation_code_simple")

# Create server
server = Server("federation-code")

@server.list_tools()
async def list_tools() -> types.ListToolsResult:
    """List available tools."""
    return types.ListToolsResult(tools=[
        types.Tool(
            name="fc_analyze",
            description="Analyze code for issues (simplified version)",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {"type": "string", "description": "File to analyze"},
                    "mode": {"type": "string", "enum": ["quick"], "default": "quick"}
                },
                "required": ["files"]
            }
        ),
        types.Tool(
            name="fc_status", 
            description="Check status (placeholder)",
            inputSchema={
                "type": "object",
                "properties": {
                    "handle": {"type": "string", "description": "Operation handle"}
                },
                "required": ["handle"]
            }
        )
    ])

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> types.CallToolResult:
    """Execute a tool."""
    try:
        if name == "fc_analyze":
            files = arguments.get("files", "")
            mode = arguments.get("mode", "quick")
            
            # Simple mock analysis
            result = {
                "status": "success",
                "summary": {"total_issues": 2, "files_analyzed": 1},
                "issues": [
                    {
                        "id": "demo_1",
                        "file": files,
                        "line": 1,
                        "severity": "warning",
                        "message": "Demo issue 1",
                        "type": "style"
                    },
                    {
                        "id": "demo_2", 
                        "file": files,
                        "line": 5,
                        "severity": "info",
                        "message": "Demo issue 2",
                        "type": "suggestion"
                    }
                ],
                "execution_time": 0.1,
                "mode": mode
            }
            
            import json
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        elif name == "fc_status":
            handle = arguments.get("handle", "")
            result = {
                "handle": handle,
                "status": "completed",
                "progress": 100,
                "message": "Demo status check"
            }
            
            import json
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=json.dumps(result, indent=2))]
            )
            
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )

async def main():
    """Main entry point."""
    try:
        logger.info("Starting Federation Code MCP Server (Simple)")
        
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="federation-code",
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

if __name__ == "__main__":
    asyncio.run(main())