#!/usr/bin/env python3
"""
Federation Commander MCP Server
Main entry point for the MCP server
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from federation_commander.tools import (
    RunTool, FileTool, EditTool, FindTool, GitTool,
    WatchTool, TaskTool, MemoryTool, ConfigTool, ProcessTool
)
from federation_commander.utils.config import Config
from federation_commander.utils.federation import FederationContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FederationCommanderServer:
    """Main server class for Federation Commander MCP"""
    
    def __init__(self):
        self.server = Server("federation-commander")
        self.config = Config()
        self.context = FederationContext()
        
        # Initialize tools with fc_ prefix for clarity
        self.tools = {
            'fc_run': RunTool(self.config, self.context),
            'fc_file': FileTool(self.config, self.context),
            'fc_edit': EditTool(self.config, self.context),
            'fc_find': FindTool(self.config, self.context),
            'fc_git': GitTool(self.config, self.context),
            'fc_watch': WatchTool(self.config, self.context),
            'fc_task': TaskTool(self.config, self.context),
            'fc_memory': MemoryTool(self.config, self.context),
            'fc_config': ConfigTool(self.config, self.context),
            'fc_ps': ProcessTool(self.config, self.context),
        }
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register all MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available tools"""
            tools = []
            for name, tool in self.tools.items():
                tools.append(types.Tool(
                    name=name,
                    description=tool.description,
                    inputSchema=tool.input_schema
                ))
            return tools
        
        @self.server.call_tool()
        async def handle_call_tool(
            name: str,
            arguments: Optional[Dict[str, Any]] = None
        ) -> List[types.TextContent]:
            """Handle tool execution"""
            if name not in self.tools:
                raise ValueError(f"Unknown tool: {name}")
            
            tool = self.tools[name]
            result = await tool.execute(arguments or {})
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
            )]
    
    async def run(self):
        """Run the server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Federation Commander MCP starting...")
            
            # Run server with initialization options
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="federation-commander",
                    server_version="1.0.0",
                    capabilities=types.ServerCapabilities(
                        tools=types.ToolsCapability()
                    )
                )
            )

def main():
    """Main entry point"""
    try:
        server = FederationCommanderServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()