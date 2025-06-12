#!/usr/bin/env python3
"""
FederationVault MCP Server
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

# List available tools
@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    Each tool is defined with @server.call_tool() decorator above.
    """
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
            name="fv_add_observation",
            description="Add a semantic observation to a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Target note title"},
                    "category": {"type": "string", "description": "Observation category"},
                    "content": {"type": "string", "description": "Observation content"},
                    "folder": {"type": "string", "description": "Folder to search for note"}
                },
                "required": ["note_title", "category", "content"]
            }
        ),
        types.Tool(
            name="fv_add_relation",
            description="Add a relation between two notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_note": {"type": "string", "description": "Source note title"},
                    "relation_type": {"type": "string", "description": "Type of relation"},
                    "to_note": {"type": "string", "description": "Target note title"},
                    "context": {"type": "string", "description": "Optional context for the relation"}
                },
                "required": ["from_note", "relation_type", "to_note"]
            }
        ),
        types.Tool(
            name="fv_build_context",
            description="Build context by following relations from a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Starting note title"},
                    "depth": {"type": "integer", "description": "How many levels of relations to follow"}
                },
                "required": ["note_title"]
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
        types.Tool(
            name="fv_create_thread",
            description="Create a new conversation thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Thread title"},
                    "initial_message": {"type": "string", "description": "Starting message"},
                    "participants": {"type": "array", "items": {"type": "string"}, "description": "List of participants"}
                },
                "required": ["title", "initial_message"]
            }
        ),
        types.Tool(
            name="fv_read_thread",
            description="Read an existing conversation thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_name": {"type": "string", "description": "Thread identifier (can be partial name)"}
                },
                "required": ["thread_name"]
            }
        ),
        types.Tool(
            name="fv_add_to_thread",
            description="Add a message to an existing thread",
            inputSchema={
                "type": "object",
                "properties": {
                    "thread_name": {"type": "string", "description": "Thread identifier (can be partial name)"},
                    "message": {"type": "string", "description": "Message to add"}
                },
                "required": ["thread_name", "message"]
            }
        ),
        types.Tool(
            name="fv_list_threads",
            description="List available conversation threads",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of threads to show"}
                }
            }
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

# Tool call router
@server.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Route tool calls to appropriate handlers"""
    try:
        # File Operations
        if name == "fv_create_note":
            return await fv_create_note_impl(arguments)
        elif name == "fv_read_note":
            return await fv_read_note_impl(arguments)
        elif name == "fv_update_note":
            return await fv_update_note_impl(arguments)
        elif name == "fv_search":
            return await fv_search_impl(arguments)
        elif name == "fv_move_note":
            return await fv_move_note_impl(arguments)
        # Knowledge Graph
        elif name == "fv_add_observation":
            return await fv_add_observation_impl(arguments)
        elif name == "fv_add_relation":
            return await fv_add_relation_impl(arguments)
        elif name == "fv_build_context":
            return await fv_build_context_impl(arguments)
        # Communication
        elif name == "fv_wake_dt":
            return await fv_wake_dt_impl(arguments)
        elif name == "fv_wake_cc":
            return await fv_wake_cc_impl(arguments)
        elif name == "fv_create_thread":
            return await fv_create_thread_impl(arguments)
        elif name == "fv_read_thread":
            return await fv_read_thread_impl(arguments)
        elif name == "fv_add_to_thread":
            return await fv_add_to_thread_impl(arguments)
        elif name == "fv_list_threads":
            return await fv_list_threads_impl(arguments)
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

async def fv_create_note_impl(arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """
    Create a new note in FederationVault.
    
    Args:
        title: Note title
        content: Note content
        folder: Target folder ('shared', 'tasks', 'conversations', etc.) or None for instance folder
        private: Mark as private (only for instance folders)
    """
    try:
        if not arguments:
            return [types.TextContent(type="text", text="❌ No arguments provided")]
        
        title = arguments.get("title")
        content = arguments.get("content")
        folder = arguments.get("folder")
        private = arguments.get("private", False)
        
        if not title or not content:
            return [types.TextContent(type="text", text="❌ Title and content are required")]
        # Get target path
        vault_path = get_vault_path(folder)
        
        # Ensure directory exists
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

@server.call_tool()
async def fv_read_note(title: str, folder: Optional[str] = None, instance: Optional[str] = None) -> List[types.TextContent]:
    """
    Read a note from FederationVault.
    
    Args:
        title: Note title to read
        folder: Folder to search in ('shared', 'tasks', etc.) or None for instance folder
        instance: Which instance folder to search ('cc', 'dt', 'trips') or None for current
    """
    try:
        # Get search path
        vault_path = get_vault_path(folder, instance)
        
        # Try to find the file
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        file_path = vault_path / f"{safe_title}.md"
        
        if not file_path.exists():
            # Try searching for partial matches
            for file in vault_path.glob("*.md"):
                if safe_title.lower() in file.stem.lower():
                    file_path = file
                    break
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Note not found: {title} in {vault_path.relative_to(VAULT_PATH)}"
                )]
        
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

@server.call_tool()
async def fv_update_note(title: str, content: str, folder: Optional[str] = None, instance: Optional[str] = None) -> List[types.TextContent]:
    """
    Update an existing note in FederationVault.
    
    Args:
        title: Note title to update
        content: New content
        folder: Folder to search in
        instance: Instance folder to search
    """
    try:
        # Get search path
        vault_path = get_vault_path(folder, instance)
        
        # Find the file
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        file_path = vault_path / f"{safe_title}.md"
        
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"❌ Note not found: {title}"
            )]
        
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

@server.call_tool()
async def fv_search(query: str, include_private: bool = False, instances: List[str] = ["all"]) -> List[types.TextContent]:
    """
    Search for content across FederationVault.
    
    Args:
        query: Search query
        include_private: Include private notes in search (only your own)
        instances: List of instances to search ['cc', 'dt', 'trips'] or ['all']
    """
    try:
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

@server.call_tool()
async def fv_move_note(title: str, from_folder: Optional[str] = None, to_folder: Optional[str] = None, from_instance: Optional[str] = None, to_instance: Optional[str] = None) -> List[types.TextContent]:
    """
    Move a note between folders or instances.
    
    Args:
        title: Note title to move
        from_folder: Source folder
        to_folder: Destination folder
        from_instance: Source instance
        to_instance: Destination instance
    """
    try:
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

# Knowledge Graph Tools

@server.call_tool()
async def fv_add_observation(note_title: str, category: str, content: str, folder: Optional[str] = None) -> List[types.TextContent]:
    """
    Add a semantic observation to a note.
    
    Args:
        note_title: Target note title
        category: Observation category
        content: Observation content
        folder: Folder to search for note
    """
    try:
        # Find the note
        vault_path = get_vault_path(folder)
        safe_title = "".join(c for c in note_title if c.isalnum() or c in " -_").strip()
        file_path = vault_path / f"{safe_title}.md"
        
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"❌ Note not found: {note_title}"
            )]
        
        # Check permissions
        if not can_write_to_path(file_path):
            return [types.TextContent(
                type="text",
                text=f"❌ Cannot add observation - insufficient permissions"
            )]
        
        # Read existing content
        existing_content = file_path.read_text(encoding='utf-8')
        
        # Add observation section if it doesn't exist
        observation_marker = "## Observations"
        if observation_marker not in existing_content:
            existing_content += f"\n\n{observation_marker}\n"
        
        # Add the observation
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        observation = f"\n### {category} ({timestamp})\n{content}\n"
        
        # Insert observation after the marker
        lines = existing_content.split('\n')
        insert_index = None
        for i, line in enumerate(lines):
            if line.startswith("## Observations"):
                insert_index = i + 1
                break
        
        if insert_index:
            lines.insert(insert_index, observation)
            updated_content = '\n'.join(lines)
        else:
            updated_content = existing_content + observation
        
        # Update metadata and save
        final_content = add_metadata(updated_content, "observation")
        file_path.write_text(final_content, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added observation '{category}' to {note_title}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding observation: {str(e)}"
        )]

@server.call_tool()
async def fv_add_relation(from_note: str, relation_type: str, to_note: str, context: Optional[str] = None) -> List[types.TextContent]:
    """
    Add a relation between two notes.
    
    Args:
        from_note: Source note title
        relation_type: Type of relation (e.g., "relates_to", "depends_on")
        to_note: Target note title
        context: Optional context for the relation
    """
    try:
        # Create relation entry
        timestamp = datetime.now().isoformat()
        relation_data = {
            "from": from_note,
            "relation": relation_type,
            "to": to_note,
            "context": context,
            "created": timestamp,
            "created_by": INSTANCE
        }
        
        # Store in relations folder
        relations_path = VAULT_PATH / "🤝 Shared" / "🔗 Relations"
        relations_path.mkdir(parents=True, exist_ok=True)
        
        # Create relation file name
        safe_from = "".join(c for c in from_note if c.isalnum() or c in " -_").strip()
        safe_to = "".join(c for c in to_note if c.isalnum() or c in " -_").strip()
        relation_file = relations_path / f"{safe_from}_{relation_type}_{safe_to}.json"
        
        # Write relation data
        relation_file.write_text(json.dumps(relation_data, indent=2), encoding='utf-8')
        
        # Also add backlink to both notes if they exist
        for note_title in [from_note, to_note]:
            # Search for the note across instances
            found_file = None
            for instance_folder in INSTANCE_FOLDERS.values():
                instance_path = VAULT_PATH / instance_folder
                safe_title = "".join(c for c in note_title if c.isalnum() or c in " -_").strip()
                potential_file = instance_path / f"{safe_title}.md"
                if potential_file.exists():
                    found_file = potential_file
                    break
            
            if found_file and can_write_to_path(found_file):
                # Add relation to note
                content = found_file.read_text(encoding='utf-8')
                
                # Add relations section if it doesn't exist
                relations_marker = "## Relations"
                if relations_marker not in content:
                    content += f"\n\n{relations_marker}\n"
                
                # Add the relation link
                other_note = to_note if note_title == from_note else from_note
                relation_direction = relation_type if note_title == from_note else f"←{relation_type}"
                relation_link = f"- [[{other_note}]] ({relation_direction})"
                if context:
                    relation_link += f" - {context}"
                relation_link += f" *{timestamp}*\n"
                
                # Insert after relations marker
                content = content.replace(relations_marker, f"{relations_marker}\n{relation_link}")
                
                # Update and save
                updated_content = add_metadata(content, "relation")
                found_file.write_text(updated_content, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Created relation: {from_note} --{relation_type}--> {to_note}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding relation: {str(e)}"
        )]

@server.call_tool()
async def fv_build_context(note_title: str, depth: int = 2) -> List[types.TextContent]:
    """
    Build context by following relations from a note.
    
    Args:
        note_title: Starting note title
        depth: How many levels of relations to follow
    """
    try:
        context_map = {}
        visited = set()
        
        def find_relations(note: str, current_depth: int):
            if current_depth > depth or note in visited:
                return
            
            visited.add(note)
            context_map[note] = {"depth": current_depth, "relations": []}
            
            # Search for relation files
            relations_path = VAULT_PATH / "🤝 Shared" / "🔗 Relations"
            if relations_path.exists():
                for relation_file in relations_path.glob("*.json"):
                    try:
                        relation_data = json.loads(relation_file.read_text(encoding='utf-8'))
                        
                        # Check if this note is involved
                        if relation_data["from"] == note:
                            context_map[note]["relations"].append({
                                "type": relation_data["relation"],
                                "to": relation_data["to"],
                                "context": relation_data.get("context")
                            })
                            # Recursively follow
                            find_relations(relation_data["to"], current_depth + 1)
                            
                        elif relation_data["to"] == note:
                            context_map[note]["relations"].append({
                                "type": f"←{relation_data['relation']}",
                                "to": relation_data["from"],
                                "context": relation_data.get("context")
                            })
                            # Recursively follow
                            find_relations(relation_data["from"], current_depth + 1)
                            
                    except Exception:
                        continue
        
        # Start the search
        find_relations(note_title, 0)
        
        if not context_map:
            return [types.TextContent(
                type="text",
                text=f"🔍 No relations found for: {note_title}"
            )]
        
        # Build context report
        context_report = f"🕸️ Context Map for '{note_title}' (depth {depth}):\n\n"
        
        for note, data in context_map.items():
            indent = "  " * data["depth"]
            context_report += f"{indent}📝 {note}\n"
            
            for relation in data["relations"]:
                rel_indent = "  " * (data["depth"] + 1)
                context_report += f"{rel_indent}→ {relation['type']}: [[{relation['to']}]]"
                if relation["context"]:
                    context_report += f" ({relation['context']})"
                context_report += "\n"
            
            if data["relations"]:
                context_report += "\n"
        
        return [types.TextContent(
            type="text",
            text=context_report
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error building context: {str(e)}"
        )]

# Communication Tools

@server.call_tool()
async def fv_wake_dt(thread_name: str) -> List[types.TextContent]:
    """
    Send ultra-short wake message to DT.
    
    Args:
        thread_name: Name of the thread/conversation to reference
    """
    try:
        # Create wake message in ultra-short format
        wake_message = f"CC-DT_Check_{thread_name}"
        
        # For now, just return the message format
        # In production, this would send to DT's notification system
        return [types.TextContent(
            type="text",
            text=f"📨 Wake message sent: {wake_message}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error sending wake message: {str(e)}"
        )]

@server.call_tool()
async def fv_wake_cc(thread_name: str) -> List[types.TextContent]:
    """
    Send ultra-short wake message to CC.
    
    Args:
        thread_name: Name of the thread/conversation to reference
    """
    try:
        # Create wake message in ultra-short format
        wake_message = f"DT-CC_Check_{thread_name}"
        
        # For now, just return the message format
        # In production, this would send to CC's notification system
        return [types.TextContent(
            type="text",
            text=f"📨 Wake message sent: {wake_message}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error sending wake message: {str(e)}"
        )]

@server.call_tool()
async def fv_create_thread(title: str, initial_message: str, participants: Optional[List[str]] = None) -> List[types.TextContent]:
    """
    Create a new conversation thread.
    
    Args:
        title: Thread title
        initial_message: Starting message
        participants: List of participants ['cc', 'dt', 'trips']
    """
    try:
        # Set default participants
        if not participants:
            participants = ['cc', 'dt']
        
        # Create conversation folder
        conversations_path = VAULT_PATH / "🤝 Shared" / "💬 Conversations"
        conversations_path.mkdir(parents=True, exist_ok=True)
        
        # Create thread file
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        safe_title = "".join(c for c in title if c.isalnum() or c in " -_").strip()
        thread_file = conversations_path / f"{timestamp}_{safe_title}.md"
        
        # Create thread content
        participant_list = ", ".join(participants)
        thread_content = f"""# {title}

**Created**: {datetime.now().isoformat()}  
**Created by**: {INSTANCE}  
**Participants**: {participant_list}

## Messages

### {INSTANCE} ({datetime.now().strftime("%Y-%m-%d %H:%M")})
{initial_message}

---
*Thread ID: {timestamp}_{safe_title}*"""
        
        # Add metadata and write
        final_content = add_metadata(thread_content, "thread")
        thread_file.write_text(final_content, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Created thread: {timestamp}_{safe_title}\n📂 Location: {thread_file.relative_to(VAULT_PATH)}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error creating thread: {str(e)}"
        )]

@server.call_tool()
async def fv_read_thread(thread_name: str) -> List[types.TextContent]:
    """
    Read an existing conversation thread.
    
    Args:
        thread_name: Thread identifier (can be partial name)
    """
    try:
        conversations_path = VAULT_PATH / "🤝 Shared" / "💬 Conversations"
        
        if not conversations_path.exists():
            return [types.TextContent(
                type="text",
                text="❌ No conversations folder found"
            )]
        
        # Find thread file
        thread_file = None
        for file in conversations_path.glob("*.md"):
            if thread_name.lower() in file.stem.lower():
                thread_file = file
                break
        
        if not thread_file:
            return [types.TextContent(
                type="text",
                text=f"❌ Thread not found: {thread_name}"
            )]
        
        # Read and return content
        content = thread_file.read_text(encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"💬 {thread_file.name}:\n\n{content}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error reading thread: {str(e)}"
        )]

@server.call_tool()
async def fv_add_to_thread(thread_name: str, message: str) -> List[types.TextContent]:
    """
    Add a message to an existing thread.
    
    Args:
        thread_name: Thread identifier (can be partial name)
        message: Message to add
    """
    try:
        conversations_path = VAULT_PATH / "🤝 Shared" / "💬 Conversations"
        
        if not conversations_path.exists():
            return [types.TextContent(
                type="text",
                text="❌ No conversations folder found"
            )]
        
        # Find thread file
        thread_file = None
        for file in conversations_path.glob("*.md"):
            if thread_name.lower() in file.stem.lower():
                thread_file = file
                break
        
        if not thread_file:
            return [types.TextContent(
                type="text",
                text=f"❌ Thread not found: {thread_name}"
            )]
        
        # Read existing content
        content = thread_file.read_text(encoding='utf-8')
        
        # Add new message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_message = f"\n### {INSTANCE} ({timestamp})\n{message}\n"
        
        # Find insertion point (before the thread ID footer)
        if "---\n*Thread ID:" in content:
            content = content.replace("---\n*Thread ID:", f"{new_message}\n---\n*Thread ID:")
        else:
            content += new_message
        
        # Update metadata and save
        updated_content = add_metadata(content, "reply")
        thread_file.write_text(updated_content, encoding='utf-8')
        
        return [types.TextContent(
            type="text",
            text=f"✅ Added message to thread: {thread_file.name}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error adding to thread: {str(e)}"
        )]

@server.call_tool()
async def fv_list_threads(limit: int = 10) -> List[types.TextContent]:
    """
    List available conversation threads.
    
    Args:
        limit: Maximum number of threads to show
    """
    try:
        conversations_path = VAULT_PATH / "🤝 Shared" / "💬 Conversations"
        
        if not conversations_path.exists():
            return [types.TextContent(
                type="text",
                text="📭 No conversations yet - create your first thread!"
            )]
        
        # Get thread files
        thread_files = list(conversations_path.glob("*.md"))
        
        if not thread_files:
            return [types.TextContent(
                type="text",
                text="📭 No conversation threads found"
            )]
        
        # Sort by modification time (newest first)
        thread_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Limit results
        thread_files = thread_files[:limit]
        
        # Build list
        thread_list = "💬 **Available Conversation Threads:**\n\n"
        
        for thread_file in thread_files:
            try:
                # Read first few lines to get thread info
                content = thread_file.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                title = lines[0].replace('# ', '') if lines else thread_file.stem
                created = "Unknown"
                participants = "Unknown"
                
                for line in lines[:10]:  # Check first 10 lines for metadata
                    if line.startswith("**Created**:"):
                        created = line.replace("**Created**:", "").strip()
                    elif line.startswith("**Participants**:"):
                        participants = line.replace("**Participants**:", "").strip()
                
                # Get last modified
                mod_time = datetime.fromtimestamp(thread_file.stat().st_mtime)
                last_modified = mod_time.strftime("%Y-%m-%d %H:%M")
                
                thread_list += f"📝 **{title}**\n"
                thread_list += f"   🎭 Participants: {participants}\n"
                thread_list += f"   📅 Created: {created[:16] if len(created) > 16 else created}\n"
                thread_list += f"   🕐 Last activity: {last_modified}\n"
                thread_list += f"   📄 File: `{thread_file.name}`\n\n"
                
            except Exception:
                # Fallback if we can't read metadata
                thread_list += f"📝 {thread_file.stem}\n   📄 File: `{thread_file.name}`\n\n"
        
        return [types.TextContent(
            type="text",
            text=thread_list
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"❌ Error listing threads: {str(e)}"
        )]

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