#!/usr/bin/env python3
"""
SharedVault MCP Server
Project Biographer for AI-Human Collaboration
"""

import asyncio
import sys
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from task_operations import TaskOperations
from shared_vault_manager import SharedVaultManager

# Import MCP SDK
try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.models import InitializationOptions
    import mcp.server.stdio
    import mcp.types as types
except ImportError:
    print("ERROR: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("sharedvault_mcp")

# Create server instance
server = Server("sharedvault")

# Create task operations instance
task_ops = TaskOperations()

# Create SharedVault manager instance
shared_vault: Optional[SharedVaultManager] = None

def get_shared_vault() -> SharedVaultManager:
    """Get or initialize the SharedVault manager"""
    global shared_vault
    if shared_vault is None:
        try:
            shared_vault = SharedVaultManager()
            logger.info("SharedVault manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SharedVault manager: {e}")
            raise
    return shared_vault

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available SharedVault tools"""
    return [
        types.Tool(
            name="wake_dt",
            description="Send wake message to Desktop Claude about task updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to send (no quotes/apostrophes)"},
                    "task_id": {"type": "string", "description": "Task ID for context (optional)"}
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="wake_cc",
            description="Send wake message to Claude Code about task updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to send (no quotes/apostrophes)"},
                    "task_id": {"type": "string", "description": "Task ID for context (optional)"}
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="auto_wake_config",
            description="Configure automatic wake messages on task updates",
            inputSchema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "description": "Enable/disable auto-wake"},
                    "target": {"type": "string", "enum": ["dt", "cc", "both"], "description": "Who to wake"},
                    "triggers": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["create", "update", "complete", "status_change"]},
                        "description": "Which events trigger wake messages"
                    }
                },
                "required": ["enabled"]
            }
        ),
        types.Tool(
            name="get_wake_status",
            description="Get current wake message configuration and status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # SharedVault Obsidian Tools
        types.Tool(
            name="shared_create_note",
            description="Create a new note in the SharedVault",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content (markdown)"},
                    "folder": {"type": "string", "description": "Target folder", "default": "📋 TaskTracker"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the note"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="shared_read_note",
            description="Read a note from the SharedVault",
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
            name="shared_update_note",
            description="Update an existing note in the SharedVault",
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
            name="shared_search_notes",
            description="Search notes in the SharedVault",
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
            name="shared_move_note",
            description="Move a note between folders in SharedVault",
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
            name="shared_update_checkbox",
            description="Toggle checkboxes in a SharedVault note",
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
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "create_task":
            result = task_ops.create_task(
                title=arguments["title"],
                description=arguments["description"],
                participants=arguments.get("participants"),
                metadata=arguments.get("metadata")
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Task created: {result['task_id']}\n"
                         f"Path: {result['path']}\n"
                         f"{result['message']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to create task: {result['message']}"
                )]
        
        elif name == "add_task_entry":
            result = task_ops.add_task_entry(
                task_id=arguments["task_id"],
                entry_type=arguments["entry_type"],
                content=arguments["content"],
                participants=arguments.get("participants"),
                metadata=arguments.get("metadata")
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Added {arguments['entry_type']} entry to task {arguments['task_id']}\n"
                         f"Entry file: {result['entry_file']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to add entry: {result['message']}"
                )]
        
        elif name == "get_task_details":
            result = task_ops.get_task_details(arguments["task_id"])
            
            if result["success"]:
                index = result["index"]
                entries = result["entries"]
                
                details = f"📋 Task: {index['title']}\n"
                details += f"ID: {result['task_id']}\n"
                details += f"Status: {index['status']} | Phase: {index['phase']}\n"
                details += f"Created: {index['created']}\n"
                details += f"Participants: {', '.join(index['participants'])}\n"
                details += f"\n📝 Entries ({result['entry_count']}):\n"
                
                for entry in entries:
                    details += f"\n[{entry['type'].upper()}] {entry['timestamp']}\n"
                    details += f"{entry['content'][:200]}...\n" if len(entry['content']) > 200 else f"{entry['content']}\n"
                
                return [types.TextContent(type="text", text=details)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to get task details: {result['message']}"
                )]
        
        elif name == "list_active_tasks":
            result = task_ops.list_active_tasks()
            
            if result["success"]:
                if result["count"] == 0:
                    return [types.TextContent(
                        type="text",
                        text="No active tasks found."
                    )]
                
                task_list = f"📋 Active Tasks ({result['count']}):\n\n"
                for task in result["active_tasks"]:
                    task_list += f"• {task['task_id']}\n"
                    task_list += f"  Title: {task['title']}\n"
                    task_list += f"  Status: {task['status']} | Phase: {task['phase']}\n"
                    task_list += f"  Created: {task['created']}\n\n"
                
                return [types.TextContent(type="text", text=task_list)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to list tasks: {result['message']}"
                )]
        
        elif name == "update_task_status":
            result = task_ops.update_task_status(
                task_id=arguments["task_id"],
                new_status=arguments["new_status"],
                phase=arguments.get("phase")
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ {result['message']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update status: {result['message']}"
                )]
        
        elif name == "complete_task_with_checklist":
            result = task_ops.complete_task_with_checklist(
                task_id=arguments["task_id"],
                documentation_done=arguments["documentation_done"],
                memory_hash=arguments["memory_hash"],
                cleanup_done=arguments["cleanup_done"],
                documentation_path=arguments.get("documentation_path"),
                tags=arguments.get("tags"),
                metadata=arguments.get("metadata"),
                completion_notes=arguments.get("completion_notes")
            )
            
            if result["success"]:
                checklist = result["checklist"]
                response = f"✅ {result['message']}\n\n"
                response += "Checklist Summary:\n"
                response += f"• Documentation: {'✓' if checklist['documentation']['done'] else '✗'}"
                if checklist['documentation']['path']:
                    response += f" ({checklist['documentation']['path']})"
                response += f"\n• Memory: ✓ {checklist['memory']['hash']}\n"
                response += f"• Cleanup: ✓\n"
                if checklist['tags']:
                    response += f"• Tags: {', '.join(checklist['tags'])}\n"
                if result.get('moved'):
                    response += f"\nTask moved to Complete folder"
                
                return [types.TextContent(type="text", text=response)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ {result['message']}"
                )]
        
        elif name == "wake_dt":
            if not hasattr(task_ops, 'wake_manager') or not task_ops.wake_manager:
                return [types.TextContent(
                    type="text",
                    text="❌ Wake manager not available"
                )]
            
            result = task_ops.wake_manager.wake_dt(
                message=arguments["message"],
                task_id=arguments.get("task_id")
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ {result['message']}\nSent: {result['clean_message']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Wake failed: {result['error']}"
                )]
        
        elif name == "wake_cc":
            if not hasattr(task_ops, 'wake_manager') or not task_ops.wake_manager:
                return [types.TextContent(
                    type="text",
                    text="❌ Wake manager not available"
                )]
            
            result = task_ops.wake_manager.wake_cc(
                message=arguments["message"],
                task_id=arguments.get("task_id")
            )
            
            if result["success"]:
                return [types.TextContent(
                    type="text",
                    text=f"✅ {result['message']}\nSent: {result['clean_message']}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Wake failed: {result['error']}"
                )]
        
        elif name == "auto_wake_config":
            if not hasattr(task_ops, 'wake_manager') or not task_ops.wake_manager:
                return [types.TextContent(
                    type="text",
                    text="❌ Wake manager not available"
                )]
            
            # Update configuration
            config_updates = {}
            if "enabled" in arguments:
                config_updates["auto_wake_enabled"] = arguments["enabled"]
            if "target" in arguments:
                targets = [arguments["target"]] if arguments["target"] != "both" else ["cc", "dt"]
                config_updates["auto_wake_targets"] = targets
            if "triggers" in arguments:
                config_updates["auto_wake_triggers"] = arguments["triggers"]
            
            new_config = task_ops.wake_manager.update_config(**config_updates)
            
            return [types.TextContent(
                type="text",
                text=f"✅ Auto-wake configuration updated\n\n"
                     f"Enabled: {new_config['auto_wake_enabled']}\n"
                     f"Targets: {', '.join(new_config['auto_wake_targets'])}\n"
                     f"Triggers: {', '.join(new_config['auto_wake_triggers'])}"
            )]
        
        elif name == "get_wake_status":
            if not hasattr(task_ops, 'wake_manager') or not task_ops.wake_manager:
                return [types.TextContent(
                    type="text",
                    text="❌ Wake manager not available"
                )]
            
            status = task_ops.wake_manager.get_status()
            
            output = [
                "📡 Wake Message Status",
                "=" * 25,
                f"Auto-wake: {'✅ Enabled' if status['config']['auto_wake_enabled'] else '❌ Disabled'}",
                f"Targets: {', '.join(status['config']['auto_wake_targets'])}",
                f"Triggers: {', '.join(status['config']['auto_wake_triggers'])}",
                f"Total messages sent: {status['total_wakes']}",
                "",
                "Script Status:",
                f"  DT wake script: {'✅' if status['script_exists']['dt_wake'] else '❌'} {status['script_paths']['dt_wake']}",
                f"  CC wake script: {'✅' if status['script_exists']['cc_wake'] else '❌'} {status['script_paths']['cc_wake']}"
            ]
            
            if status['recent_wakes']:
                output.append("\nRecent Wake Messages:")
                for wake in status['recent_wakes']:
                    status_icon = "✅" if wake['success'] else "❌"
                    output.append(f"  {status_icon} {wake['target'].upper()}: {wake['message'][:50]}...")
            
            return [types.TextContent(
                type="text",
                text="\n".join(output)
            )]
        
        # SharedVault tool handlers
        elif name == "shared_create_note":
            vault = get_shared_vault()
            note_path = vault.create_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder", "📋 TaskTracker"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ SharedVault note created: {note_path}"
            )]
            
        elif name == "shared_read_note":
            vault = get_shared_vault()
            content = vault.read_note(
                title=arguments["title"],
                folder=arguments.get("folder")
            )
            
            if content:
                return [types.TextContent(type="text", text=content)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Note '{arguments['title']}' not found in SharedVault"
                )]
        
        elif name == "shared_update_note":
            vault = get_shared_vault()
            success = vault.update_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder")
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ SharedVault note '{arguments['title']}' updated"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update note '{arguments['title']}' in SharedVault"
                )]
        
        elif name == "shared_search_notes":
            vault = get_shared_vault()
            results = vault.search_notes(
                query=arguments["query"],
                folder=arguments.get("folder")
            )
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No notes found in SharedVault matching '{arguments['query']}'"
                )]
            
            output = [f"Found {len(results)} notes in SharedVault:\n"]
            for result in results:
                output.append(f"📄 {result['title']}")
                output.append(f"   Folder: {result['folder']}")
                output.append(f"   Preview: {result['preview']}")
                output.append("")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "shared_move_note":
            vault = get_shared_vault()
            success = vault.move_note(
                title=arguments["title"],
                from_folder=arguments["from_folder"],
                to_folder=arguments["to_folder"]
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Note moved in SharedVault: {arguments['to_folder']}/{arguments['title']}.md"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to move note '{arguments['title']}' in SharedVault"
                )]
        
        elif name == "shared_update_checkbox":
            vault = get_shared_vault()
            success = vault.update_checkbox(
                title=arguments["title"],
                checkbox_text=arguments["checkbox_text"],
                checked=arguments["checked"],
                folder=arguments.get("folder")
            )
            
            if success:
                status = "checked" if arguments["checked"] else "unchecked"
                return [types.TextContent(
                    type="text",
                    text=f"✅ Checkbox '{arguments['checkbox_text']}' {status} in SharedVault note '{arguments['title']}'"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update checkbox in SharedVault note '{arguments['title']}'"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Error handling tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]

# Main entry point
async def main():
    """Run the SharedVault MCP server"""
    logger.info("Starting SharedVault MCP Server")
    
    try:
        # Run the server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="sharedvault",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())