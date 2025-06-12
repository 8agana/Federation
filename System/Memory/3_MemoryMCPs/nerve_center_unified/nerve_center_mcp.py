#!/usr/bin/env python3
"""
Unified Nerve Center MCP - Knowledge Graph Only
Simplified from 36 tools to 6 essential knowledge graph tools
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nerve_center_unified")

# Initialize MCP server
server = Server("nerve-center-unified")

# Get instance from environment variable
INSTANCE = os.environ.get("NERVE_CENTER_INSTANCE", "cc").lower()
if INSTANCE not in ["cc", "dt"]:
    logger.error(f"Invalid NERVE_CENTER_INSTANCE: {INSTANCE}. Must be 'cc' or 'dt'")
    sys.exit(1)

# Vault paths based on instance
VAULT_PATHS = {
    "cc": Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center"),
    "dt": Path("/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center")
}

VAULT_PATH = VAULT_PATHS[INSTANCE]
logger.info(f"Initialized Nerve Center for instance: {INSTANCE}")
logger.info(f"Using vault: {VAULT_PATH}")

# Knowledge Graph folder
KG_FOLDER = VAULT_PATH / "🧠 Knowledge Graph"


def ensure_folder_exists(folder: Path) -> None:
    """Ensure a folder exists, create if not"""
    folder.mkdir(parents=True, exist_ok=True)


def parse_note_content(content: str) -> Dict[str, Any]:
    """Parse note content to extract observations and relations"""
    lines = content.split('\n')
    observations = []
    relations = []
    
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        if line == "## Observations":
            current_section = "observations"
        elif line == "## Relations":
            current_section = "relations"
        elif line.startswith("### ") and current_section == "observations":
            # Start of an observation category
            category = line[4:]
            observations.append({"category": category, "items": []})
        elif line.startswith("- ") and current_section == "observations" and observations:
            # Observation item
            observations[-1]["items"].append(line[2:])
        elif line.startswith("- ") and current_section == "relations":
            # Relation item
            if " -> " in line:
                parts = line[2:].split(" -> ", 1)
                if len(parts) == 2:
                    relation_type, target = parts
                    relations.append({
                        "type": relation_type.strip(),
                        "target": target.strip()
                    })
    
    return {
        "observations": observations,
        "relations": relations
    }


def build_semantic_content(title: str, observations: List[Dict], relations: List[Dict], 
                         tags: List[str] = None, metadata: Dict = None) -> str:
    """Build semantic note content with observations and relations"""
    content = f"# {title}\n\n"
    
    # Metadata section
    if metadata or tags:
        content += "---\n"
        if tags:
            content += f"tags: {', '.join(tags)}\n"
        if metadata:
            for key, value in metadata.items():
                content += f"{key}: {value}\n"
        content += "---\n\n"
    
    # Observations section
    if observations:
        content += "## Observations\n\n"
        for obs in observations:
            content += f"### {obs['category']}\n"
            for item in obs.get('items', [obs.get('content', '')]):
                if isinstance(item, str):
                    content += f"- {item}\n"
            content += "\n"
    
    # Relations section
    if relations:
        content += "## Relations\n\n"
        for rel in relations:
            content += f"- {rel['relation_type']} -> {rel['to_name']}"
            if rel.get('context'):
                content += f" ({rel['context']})"
            content += "\n"
    
    return content


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available knowledge graph tools"""
    return [
        types.Tool(
            name="NC_create_semantic_note",
            description="Create a note with semantic markup (observations and relations)",
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
                                "items": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of observation items"
                                }
                            },
                            "required": ["category"]
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
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for the note"},
                    "metadata": {"type": "object", "description": "Additional metadata"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="NC_write_observation",
            description="Add an observation to an existing note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Title of the note to update"},
                    "category": {"type": "string", "description": "Observation category"},
                    "content": {"type": "string", "description": "Observation content"}
                },
                "required": ["note_title", "category", "content"]
            }
        ),
        types.Tool(
            name="NC_write_relation",
            description="Add a relation to an existing note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Title of the note to update"},
                    "relation_type": {"type": "string", "description": "Type of relation"},
                    "to_name": {"type": "string", "description": "Target entity name"},
                    "context": {"type": "string", "description": "Optional context"}
                },
                "required": ["note_title", "relation_type", "to_name"]
            }
        ),
        types.Tool(
            name="NC_search_knowledge_graph",
            description="Search for entities in the knowledge graph",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="NC_get_knowledge_graph",
            description="Get knowledge graph data for a specific note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Title of the note"}
                },
                "required": ["note_title"]
            }
        ),
        types.Tool(
            name="NC_build_context",
            description="Build context by following relations from a note",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "Starting note title"},
                    "depth": {"type": "integer", "description": "How many levels of relations to follow", "default": 2}
                },
                "required": ["note_title"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    ensure_folder_exists(KG_FOLDER)
    
    if name == "NC_create_semantic_note":
        title = arguments["title"]
        observations = arguments.get("observations", [])
        relations = arguments.get("relations", [])
        tags = arguments.get("tags", [])
        metadata = arguments.get("metadata", {})
        
        # Build content
        content = build_semantic_content(title, observations, relations, tags, metadata)
        
        # Save note
        file_path = KG_FOLDER / f"{title}.md"
        file_path.write_text(content)
        
        return [types.TextContent(
            type="text",
            text=f"Created semantic note '{title}' in Knowledge Graph folder with {len(observations)} observations and {len(relations)} relations"
        )]
    
    elif name == "NC_write_observation":
        note_title = arguments["note_title"]
        category = arguments["category"]
        content = arguments["content"]
        
        file_path = KG_FOLDER / f"{note_title}.md"
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"Note '{note_title}' not found in Knowledge Graph folder"
            )]
        
        # Read existing content
        existing = file_path.read_text()
        
        # Find or create observations section
        if "## Observations" not in existing:
            existing += "\n## Observations\n\n"
        
        # Find category or create it
        category_header = f"### {category}"
        if category_header in existing:
            # Add to existing category
            lines = existing.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == category_header:
                    # Find next section or end
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith('#'):
                        j += 1
                    lines.insert(j - 1, f"- {content}")
                    existing = '\n'.join(lines)
                    break
        else:
            # Add new category
            obs_index = existing.find("## Observations")
            next_section = existing.find("## Relations", obs_index)
            if next_section == -1:
                existing += f"\n{category_header}\n- {content}\n"
            else:
                insert_point = existing.rfind('\n', obs_index, next_section)
                existing = existing[:insert_point] + f"\n{category_header}\n- {content}\n" + existing[insert_point:]
        
        file_path.write_text(existing)
        
        return [types.TextContent(
            type="text",
            text=f"Added observation to '{note_title}' under category '{category}'"
        )]
    
    elif name == "NC_write_relation":
        note_title = arguments["note_title"]
        relation_type = arguments["relation_type"]
        to_name = arguments["to_name"]
        context = arguments.get("context", "")
        
        file_path = KG_FOLDER / f"{note_title}.md"
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"Note '{note_title}' not found in Knowledge Graph folder"
            )]
        
        # Read existing content
        existing = file_path.read_text()
        
        # Find or create relations section
        if "## Relations" not in existing:
            existing += "\n## Relations\n\n"
        
        # Add relation
        relation_line = f"- {relation_type} -> {to_name}"
        if context:
            relation_line += f" ({context})"
        
        relations_index = existing.find("## Relations")
        next_section_start = existing.find("\n#", relations_index + 1)
        
        if next_section_start == -1:
            existing += f"{relation_line}\n"
        else:
            insert_point = existing.rfind('\n', relations_index, next_section_start)
            existing = existing[:insert_point] + f"\n{relation_line}" + existing[insert_point:]
        
        file_path.write_text(existing)
        
        return [types.TextContent(
            type="text",
            text=f"Added relation '{relation_type} -> {to_name}' to '{note_title}'"
        )]
    
    elif name == "NC_search_knowledge_graph":
        query = arguments["query"].lower()
        results = []
        
        # Search through all notes in KG folder
        for file_path in KG_FOLDER.glob("*.md"):
            try:
                content = file_path.read_text()
                title = file_path.stem
                score = 0
                
                # Title match (higher weight)
                if query in title.lower():
                    score += 10
                
                # Content match
                content_lower = content.lower()
                if query in content_lower:
                    score += 5
                    # Bonus for multiple occurrences
                    score += content_lower.count(query) - 1
                
                # Fuzzy matching for single words
                if len(query.split()) == 1 and len(query) > 3:
                    # Check if any word in content starts with query
                    words = content_lower.split()
                    for word in words:
                        if word.startswith(query):
                            score += 2
                            break
                
                if score > 0:
                    # Parse to get summary
                    parsed = parse_note_content(content)
                    obs_count = sum(len(obs.get('items', [])) for obs in parsed['observations'])
                    rel_count = len(parsed['relations'])
                    
                    # Find matching context
                    lines = content.split('\n')
                    context_lines = []
                    for i, line in enumerate(lines):
                        if query in line.lower() and len(context_lines) < 2:
                            context_lines.append(f"  > {line.strip()}")
                    
                    result_text = f"- **{title}** (score: {score}): {obs_count} observations, {rel_count} relations"
                    if context_lines:
                        result_text += "\n" + "\n".join(context_lines)
                    
                    results.append((score, result_text))
            except Exception as e:
                logger.warning(f"Error searching {file_path}: {e}")
                continue
        
        # Sort by score descending
        results.sort(reverse=True, key=lambda x: x[0])
        
        if not results:
            # Provide helpful message
            return [types.TextContent(
                type="text",
                text=f"No results found for '{query}' in Knowledge Graph.\n\nTip: The Knowledge Graph folder may be empty. Create semantic notes with NC_create_semantic_note first."
            )]
        
        # Format results without scores
        formatted_results = [r[1] for r in results[:10]]  # Top 10 results
        
        return [types.TextContent(
            type="text",
            text=f"Found {len(results)} notes matching '{query}':\n\n" + '\n\n'.join(formatted_results)
        )]
    
    elif name == "NC_get_knowledge_graph":
        note_title = arguments["note_title"]
        file_path = KG_FOLDER / f"{note_title}.md"
        
        if not file_path.exists():
            return [types.TextContent(
                type="text",
                text=f"Note '{note_title}' not found in Knowledge Graph folder"
            )]
        
        content = file_path.read_text()
        parsed = parse_note_content(content)
        
        # Format output
        output = f"# Knowledge Graph: {note_title}\n\n"
        
        if parsed['observations']:
            output += "## Observations\n"
            for obs in parsed['observations']:
                output += f"- **{obs['category']}**: {len(obs.get('items', []))} items\n"
        
        if parsed['relations']:
            output += f"\n## Relations ({len(parsed['relations'])} total)\n"
            for rel in parsed['relations']:
                output += f"- {rel['type']} -> {rel['target']}\n"
        
        return [types.TextContent(type="text", text=output)]
    
    elif name == "NC_build_context":
        note_title = arguments["note_title"]
        depth = arguments.get("depth", 2)
        
        visited = set()
        context_notes = []
        
        async def explore_relations(title: str, current_depth: int):
            if current_depth > depth or title in visited:
                return
            
            visited.add(title)
            file_path = KG_FOLDER / f"{title}.md"
            
            if not file_path.exists():
                return
            
            content = file_path.read_text()
            parsed = parse_note_content(content)
            
            context_notes.append({
                "title": title,
                "depth": current_depth,
                "observations": len(parsed['observations']),
                "relations": parsed['relations']
            })
            
            # Follow relations
            for rel in parsed['relations']:
                target = rel['target']
                await explore_relations(target, current_depth + 1)
        
        await explore_relations(note_title, 0)
        
        # Format output
        output = f"# Context for: {note_title}\n\n"
        output += f"Explored {len(visited)} notes up to depth {depth}\n\n"
        
        for note in sorted(context_notes, key=lambda x: x['depth']):
            indent = "  " * note['depth']
            output += f"{indent}- **{note['title']}** ({note['observations']} observations)\n"
            for rel in note['relations']:
                output += f"{indent}  → {rel['type']} -> {rel['target']}\n"
        
        return [types.TextContent(type="text", text=output)]
    
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="nerve-center-unified",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())