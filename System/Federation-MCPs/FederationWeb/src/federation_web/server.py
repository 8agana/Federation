"""
FederationWeb MCP Server
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the src directory to Python path for imports
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from federation_web.utils.config import Config
from federation_web.core.context import FederationContext
from federation_web.tools.research import ResearchTool
from federation_web.tools.interests import InterestsTool

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FederationWebServer:
    """MCP server for FederationWeb tools"""
    
    def __init__(self):
        self.server = Server("federation-web")
        self.config = Config()
        self.context = FederationContext(self.config)
        
        # Initialize tools
        self.research_tool = ResearchTool(self.config, self.context)
        self.interests_tool = InterestsTool(self.config, self.context)
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="fw_research",
                    description="Work-focused web research with ReAct orchestration. Features multi-provider search, content extraction, smart chunking, and auto-memorization.",
                    inputSchema=self.research_tool.get_schema()
                ),
                types.Tool(
                    name="fw_interests",
                    description="Exploration and discovery tool for intellectual curiosity. Features multiple modes (explore, connections, surprise_me, visual), mood-based browsing, and SharedVault integration.",
                    inputSchema=self.interests_tool.get_schema()
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: dict | None
        ) -> List[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """Execute tool and return results"""
            
            if arguments is None:
                arguments = {}
                
            try:
                if name == "fw_research":
                    result = await self.research_tool.execute(arguments)
                elif name == "fw_interests":
                    result = await self.interests_tool.execute(arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                # Convert result to MCP response
                return [types.TextContent(
                    type="text",
                    text=self._format_result(result)
                )]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                error_result = {
                    "status": "error",
                    "error": str(e),
                    "tool": name
                }
                return [types.TextContent(
                    type="text",
                    text=self._format_result(error_result)
                )]
    
    def _format_result(self, result: Dict[str, Any]) -> str:
        """Format result for display"""
        import json
        
        # For now, return JSON. Could format as markdown later.
        return json.dumps(result, indent=2, default=str)
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting FederationWeb MCP server...")
        
        # Run server with stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="federation-web",
                    server_version="1.0.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability()
                    )
                )
            )

def main():
    """Main entry point"""
    try:
        server = FederationWebServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()