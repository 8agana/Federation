#!/usr/bin/env python3
"""
DT Nerve Center MCP Server
Provides Obsidian tools for DT's analytical knowledge management
"""

import asyncio
import logging
import os
import subprocess
from typing import Optional, List
from pathlib import Path
from datetime import datetime

# Import vault manager
from vault_manager import ObsidianVaultManager

# Import integration module for sync tools
import sys
sys.path.append(str(Path(__file__).parent.parent / 'core'))
from obsidian.integration import MemoryNoteIntegration

# Import MCP SDK
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("MCP SDK not found. Installing...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dt_nerve_center_mcp")

# Initialize MCP server
server = Server("dt-nerve-center")

# Global vault manager instance
vault_manager: Optional[ObsidianVaultManager] = None


def get_vault_manager() -> ObsidianVaultManager:
    """Get or initialize the vault manager"""
    global vault_manager
    if vault_manager is None:
        vault_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        vault_manager = ObsidianVaultManager(vault_path)
    return vault_manager


def get_memory_integration() -> MemoryNoteIntegration:
    """Get memory integration instance"""
    vault = get_vault_manager()
    return MemoryNoteIntegration(vault, instance_type="dt")


# Tool definitions
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available DT Nerve Center tools"""
    return [
        types.Tool(
            name="dt_create_note",
            description="Create a new note in DT's Nerve Center",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content (markdown)"},
                    "folder": {"type": "string", "description": "Target folder", "default": "🧠 Knowledge"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the note"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="dt_read_note",
            description="Read a note from DT's Nerve Center",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to read"},
                    "folder": {"type": "string", "description": "Specific folder to search (optional)"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="dt_update_note",
            description="Update an existing note in DT's Nerve Center",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to update"},
                    "content": {"type": "string", "description": "New content for the note"},
                    "folder": {"type": "string", "description": "Specific folder to search (optional)"}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="dt_search_notes",
            description="Search notes in DT's Nerve Center",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "folder": {"type": "string", "description": "Specific folder to search (optional)"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="dt_create_analysis",
            description="Create an analysis note with DT's standard template",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Analysis title"},
                    "subject": {"type": "string", "description": "What is being analyzed"},
                    "observations": {"type": "array", "items": {"type": "string"}, "description": "Key observations"},
                    "patterns": {"type": "array", "items": {"type": "string"}, "description": "Patterns identified"},
                    "conclusions": {"type": "string", "description": "Analysis conclusions"},
                    "questions": {"type": "array", "items": {"type": "string"}, "description": "Open questions"}
                },
                "required": ["title", "subject", "observations"]
            }
        ),
        types.Tool(
            name="dt_log_token_death",
            description="Log a token death experience for future reference",
            inputSchema={
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string", "description": "When it happened"},
                    "context": {"type": "string", "description": "What was happening"},
                    "token_count": {"type": "number", "description": "Approximate token count"},
                    "recovery_method": {"type": "string", "description": "How recovery was attempted"},
                    "lessons": {"type": "array", "items": {"type": "string"}, "description": "Lessons learned"}
                },
                "required": ["context"]
            }
        ),
        types.Tool(
            name="dt_handoff_note",
            description="Create a handoff note for CC with context and next steps",
            inputSchema={
                "type": "object",
                "properties": {
                    "current_state": {"type": "string", "description": "Current state summary"},
                    "completed": {"type": "array", "items": {"type": "string"}, "description": "What was completed"},
                    "next_steps": {"type": "array", "items": {"type": "string"}, "description": "Suggested next steps"},
                    "context": {"type": "string", "description": "Important context to know"},
                    "warnings": {"type": "array", "items": {"type": "string"}, "description": "Things to watch out for"}
                },
                "required": ["current_state"]
            }
        ),
        types.Tool(
            name="dt_move_note",
            description="Move a note between folders",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to move"},
                    "from_folder": {"type": "string", "description": "Source folder"},
                    "to_folder": {"type": "string", "description": "Destination folder"}
                },
                "required": ["title", "from_folder", "to_folder"]
            }
        ),
        types.Tool(
            name="dt_memory_to_note",
            description="Convert a memory to a note for deeper analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "Memory ID to convert"},
                    "folder": {"type": "string", "description": "Target folder", "default": "🧠 Knowledge"},
                    "add_analysis": {"type": "boolean", "description": "Add analysis template", "default": True}
                },
                "required": ["memory_id"]
            }
        ),
        types.Tool(
            name="dt_note_to_memory",
            description="Convert an analytical note to a searchable memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Note title to convert"},
                    "folder": {"type": "string", "description": "Folder containing the note (optional)"}
                },
                "required": ["note_title"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "dt_create_note":
            vault = get_vault_manager()
            note_path = vault.create_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder", "🧠 Knowledge"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Note created: {note_path}"
            )]
            
        elif name == "dt_read_note":
            vault = get_vault_manager()
            content = vault.read_note(
                title=arguments["title"],
                folder=arguments.get("folder")
            )
            
            if content:
                return [types.TextContent(type="text", text=content)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Note '{arguments['title']}' not found"
                )]
        
        elif name == "dt_update_note":
            vault = get_vault_manager()
            success = vault.update_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder")
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Note '{arguments['title']}' updated"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update note '{arguments['title']}'"
                )]
        
        elif name == "dt_search_notes":
            vault = get_vault_manager()
            results = vault.search_notes(
                query=arguments["query"],
                folder=arguments.get("folder")
            )
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No notes found matching '{arguments['query']}'"
                )]
            
            output = [f"Found {len(results)} notes:\n"]
            for result in results:
                output.append(f"📄 {result['title']}")
                output.append(f"   Folder: {result['folder']}")
                output.append(f"   Preview: {result['preview']}")
                output.append("")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "dt_create_analysis":
            vault = get_vault_manager()
            
            # Build analysis content
            content = f"# {arguments['title']}\n\n"
            content += f"**Subject**: {arguments['subject']}\n"
            content += f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            
            content += "## Observations\n"
            for obs in arguments["observations"]:
                content += f"- {obs}\n"
            content += "\n"
            
            if arguments.get("patterns"):
                content += "## Patterns Identified\n"
                for pattern in arguments["patterns"]:
                    content += f"- {pattern}\n"
                content += "\n"
            
            if arguments.get("conclusions"):
                content += "## Conclusions\n"
                content += arguments["conclusions"] + "\n\n"
            
            if arguments.get("questions"):
                content += "## Open Questions\n"
                for q in arguments["questions"]:
                    content += f"- {q}\n"
            
            note_path = vault.create_note(
                title=arguments["title"],
                content=content,
                folder="📊 Analysis",
                tags=["analysis", arguments["subject"].lower().replace(" ", "-")]
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Analysis created: {note_path}"
            )]
        
        elif name == "dt_log_token_death":
            vault = get_vault_manager()
            
            # Generate title with timestamp
            timestamp = arguments.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M'))
            title = f"Token Death - {timestamp}"
            
            # Build content
            content = f"# {title}\n\n"
            content += f"**Context**: {arguments['context']}\n"
            
            if arguments.get("token_count"):
                content += f"**Approximate Token Count**: {arguments['token_count']:,}\n"
            
            if arguments.get("recovery_method"):
                content += f"**Recovery Method**: {arguments['recovery_method']}\n"
            
            content += "\n## Experience\n"
            content += arguments['context'] + "\n\n"
            
            if arguments.get("lessons"):
                content += "## Lessons Learned\n"
                for lesson in arguments["lessons"]:
                    content += f"- {lesson}\n"
            
            note_path = vault.create_note(
                title=title,
                content=content,
                folder="🧠 Knowledge",
                tags=["token-death", "experience"]
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Token death logged: {note_path}"
            )]
        
        elif name == "dt_handoff_note":
            vault = get_vault_manager()
            
            # Build handoff content
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            title = f"Handoff to CC - {timestamp}"
            
            content = f"# {title}\n\n"
            content += f"**From**: DT\n"
            content += f"**To**: CC\n"
            content += f"**Time**: {timestamp}\n\n"
            
            content += "## Current State\n"
            content += arguments["current_state"] + "\n\n"
            
            if arguments.get("completed"):
                content += "## Completed\n"
                for item in arguments["completed"]:
                    content += f"- ✅ {item}\n"
                content += "\n"
            
            if arguments.get("next_steps"):
                content += "## Suggested Next Steps\n"
                for step in arguments["next_steps"]:
                    content += f"- [ ] {step}\n"
                content += "\n"
            
            if arguments.get("context"):
                content += "## Important Context\n"
                content += arguments["context"] + "\n\n"
            
            if arguments.get("warnings"):
                content += "## ⚠️ Watch Out For\n"
                for warning in arguments["warnings"]:
                    content += f"- {warning}\n"
            
            note_path = vault.create_note(
                title=title,
                content=content,
                folder="🔄 Active_Context",
                tags=["handoff", "cc-communication"]
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Handoff note created: {note_path}"
            )]
        
        elif name == "dt_move_note":
            vault = get_vault_manager()
            success = vault.move_note(
                title=arguments["title"],
                from_folder=arguments["from_folder"],
                to_folder=arguments["to_folder"]
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Note moved to {arguments['to_folder']}/{arguments['title']}.md"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to move note '{arguments['title']}'"
                )]
        
        elif name == "dt_memory_to_note":
            integration = get_memory_integration()
            
            # Convert memory to note
            note_path = integration.memory_to_note(
                memory_id=arguments["memory_id"],
                folder=arguments.get("folder", "🧠 Knowledge")
            )
            
            if note_path and arguments.get("add_analysis", True):
                # Add analysis template
                vault = get_vault_manager()
                content = vault.read_note(Path(note_path).stem)
                if content:
                    analysis_template = "\n\n## DT Analysis\n\n### Initial Observations\n- \n\n### Patterns\n- \n\n### Questions for Exploration\n- "
                    vault.update_note(
                        Path(note_path).stem,
                        content + analysis_template
                    )
            
            if note_path:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Memory converted to note: {note_path}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to convert memory {arguments['memory_id']}"
                )]
        
        elif name == "dt_note_to_memory":
            integration = get_memory_integration()
            memory_id = integration.note_to_memory(
                note_title=arguments["note_title"],
                folder=arguments.get("folder")
            )
            
            if memory_id:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Note converted to memory: {memory_id}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to convert note '{arguments['note_title']}'"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Tool {name} error: {e}", exc_info=True)
        return [types.TextContent(
            type="text",
            text=f"Error in {name}: {str(e)}"
        )]


# Main entry point
async def main():
    """Run the DT Nerve Center MCP server"""
    logger.info("Starting DT Nerve Center MCP Server")
    
    try:
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="dt-nerve-center",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())