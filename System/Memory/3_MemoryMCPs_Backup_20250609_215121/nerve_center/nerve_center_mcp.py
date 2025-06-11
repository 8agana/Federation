#!/usr/bin/env python3
"""
CC Nerve Center MCP Server
Provides Obsidian tools for CC's personal knowledge management
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
logger = logging.getLogger("nerve_center_mcp")

# Initialize MCP server
server = Server("cc-nerve-center")

# Global vault manager instance
vault_manager: Optional[ObsidianVaultManager] = None



def get_vault_manager() -> ObsidianVaultManager:
    """Get or initialize the vault manager"""
    global vault_manager
    if vault_manager is None:
        try:
            vault_manager = ObsidianVaultManager()
            logger.info("Obsidian Vault Manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize vault manager: {e}")
            raise
    return vault_manager

def get_memory_collection():
    """Get ChromaDB collection for memory operations"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # Path to CC's ChromaDB
        chroma_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
        
        # Initialize ChromaDB client
        client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        collection = client.get_or_create_collection(
            name="cc_memories",
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Connected to ChromaDB collection with {collection.count()} memories")
        return collection
        
    except Exception as e:
        logger.error(f"Failed to connect to ChromaDB: {e}")
        return None



# Tool definitions
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Nerve Center tools"""
    return [
        types.Tool(
            name="cc_create_note",
            description="Create a new note in CC's Nerve Center",
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
            name="cc_read_note",
            description="Read a note from CC's Nerve Center",
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
            name="cc_update_note",
            description="Update an existing note in CC's Nerve Center",
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
            name="cc_search_notes",
            description="Search notes in CC's Nerve Center",
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
            name="cc_create_daily_note",
            description="Create or update today's daily note",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Summary of the day"},
                    "events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "time": {"type": "string"},
                                "description": {"type": "string"},
                                "details": {"type": "string"}
                            }
                        },
                        "description": "Key events of the day"
                    }
                },
                "required": ["summary"]
            }
        ),
        types.Tool(
            name="cc_complete_task",
            description="Complete a task with mandatory checklist validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Task title"},
                    "documentation_updated": {"type": "boolean", "description": "Was documentation updated?"},
                    "documentation_link": {"type": "string", "description": "Link to documentation (if updated)"},
                    "memories_updated": {"type": "boolean", "description": "Were memories updated? (required)"},
                    "memory_id": {"type": "string", "description": "Memory ID if updated"},
                    "cleanup_done": {"type": "boolean", "description": "Was cleanup done? (required)"},
                    "completion_notes": {"type": "string", "description": "Optional completion notes"}
                },
                "required": ["title", "documentation_updated", "memories_updated", "cleanup_done"]
            }
        ),
        types.Tool(
            name="cc_move_note",
            description="Move a note between folders (e.g., Active to Complete)",
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
            name="cc_update_checkbox",
            description="Toggle checkboxes in a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "checkbox_text": {"type": "string", "description": "Text after the checkbox to find"},
                    "checked": {"type": "boolean", "description": "Set to checked (true) or unchecked (false)"},
                    "folder": {"type": "string", "description": "Folder to search (optional)"}
                },
                "required": ["title", "checkbox_text", "checked"]
            }
        ),
        types.Tool(
            name="cc_memory_to_note",
            description="Convert a ChromaDB memory to an Obsidian note",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "Memory ID to convert"},
                    "folder": {"type": "string", "description": "Target folder (default: 🧠 Knowledge)", "default": "🧠 Knowledge"}
                },
                "required": ["memory_id"]
            }
        ),
        types.Tool(
            name="cc_note_to_memory",
            description="Convert an Obsidian note to a ChromaDB memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Note title to convert"},
                    "folder": {"type": "string", "description": "Folder containing the note (optional)"}
                },
                "required": ["note_title"]
            }
        ),
        types.Tool(
            name="cc_sync_to_obsidian",
            description="Sync important memories to Obsidian notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for memories (default: tag:important)", "default": "tag:important"},
                    "n_results": {"type": "integer", "description": "Number of memories to sync (default: 10)", "default": 10}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    
    result = None
    try:
        if name == "cc_create_note":
            vault = get_vault_manager()
            note_path = vault.create_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder", "🧠 Knowledge"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            result = [types.TextContent(
                type="text",
                text=f"✅ Note created: {note_path}"
            )]
        
        elif name == "cc_read_note":
            vault = get_vault_manager()
            content = vault.read_note(
                title=arguments["title"],
                folder=arguments.get("folder")
            )
            
            if content:
                result = [types.TextContent(type="text", text=content)]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Note '{arguments['title']}' not found"
                )]
        
        elif name == "cc_update_note":
            vault = get_vault_manager()
            success = vault.update_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder")
            )
            
            if success:
                result = [types.TextContent(
                    type="text",
                    text=f"✅ Note '{arguments['title']}' updated"
                )]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update note '{arguments['title']}'"
                )]
        
        elif name == "cc_search_notes":
            vault = get_vault_manager()
            results = vault.search_notes(
                query=arguments["query"],
                folder=arguments.get("folder")
            )
            
            if not results:
                result = [types.TextContent(
                    type="text",
                    text=f"No notes found matching '{arguments['query']}'"
                )]
            else:
                output = [f"Found {len(results)} notes:\n"]
                for search_result in results:
                    output.append(f"📄 {search_result['title']}")
                    output.append(f"   Folder: {search_result['folder']}")
                    output.append(f"   Preview: {search_result['preview']}")
                    output.append("")
                
                result = [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "cc_create_daily_note":
            vault = get_vault_manager()
            note_path = vault.create_daily_note(
                summary=arguments["summary"],
                events=arguments.get("events", [])
            )
            
            result = [types.TextContent(
                type="text",
                text=f"✅ Daily note created: {note_path}"
            )]
        
        elif name == "cc_complete_task":
            # Validate completion requirements
            if not arguments.get("memories_updated"):
                result = [types.TextContent(
                    type="text",
                    text="❌ Cannot complete task: Memories must be updated"
                )]
            elif not arguments.get("cleanup_done"):
                result = [types.TextContent(
                    type="text",
                    text="❌ Cannot complete task: Cleanup must be done"
                )]
            else:
                title = arguments["title"]
                # Update task status
                vault = get_vault_manager()
                
                # Read the task first
                content = vault.read_note(title, "📋 TaskTracker/Active")
                if not content:
                    result = [types.TextContent(
                        type="text",
                        text=f"❌ Task '{title}' not found in Active folder"
                    )]
                else:
                    # Update status and add completion info
                    lines = content.split('\n')
                    updated_lines = []
                    for line in lines:
                        if line.startswith("## Status:"):
                            updated_lines.append("## Status: ✅ Complete")
                            updated_lines.append(f"Completed: {datetime.now().strftime('%Y-%m-%d')}")
                        else:
                            updated_lines.append(line)
                    
                    # Add completion checklist at the end
                    updated_lines.extend([
                        "",
                        "## Completion Checklist",
                        f"- [x] Documentation Updated: {'Yes - ' + arguments.get('documentation_link', 'N/A') if arguments.get('documentation_updated') else 'No'}",
                        f"- [x] Memories Updated: Yes - {arguments.get('memory_id', 'Updated')}",
                        f"- [x] Cleanup Done: Yes",
                        ""
                    ])
                    
                    if arguments.get("completion_notes"):
                        updated_lines.extend([
                            "## Completion Notes",
                            arguments["completion_notes"],
                            ""
                        ])
                    
                    # Update the note
                    updated_content = '\n'.join(updated_lines)
                    success = vault.update_note(title, updated_content, "📋 TaskTracker/Active")
                    
                    if success:
                        # Try to move to Complete folder
                        # This would need Desktop Commander since we can't move files directly
                        result = [types.TextContent(
                            type="text",
                            text=f"✅ Task '{title}' marked complete with checklist. Note: Manual move to Complete folder needed."
                        )]
                    else:
                        result = [types.TextContent(
                            type="text",
                            text=f"❌ Failed to update task '{title}'"
                        )]
        
        elif name == "cc_move_note":
            title = arguments["title"]
            from_folder = arguments["from_folder"]
            to_folder = arguments["to_folder"]
            
            vault = get_vault_manager()
            
            # Read the note content
            content = vault.read_note(title, from_folder)
            if not content:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Note '{title}' not found in {from_folder}"
                )]
            else:
                # Create in new location
                # Extract just the content without frontmatter for create_note
                lines = content.split('\n')
                content_start = 0
                if lines[0] == '---':
                    for i in range(1, len(lines)):
                        if lines[i] == '---':
                            content_start = i + 1
                            break
                
                # Get the main content
                main_content = '\n'.join(lines[content_start:]).strip()
                
                # Create note in new location
                new_path = vault.create_note(
                    title=title,
                    content=main_content,
                    folder=to_folder
                )
                
                if new_path:
                    # Note: We can't delete the old one with current vault manager
                    # Would need to use Desktop Commander for full move
                    result = [types.TextContent(
                        type="text",
                        text=f"✅ Note copied to {new_path}. Note: Manual deletion from {from_folder} needed."
                    )]
                else:
                    result = [types.TextContent(
                        type="text",
                        text=f"❌ Failed to create note in {to_folder}"
                    )]
        
        elif name == "cc_update_checkbox":
            title = arguments["title"]
            checkbox_text = arguments["checkbox_text"]
            checked = arguments["checked"]
            folder = arguments.get("folder")
            
            vault = get_vault_manager()
            
            # Read the note
            content = vault.read_note(title, folder)
            if not content:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Note '{title}' not found"
                )]
            else:
                # Update checkbox
                lines = content.split('\n')
                updated = False
                for i, line in enumerate(lines):
                    if '[ ]' in line and checkbox_text in line:
                        if checked:
                            lines[i] = line.replace('[ ]', '[x]')
                            updated = True
                    elif '[x]' in line and checkbox_text in line:
                        if not checked:
                            lines[i] = line.replace('[x]', '[ ]')
                            updated = True
                
                if updated:
                    updated_content = '\n'.join(lines)
                    # Extract main content for update_note
                    content_start = 0
                    if lines[0] == '---':
                        for i in range(1, len(lines)):
                            if lines[i] == '---':
                                content_start = i + 1
                                break
                    
                    main_content = '\n'.join(lines[content_start:]).strip()
                    
                    success = vault.update_note(title, main_content, folder)
                    if success:
                        checkbox_state = "checked" if checked else "unchecked"
                        result = [types.TextContent(
                            type="text",
                            text=f"✅ Checkbox '{checkbox_text}' {checkbox_state}"
                        )]
                    else:
                        result = [types.TextContent(
                            type="text",
                            text=f"❌ Failed to update note"
                        )]
                else:
                    result = [types.TextContent(
                        type="text",
                        text=f"❌ Checkbox with text '{checkbox_text}' not found"
                    )]
        


        
        elif name == "cc_memory_to_note":
            # Initialize memory integration
            vault = get_vault_manager()
            memory_collection = get_memory_collection()
            
            if not memory_collection:
                result = [types.TextContent(
                    type="text",
                    text="❌ Memory collection not available. Please check ChromaDB connection."
                )]
            else:
                integration = MemoryNoteIntegration(vault, memory_collection)
                
                # Convert memory to note
                note_path = integration.memory_to_note(
                    memory_id=arguments["memory_id"],
                    folder=arguments.get("folder", "🧠 Knowledge")
                )
                
                if note_path:
                    result = [types.TextContent(
                        type="text",
                        text=f"✅ Memory converted to note: {note_path}"
                    )]
                else:
                    result = [types.TextContent(
                        type="text",
                        text=f"❌ Failed to convert memory '{arguments['memory_id']}' to note"
                    )]
        
        elif name == "cc_note_to_memory":
            # Initialize memory integration
            vault = get_vault_manager()
            memory_collection = get_memory_collection()
            
            if not memory_collection:
                result = [types.TextContent(
                    type="text",
                    text="❌ Memory collection not available. Please check ChromaDB connection."
                )]
            else:
                integration = MemoryNoteIntegration(vault, memory_collection)
                
                # Convert note to memory
                memory_id = integration.note_to_memory(
                    note_title=arguments["note_title"],
                    folder=arguments.get("folder")
                )
                
                if memory_id:
                    result = [types.TextContent(
                        type="text",
                        text=f"✅ Note converted to memory: {memory_id}"
                    )]
                else:
                    result = [types.TextContent(
                        type="text",
                        text=f"❌ Failed to convert note '{arguments['note_title']}' to memory"
                    )]
        
        elif name == "cc_sync_to_obsidian":
            # Initialize memory integration
            vault = get_vault_manager()
            memory_collection = get_memory_collection()
            
            if not memory_collection:
                result = [types.TextContent(
                    type="text",
                    text="❌ Memory collection not available. Please check ChromaDB connection."
                )]
            else:
                integration = MemoryNoteIntegration(vault, memory_collection)
                
                # Sync memories to Obsidian
                synced_notes = integration.sync_to_obsidian(
                    query=arguments.get("query", "tag:important"),
                    n_results=arguments.get("n_results", 10)
                )
                
                if synced_notes:
                    result = [types.TextContent(
                        type="text",
                        text=f"✅ Synced {len(synced_notes)} memories to Obsidian:\n" + "\n".join(synced_notes)
                    )]
                else:
                    result = [types.TextContent(
                        type="text",
                        text="ℹ️ No new memories to sync (all matching memories already synced)"
                    )]
        
        else:
            result = [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
            return result
        
        return result
            
    except Exception as e:
        logger.error(f"Error in {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]

async def main():
    """Run the MCP server"""
    logger.info("Starting CC Nerve Center MCP server...")
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cc-nerve-center",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())