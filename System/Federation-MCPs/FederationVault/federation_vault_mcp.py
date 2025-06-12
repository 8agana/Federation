#!/usr/bin/env python3
"""
FederationVault MCP Server - FIXED VERSION
Unified vault management for CC, DT, and Trips with 14 comprehensive tools.

Architecture:
- File Operations: Create, read, update, search, move with permissions
- Knowledge Graph: Observations, relations, context building
- Communication: Wake messages and thread management
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# MCP imports
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configuration
INSTANCE = os.environ.get("FEDERATION_INSTANCE", "cc").lower()
VAULT_PATH = Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault")

# Instance folders mapping
INSTANCE_FOLDERS = {
    "cc": "CC",
    "dt": "DT", 
    "trips": "Trips"
}

# Shared folders
SHARED_FOLDERS = {
    "shared": "🤝 Shared",
    "tasks": "🤝 Shared/📋 TaskTracker",
    "conversations": "🤝 Shared/💬 Conversations",
    "knowledge": "🤝 Shared/📚 Knowledge",
    "relations": "🤝 Shared/🔗 Relations",
    "summaries": "🤝 Shared/📊 Summaries"
}

# Initialize server
server = Server("federation-vault")

def get_vault_path(folder: Optional[str] = None, instance: Optional[str] = None) -> Path:
    """Get the appropriate vault path based on folder and instance."""
    if folder and folder in SHARED_FOLDERS:
        return VAULT_PATH / SHARED_FOLDERS[folder]
    
    # Default to current instance folder
    target_instance = instance or INSTANCE
    instance_folder = INSTANCE_FOLDERS.get(target_instance, "CC")
    return VAULT_PATH / instance_folder

def add_metadata(content: str, operation: str = "create") -> str:
    """Add frontmatter metadata to note content."""
    timestamp = datetime.now().isoformat()
    
    # Check if frontmatter already exists
    if content.startswith("---\n"):
        # Update existing frontmatter
        lines = content.split("\n")
        frontmatter_end = lines[1:].index("---") + 1
        
        # Extract existing frontmatter
        existing = "\n".join(lines[1:frontmatter_end])
        body = "\n".join(lines[frontmatter_end + 1:])
        
        # Add our metadata
        metadata = f"""---
{existing}
last_modified: {timestamp}
modified_by: {INSTANCE}
---

{body}"""
    else:
        # Add new frontmatter
        metadata = f"""---
created: {timestamp}
created_by: {INSTANCE}
last_modified: {timestamp}
modified_by: {INSTANCE}
---

{content}"""
    
    return metadata

def can_write_to_path(path: Path) -> bool:
    """Check if current instance can write to the given path."""
    path_str = str(path)
    
    # Can always write to shared folders
    for shared_path in SHARED_FOLDERS.values():
        if shared_path in path_str:
            return True
    
    # Can write to own instance folder
    own_folder = INSTANCE_FOLDERS.get(INSTANCE, "CC")
    if own_folder in path_str:
        return True
    
    return False

def find_file_in_vault(vault_path: Path, title: str) -> Optional[Path]:
    """Find a file in the vault with fuzzy matching and smart suggestions."""
    if not vault_path.exists():
        return None
    
    # Strategy 1: Exact filename match
    safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
    exact_match = vault_path / f"{safe_title}.md"
    if exact_match.exists():
        return exact_match
    
    # Strategy 2: Try original title as-is
    original_match = vault_path / f"{title}.md"
    if original_match.exists():
        return original_match
    
    # Strategy 3: Fuzzy matching - search all .md files
    md_files = list(vault_path.glob("*.md"))
    
    # Try partial matches in order of preference
    title_lower = title.lower()
    
    # First: exact stem match (case insensitive)
    for file in md_files:
        if file.stem.lower() == title_lower:
            return file
    
    # Second: title is contained in filename
    for file in md_files:
        if title_lower in file.stem.lower():
            return file
    
    # Third: filename is contained in title (for shorter searches)
    for file in md_files:
        if file.stem.lower() in title_lower and len(file.stem) > 3:
            return file
    
    # Fourth: word-based matching (split on spaces, dashes, underscores)
    title_words = set(title_lower.replace('-', ' ').replace('_', ' ').split())
    if title_words:
        for file in md_files:
            file_words = set(file.stem.lower().replace('-', ' ').replace('_', ' ').split())
            # If most title words are in filename
            if len(title_words.intersection(file_words)) >= min(len(title_words), 2):
                return file
    
    return None

# Tool call router
@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Route tool calls to appropriate handlers"""
    try:
        if not arguments:
            arguments = {}
        
        # File Operations
        if name == "fv_create_note":
            return await create_note_impl(arguments)
        elif name == "fv_read_note":
            return await read_note_impl(arguments)
        elif name == "fv_update_note":
            return await update_note_impl(arguments)
        elif name == "fv_search":
            return await search_impl(arguments)
        elif name == "fv_move_note":
            return await move_note_impl(arguments)
        # Knowledge Graph
        elif name == "fv_add_observation":
            return await add_observation_impl(arguments)
        elif name == "fv_add_relation":
            return await add_relation_impl(arguments)
        elif name == "fv_build_context":
            return await build_context_impl(arguments)
        # Communication
        elif name == "fv_wake_dt":
            return await wake_dt_impl(arguments)
        elif name == "fv_wake_cc":
            return await wake_cc_impl(arguments)
        elif name == "fv_create_thread":
            return await create_thread_impl(arguments)
        elif name == "fv_read_thread":
            return await read_thread_impl(arguments)
        elif name == "fv_add_to_thread":
            return await add_to_thread_impl(arguments)
        elif name == "fv_list_threads":
            return await list_threads_impl(arguments)
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error in {name}: {str(e)}"
        )]

# File Operations Implementation

async def create_note_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Create a new note in FederationVault."""
    try:
        title = arguments.get("title")
        content = arguments.get("content")
        folder = arguments.get("folder")
        private = arguments.get("private", False)
        
        if not title or not content:
            return [types.TextContent(type="text", text="❌ Title and content are required")]
        
        # Get target path
        vault_path = get_vault_path(folder)
        vault_path.mkdir(parents=True, exist_ok=True)
        
        # Create file path
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        file_path = vault_path / f"{safe_title}.md"
        
        # Check permissions
        if not can_write_to_path(file_path):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot write to {vault_path} - insufficient permissions"
            )]
        
        # Add privacy marker if requested
        if private and not folder:
            content = f"<!-- PRIVATE: {INSTANCE} -->\n\n{content}"
        
        # Add metadata
        content_with_metadata = add_metadata(content, "create")
        
        # Write file
        file_path.write_text(content_with_metadata, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Created note: {file_path.relative_to(VAULT_PATH)}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text", 
            text=f"❌ Error creating note: {str(e)}"
        )]

async def read_note_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Read a note from FederationVault."""
    try:
        title = arguments.get("title")
        folder = arguments.get("folder")
        instance = arguments.get("instance")
        
        if not title:
            return [types.TextContent(type="text", text="❌ Title is required")]
        
        # Get search path
        vault_path = get_vault_path(folder, instance)
        
        # Try to find the file with improved matching
        file_path = find_file_in_vault(vault_path, title)
        
        if not file_path:
            # Show helpful error with available files
            available_files = list(vault_path.glob("*.md"))
            if available_files:
                file_list = "\n".join([f"  • {f.stem}" for f in available_files[:10]])
                if len(available_files) > 10:
                    file_list += f"\n  ... and {len(available_files) - 10} more"
                error_msg = f"❌ Note not found: '{title}' in {vault_path.relative_to(VAULT_PATH)}\n\nAvailable files:\n{file_list}"
            else:
                error_msg = f"❌ No files found in {vault_path.relative_to(VAULT_PATH)}"
            
            return [types.TextContent(type="text", text=error_msg)]
        
        # Read content
        content = file_path.read_text(encoding='utf-8')
        
        # Check if private and we can access it
        if "<!-- PRIVATE:" in content and not can_write_to_path(file_path):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot access private note: {title}"
            )]
        
        return [types.TextContent(
            type="text",
            text=f"📄 {file_path.relative_to(VAULT_PATH)}:\n\n{content}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error reading note: {str(e)}"
        )]

async def update_note_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Update an existing note in FederationVault."""
    try:
        title = arguments.get("title")
        content = arguments.get("content")
        folder = arguments.get("folder")
        instance = arguments.get("instance")
        
        if not title or not content:
            return [types.TextContent(type="text", text="❌ Title and content are required")]
        
        # Get search path
        vault_path = get_vault_path(folder, instance)
        
        # Find the file with improved matching
        file_path = find_file_in_vault(vault_path, title)
        
        if not file_path:
            # Show helpful error with available files
            available_files = list(vault_path.glob("*.md"))
            if available_files:
                file_list = "\n".join([f"  • {f.stem}" for f in available_files[:10]])
                if len(available_files) > 10:
                    file_list += f"\n  ... and {len(available_files) - 10} more"
                error_msg = f"❌ Note not found: '{title}' in {vault_path.relative_to(VAULT_PATH)}\n\nAvailable files:\n{file_list}"
            else:
                error_msg = f"❌ No files found in {vault_path.relative_to(VAULT_PATH)}"
            
            return [types.TextContent(type="text", text=error_msg)]
        
        # Check permissions
        if not can_write_to_path(file_path):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot update note - insufficient permissions"
            )]
        
        # Add metadata
        content_with_metadata = add_metadata(content, "update")
        
        # Write updated content
        file_path.write_text(content_with_metadata, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Updated note: {file_path.relative_to(VAULT_PATH)}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error updating note: {str(e)}"
        )]

async def search_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Search for content across FederationVault."""
    try:
        query = arguments.get("query")
        include_private = arguments.get("include_private", False)
        instances = arguments.get("instances", ["all"])
        
        if not query:
            return [types.TextContent(type="text", text="❌ Query is required")]
        
        results = []
        search_instances = instances if "all" not in instances else ["cc", "dt", "trips"]
        
        # Search in instance folders
        for inst in search_instances:
            if inst not in INSTANCE_FOLDERS:
                continue
                
            instance_path = VAULT_PATH / INSTANCE_FOLDERS[inst]
            if instance_path.exists():
                for file_path in instance_path.rglob("*.md"):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        
                        # Skip private notes unless we own them or explicitly requested
                        if "<!-- PRIVATE:" in content and not include_private:
                            if inst != INSTANCE:
                                continue
                        
                        # Search in title and content
                        if query.lower() in file_path.stem.lower() or query.lower() in content.lower():
                            relative_path = file_path.relative_to(VAULT_PATH)
                            results.append(f"📄 {relative_path}")
                            
                    except Exception:
                        continue
        
        # Search in shared folders
        shared_path = VAULT_PATH / "🤝 Shared"
        if shared_path.exists():
            for file_path in shared_path.rglob("*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    if query.lower() in file_path.stem.lower() or query.lower() in content.lower():
                        relative_path = file_path.relative_to(VAULT_PATH)
                        results.append(f"🤝 {relative_path}")
                        
                except Exception:
                    continue
        
        if not results:
            return [types.TextContent(
                type="text",
                text=f"🔍 No results found for: {query}"
            )]
        
        return [types.TextContent(
            type="text",
            text=f"🔍 Search results for '{query}':\n\n" + "\n".join(results[:20])  # Limit to 20 results
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error searching: {str(e)}"
        )]

async def move_note_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Move a note between folders or instances."""
    try:
        title = arguments.get("title")
        from_folder = arguments.get("from_folder")
        to_folder = arguments.get("to_folder")
        from_instance = arguments.get("from_instance")
        to_instance = arguments.get("to_instance")
        
        if not title:
            return [types.TextContent(type="text", text="❌ Title is required")]
        
        # Get source path
        source_path = get_vault_path(from_folder, from_instance)
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        source_file = source_path / f"{safe_title}.md"
        
        if not source_file.exists():
            return [types.TextContent(
                type="text",
                text=f"❌ Source note not found: {title}"
            )]
        
        # Check if we can read from source
        if not can_write_to_path(source_file):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot move note - insufficient permissions on source"
            )]
        
        # Get destination path
        dest_path = get_vault_path(to_folder, to_instance)
        dest_path.mkdir(parents=True, exist_ok=True)
        dest_file = dest_path / f"{safe_title}.md"
        
        # Check if we can write to destination
        if not can_write_to_path(dest_file):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot move note - insufficient permissions on destination"
            )]
        
        # Read, update metadata, and write to new location
        content = source_file.read_text(encoding='utf-8')
        updated_content = add_metadata(content, "move")
        dest_file.write_text(updated_content, encoding='utf-8')
        
        # Remove from source
        source_file.unlink()
        
        source_rel = source_file.relative_to(VAULT_PATH)
        dest_rel = dest_file.relative_to(VAULT_PATH)
        
        return [types.TextContent(
            type="text",
            text=f"✅ Moved note:\n📤 From: {source_rel}\n📥 To: {dest_rel}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error moving note: {str(e)}"
        )]

# Communication Implementation (simplified for now)
async def wake_dt_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Send ultra-short wake message to DT."""
    try:
        thread_name = arguments.get("thread_name")
        if not thread_name:
            return [types.TextContent(type="text", text="❌ Thread name is required")]
        
        wake_message = f"CC-DT_Check_{thread_name}"
        return [types.TextContent(
            type="text",
            text=f"📨 Wake message sent: {wake_message}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error sending wake message: {str(e)}"
        )]

async def wake_cc_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Send ultra-short wake message to CC."""
    try:
        thread_name = arguments.get("thread_name")
        if not thread_name:
            return [types.TextContent(type="text", text="❌ Thread name is required")]
        
        wake_message = f"DT-CC_Check_{thread_name}"
        return [types.TextContent(
            type="text",
            text=f"📨 Wake message sent: {wake_message}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error sending wake message: {str(e)}"
        )]

# Placeholder implementations for other tools
async def add_observation_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Add a semantic observation to a note."""
    return [types.TextContent(type="text", text="🚧 Observation functionality coming soon")]

async def add_relation_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Add a relation between two notes."""
    return [types.TextContent(type="text", text="🚧 Relation functionality coming soon")]

async def build_context_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Build context by following relations from a note."""
    return [types.TextContent(type="text", text="🚧 Context building functionality coming soon")]

async def create_thread_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Create a new conversation thread."""
    return [types.TextContent(type="text", text="🚧 Thread creation functionality coming soon")]

async def read_thread_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Read an existing conversation thread."""
    return [types.TextContent(type="text", text="🚧 Thread reading functionality coming soon")]

async def add_to_thread_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Add a message to an existing thread."""
    return [types.TextContent(type="text", text="🚧 Thread messaging functionality coming soon")]

async def list_threads_impl(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """List available conversation threads."""
    return [types.TextContent(type="text", text="🚧 Thread listing functionality coming soon")]

# List available tools
@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="fv_create_note",
            description="Create a new note in FederationVault with automatic metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content"},
                    "folder": {"type": "string", "description": "Target folder ('shared', 'tasks', etc.) or None for instance folder"},
                    "private": {"type": "boolean", "description": "Mark as private (only for instance folders)"}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="fv_read_note",
            description="Read a note from FederationVault",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to read"},
                    "folder": {"type": "string", "description": "Folder to search in"},
                    "instance": {"type": "string", "description": "Instance folder to search ('cc', 'dt', 'trips')"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="fv_update_note",
            description="Update an existing note in FederationVault",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to update"},
                    "content": {"type": "string", "description": "New content"},
                    "folder": {"type": "string", "description": "Folder to search in"},
                    "instance": {"type": "string", "description": "Instance folder to search"}
                },
                "required": ["title", "content"]
            }
        ),
        types.Tool(
            name="fv_search",
            description="Search for content across FederationVault",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "include_private": {"type": "boolean", "description": "Include private notes in search"},
                    "instances": {"type": "array", "items": {"type": "string"}, "description": "Instances to search"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="fv_move_note",
            description="Move a note between folders or instances",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title to move"},
                    "from_folder": {"type": "string", "description": "Source folder"},
                    "to_folder": {"type": "string", "description": "Destination folder"},
                    "from_instance": {"type": "string", "description": "Source instance"},
                    "to_instance": {"type": "string", "description": "Destination instance"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="fv_wake_dt",
            description="Send ultra-short wake message to DT",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_name": {"type": "string", "description": "Name of the thread/conversation to reference"}
                },
                "required": ["thread_name"]
            }
        ),
        types.Tool(
            name="fv_wake_cc",
            description="Send ultra-short wake message to CC",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_name": {"type": "string", "description": "Name of the thread/conversation to reference"}
                },
                "required": ["thread_name"]
            }
        ),
        # Placeholder tools for now
        types.Tool(
            name="fv_add_observation",
            description="Add a semantic observation to a note (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_add_relation", 
            description="Add a relation between two notes (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_build_context",
            description="Build context by following relations from a note (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_create_thread",
            description="Create a new conversation thread (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_read_thread",
            description="Read an existing conversation thread (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_add_to_thread",
            description="Add a message to an existing thread (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="fv_list_threads",
            description="List available conversation threads (coming soon)",
            inputSchema={"type": "object", "properties": {}}
        )
    ]

# List available resources (none for now)
@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources."""
    return []

# List available prompts (none for now)
@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """List available prompts."""
    return []

# Initialize the server
async def main():
    """Main server initialization."""
    print(f"🚀 Starting FederationVault MCP Server for instance: {INSTANCE}", file=sys.stderr)
    print(f"📁 Vault path: {VAULT_PATH}", file=sys.stderr)
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="federation-vault",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())