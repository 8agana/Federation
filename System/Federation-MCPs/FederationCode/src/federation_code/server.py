"""Federation Code MCP Server - Main entry point."""

import asyncio
import logging
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
    ListToolsResult
)

from federation_code.core import AsyncEngine
from federation_code.tools import AnalyzeTool, StatusTool, GetTool, CancelTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FederationCodeServer:
    """Main MCP server for Federation Code."""
    
    def __init__(self):
        self.server = Server("federation-code")
        self.engine = AsyncEngine()
        self.tools = {}
        
        # Initialize tools
        self._register_tools()
        
        # Register handlers
        self._register_handlers()
        
    def _register_tools(self):
        """Register all available tools."""
        self.tools = {
            "fc_analyze": AnalyzeTool(self.engine),
            "fc_status": StatusTool(self.engine),
            "fc_get": GetTool(self.engine),
            "fc_cancel": CancelTool(self.engine)
        }
        
        logger.info(f"Registered {len(self.tools)} tools: {list(self.tools.keys())}")
        
    def _register_handlers(self):
        """Register MCP protocol handlers."""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            """List available tools."""
            tools = []
            
            for tool_name, tool_impl in self.tools.items():
                tools.append(Tool(
                    name=tool_name,
                    description=tool_impl.description,
                    inputSchema=tool_impl.get_schema()
                ))
                
            return ListToolsResult(tools=tools)
            
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any] | None) -> CallToolResult:
            """Execute a tool."""
            try:
                if name not in self.tools:
                    raise ValueError(f"Unknown tool: {name}")
                    
                tool = self.tools[name]
                arguments = arguments or {}
                
                logger.info(f"Executing tool {name} with args: {arguments}")
                
                # Execute tool
                result = await tool.execute(arguments)
                
                # Convert to MCP format
                content = []
                for item in result.content:
                    if item.get("type") == "text":
                        content.append(TextContent(type="text", text=item["text"]))
                        
                return CallToolResult(
                    content=content,
                    isError=result.isError
                )
                
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True
                )
                
    async def start(self):
        """Start the server and async engine."""
        logger.info("Starting Federation Code MCP Server")
        await self.engine.start()
        logger.info("AsyncEngine started")
        
    async def stop(self):
        """Stop the server and cleanup."""
        logger.info("Stopping Federation Code MCP Server")
        await self.engine.stop()
        logger.info("AsyncEngine stopped")
        
    async def run(self):
        """Run the server with stdio transport."""
        try:
            await self.start()
            
            # Run server with stdio transport
            async with stdio_server() as streams:
                await self.server.run(*streams)
                
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.stop()


async def main():
    """Main entry point."""
    server = FederationCodeServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())