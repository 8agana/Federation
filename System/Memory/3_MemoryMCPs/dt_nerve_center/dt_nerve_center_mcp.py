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
logger = logging.getLogger("dt_nerve_center_mcp")

# Initialize MCP server
server = Server("dt-nerve-center")

# Global vault manager instance
vault_manager: Optional[EnhancedVaultManager] = None


def get_vault_manager() -> EnhancedVaultManager:
    """Get or initialize the enhanced vault manager with knowledge graph"""
    global vault_manager
    if vault_manager is None:
        vault_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        vault_manager = EnhancedVaultManager(vault_path)
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
        ),
        types.Tool(
            name="dt_create_semantic_note",
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
            name="dt_write_observation",
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
            name="dt_write_relation",
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
            name="dt_search_knowledge_graph",
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
            name="dt_get_knowledge_graph",
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
            name="dt_build_context",
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
            name="dt_knowledge_graph_stats",
            description="Get knowledge graph statistics and health",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
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
        
        elif name == "dt_create_semantic_note":
            vault = get_vault_manager()
            note_path = vault.create_semantic_note(
                title=arguments["title"],
                observations=arguments.get("observations", []),
                relations=arguments.get("relations", []),
                folder=arguments.get("folder", "🧠 Knowledge"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Semantic note created: {note_path}"
            )]
        
        elif name == "dt_write_observation":
            vault = get_vault_manager()
            success = vault.write_observation(
                note_title=arguments["note_title"],
                category=arguments["category"],
                content=arguments["content"],
                tags=arguments.get("tags", []),
                context=arguments.get("context", "")
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Observation added to '{arguments['note_title']}'"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to add observation to '{arguments['note_title']}'"
                )]
        
        elif name == "dt_write_relation":
            vault = get_vault_manager()
            success = vault.write_relation(
                note_title=arguments["note_title"],
                relation_type=arguments["relation_type"],
                to_name=arguments["to_name"],
                context=arguments.get("context", "")
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Relation added to '{arguments['note_title']}'"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to add relation to '{arguments['note_title']}'"
                )]
        
        elif name == "dt_search_knowledge_graph":
            vault = get_vault_manager()
            results = vault.search_knowledge_graph(arguments["query"])
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No entities found matching '{arguments['query']}'"
                )]
            
            output = [f"Found {len(results)} entities:\n"]
            for result in results:
                output.append(f"📄 {result['title']} ({result['entity_type']})")
                output.append(f"   Permalink: {result['permalink']}")
                if result['file_path']:
                    output.append(f"   Path: {result['file_path']}")
                output.append("")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "dt_get_knowledge_graph":
            vault = get_vault_manager()
            kg_data = vault.get_note_knowledge_graph(arguments["note_title"])
            
            if not kg_data:
                return [types.TextContent(
                    type="text",
                    text=f"No knowledge graph data found for '{arguments['note_title']}'"
                )]
            
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
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "dt_build_context":
            vault = get_vault_manager()
            context = vault.build_context_from_relations(
                note_title=arguments["note_title"],
                depth=arguments.get("depth", 2)
            )
            
            if not context or not context.get('entities'):
                return [types.TextContent(
                    type="text",
                    text=f"No context found for '{arguments['note_title']}'"
                )]
            
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
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "dt_knowledge_graph_stats":
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
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
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