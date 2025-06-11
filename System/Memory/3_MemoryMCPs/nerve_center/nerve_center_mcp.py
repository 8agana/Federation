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

# Import enhanced vault manager with knowledge graph
from enhanced_vault_manager import EnhancedVaultManager

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
vault_manager: Optional[EnhancedVaultManager] = None



def get_vault_manager() -> EnhancedVaultManager:
    """Get or initialize the enhanced vault manager with knowledge graph"""
    global vault_manager
    if vault_manager is None:
        try:
            vault_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center"
            vault_manager = EnhancedVaultManager(vault_path)
            logger.info("Enhanced Obsidian Vault Manager with Knowledge Graph initialized successfully")
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
        ),
        types.Tool(
            name="cc_create_semantic_note",
            description="Create note with semantic markup (observations and relations)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title"},
                    "observations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "category": {"type": "string", "description": "Observation category"},
                                "content": {"type": "string", "description": "Observation content"},
                                "tags": {"type": "array", "items": {"type": "string"}},
                                "context": {"type": "string", "description": "Optional context"}
                            },
                            "required": ["category", "content"]
                        },
                        "description": "List of observations"
                    },
                    "relations": {
                        "type": "array", 
                        "items": {
                            "type": "object",
                            "properties": {
                                "relation_type": {"type": "string", "description": "Type of relation"},
                                "to_name": {"type": "string", "description": "Target entity name"},
                                "context": {"type": "string", "description": "Optional context"}
                            },
                            "required": ["relation_type", "to_name"]
                        },
                        "description": "List of relations"
                    },
                    "folder": {"type": "string", "description": "Target folder", "default": "🧠 Knowledge"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the note"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="cc_write_observation",
            description="Add an observation to an existing note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Note to add observation to"},
                    "category": {"type": "string", "description": "Observation category"},
                    "content": {"type": "string", "description": "Observation content"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for observation"},
                    "context": {"type": "string", "description": "Optional context"}
                },
                "required": ["note_title", "category", "content"]
            }
        ),
        types.Tool(
            name="cc_write_relation",
            description="Add a relation to an existing note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Note to add relation to"},
                    "relation_type": {"type": "string", "description": "Type of relation"},
                    "to_name": {"type": "string", "description": "Target entity name"},
                    "context": {"type": "string", "description": "Optional context"}
                },
                "required": ["note_title", "relation_type", "to_name"]
            }
        ),
        types.Tool(
            name="cc_search_knowledge_graph",
            description="Search the knowledge graph for entities",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="cc_get_knowledge_graph",
            description="Get knowledge graph data for a specific note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Note title"}
                },
                "required": ["note_title"]
            }
        ),
        types.Tool(
            name="cc_build_context",
            description="Build context by following relations from a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Starting note"},
                    "depth": {"type": "number", "description": "How many relation levels to follow", "default": 2}
                },
                "required": ["note_title"]
            }
        ),
        types.Tool(
            name="cc_knowledge_graph_stats",
            description="Get knowledge graph statistics and health",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
        
        elif name == "cc_create_semantic_note":
            vault = get_vault_manager()
            note_path = vault.create_semantic_note(
                title=arguments["title"],
                observations=arguments.get("observations", []),
                relations=arguments.get("relations", []),
                folder=arguments.get("folder", "🧠 Knowledge"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            result = [types.TextContent(
                type="text",
                text=f"✅ Semantic note created: {note_path}"
            )]
        
        elif name == "cc_write_observation":
            vault = get_vault_manager()
            success = vault.write_observation(
                note_title=arguments["note_title"],
                category=arguments["category"],
                content=arguments["content"],
                tags=arguments.get("tags", []),
                context=arguments.get("context", "")
            )
            
            if success:
                result = [types.TextContent(
                    type="text",
                    text=f"✅ Observation added to '{arguments['note_title']}'"
                )]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Failed to add observation to '{arguments['note_title']}'"
                )]
        
        elif name == "cc_write_relation":
            vault = get_vault_manager()
            success = vault.write_relation(
                note_title=arguments["note_title"],
                relation_type=arguments["relation_type"],
                to_name=arguments["to_name"],
                context=arguments.get("context", "")
            )
            
            if success:
                result = [types.TextContent(
                    type="text",
                    text=f"✅ Relation added to '{arguments['note_title']}'"
                )]
            else:
                result = [types.TextContent(
                    type="text",
                    text=f"❌ Failed to add relation to '{arguments['note_title']}'"
                )]
        
        elif name == "cc_search_knowledge_graph":
            vault = get_vault_manager()
            results = vault.search_knowledge_graph(arguments["query"])
            
            if not results:
                result = [types.TextContent(
                    type="text",
                    text=f"No entities found matching '{arguments['query']}'"
                )]
            else:
                output = [f"Found {len(results)} entities:\n"]
                for search_result in results:
                    output.append(f"📄 {search_result['title']} ({search_result['entity_type']})")
                    output.append(f"   Permalink: {search_result['permalink']}")
                    if search_result['file_path']:
                        output.append(f"   Path: {search_result['file_path']}")
                    output.append("")
                
                result = [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "cc_get_knowledge_graph":
            vault = get_vault_manager()
            kg_data = vault.get_note_knowledge_graph(arguments["note_title"])
            
            if not kg_data:
                result = [types.TextContent(
                    type="text",
                    text=f"No knowledge graph data found for '{arguments['note_title']}'"
                )]
            else:
                output = [f"Knowledge Graph for '{arguments['note_title']}':\n"]
                
                entity = kg_data['entity']
                output.append(f"**Entity**: {entity['title']} ({entity['type']})")
                output.append(f"**Permalink**: {entity['permalink']}")
                output.append("")
                
                observations = kg_data['observations']
                if observations:
                    output.append("## Observations")
                    for obs in observations:
                        tags_str = ' '.join([f"#{tag}" for tag in obs['tags']]) if obs['tags'] else ""
                        line = f"- [{obs['category']}] {obs['content']}"
                        if tags_str:
                            line += f" {tags_str}"
                        if obs['context']:
                            line += f" ({obs['context']})"
                        output.append(line)
                    output.append("")
                
                relations = kg_data['relations']
                if relations:
                    output.append("## Relations")
                    for rel in relations:
                        line = f"- {rel['relation_type']} [[{rel['to_name']}]]"
                        if rel['context']:
                            line += f" ({rel['context']})"
                        if not rel['resolved']:
                            line += " ⚠️ (unresolved)"
                        output.append(line)
                
                result = [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "cc_build_context":
            vault = get_vault_manager()
            context = vault.build_context_from_relations(
                note_title=arguments["note_title"],
                depth=arguments.get("depth", 2)
            )
            
            if not context or not context.get('entities'):
                result = [types.TextContent(
                    type="text",
                    text=f"No context found for '{arguments['note_title']}'"
                )]
            else:
                output = [f"Context for '{context['root']}' (depth {context['depth']}):\n"]
                
                # Group entities by depth
                by_depth = {}
                for entity_id, entity in context['entities'].items():
                    depth = entity['depth']
                    if depth not in by_depth:
                        by_depth[depth] = []
                    by_depth[depth].append(entity)
                
                # Display by depth level
                for depth in sorted(by_depth.keys()):
                    output.append(f"### Depth {depth}")
                    for entity in by_depth[depth]:
                        output.append(f"- {entity['title']} ({entity['type']})")
                    output.append("")
                
                # Show relations
                if context['relations']:
                    output.append("### Relations")
                    for rel in context['relations'][:20]:  # Limit display
                        from_entity = context['entities'].get(rel['from_id'], {})
                        from_title = from_entity.get('title', f"ID:{rel['from_id']}")
                        output.append(f"- {from_title} → {rel['relation_type']} → {rel['to_name']}")
                        if rel['context']:
                            output.append(f"  Context: {rel['context']}")
                
                result = [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "cc_knowledge_graph_stats":
            vault = get_vault_manager()
            stats = vault.get_knowledge_graph_stats()
            
            output = ["📊 Knowledge Graph Statistics:\n"]
            output.append(f"**Entities**: {stats['entities']:,}")
            output.append(f"**Observations**: {stats['observations']:,}")
            output.append(f"**Relations**: {stats['relations']:,}")
            output.append(f"**Unresolved Relations**: {stats['unresolved_relations']:,}")
            
            if stats['unresolved_relations'] > 0:
                output.append("\n💡 Use relation resolution to link unresolved relations")
                # Auto-resolve relations
                resolved_count = vault.resolve_unresolved_relations()
                if resolved_count > 0:
                    output.append(f"✅ Automatically resolved {resolved_count} relations")
            
            result = [types.TextContent(type="text", text="\n".join(output))]
        
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