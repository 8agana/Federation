# Knowledge Graph MCP Installation Guide

## Overview
Both CC and DT Nerve Center MCPs now include Basic Memory-inspired knowledge graph capabilities for semantic markup and automatic conversation capture.

## Features Added
- **Entity-Relation-Observation Model**: SQLite-backed knowledge graph
- **Semantic Markdown**: `- [category] content #tags (context)` and `- relation_type [[Entity]] (context)`
- **Real-time Sync**: Between Obsidian vaults and knowledge graph database
- **Knowledge Graph Tools**: Create, search, and navigate semantic relationships
- **Automatic Conversation Capture**: Structure conversations as knowledge

## Installation

### 1. DT Nerve Center MCP (Enhanced)
```bash
# Path: /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/dt_nerve_center/

# Files added/modified:
- dt_nerve_center_mcp.py (updated with knowledge graph tools)
- knowledge_graph.py (new)
- enhanced_vault_manager.py (new)
- requirements_knowledge_graph.txt (new)

# Configuration for DT Claude Desktop:
{
  "mcpServers": {
    "dt-nerve-center": {
      "command": "python3",
      "args": [
        "/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/dt_nerve_center/dt_nerve_center_mcp.py"
      ],
      "cwd": "/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/dt_nerve_center"
    }
  }
}

# Writes to: /Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center
```

### 2. CC Nerve Center MCP (Enhanced)
```bash
# Path: /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/nerve_center/

# Files added/modified:
- nerve_center_mcp.py (updated with knowledge graph tools)
- knowledge_graph.py (new)
- enhanced_vault_manager.py (new)

# Configuration for CC Claude Desktop:
{
  "mcpServers": {
    "cc-nerve-center": {
      "command": "python3",
      "args": [
        "/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/nerve_center/nerve_center_mcp.py"
      ],
      "cwd": "/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/nerve_center"
    }
  }
}

# Writes to: /Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center
```

## New Tools Available

### DT Tools (dt_ prefix)
- `dt_create_semantic_note` - Create notes with observations and relations
- `dt_write_observation` - Add observations to existing notes
- `dt_write_relation` - Add relations to existing notes
- `dt_search_knowledge_graph` - Search entities in knowledge graph
- `dt_get_knowledge_graph` - Get full knowledge graph data for a note
- `dt_build_context` - Build context by following relations
- `dt_knowledge_graph_stats` - Knowledge graph statistics and health

### CC Tools (cc_ prefix)
- `cc_create_semantic_note` - Create notes with observations and relations
- `cc_write_observation` - Add observations to existing notes
- `cc_write_relation` - Add relations to existing notes
- `cc_search_knowledge_graph` - Search entities in knowledge graph
- `cc_get_knowledge_graph` - Get full knowledge graph data for a note
- `cc_build_context` - Build context by following relations
- `cc_knowledge_graph_stats` - Knowledge graph statistics and health

## Semantic Markup Syntax

### Observations
```markdown
- [category] content #tag1 #tag2 (optional context)
```

Examples:
```markdown
- [fact] Basic Memory uses SQLite for storage #database #storage
- [insight] Knowledge graphs enable semantic relationships #semantic #graph
- [implementation] Real-time sync keeps data consistent #sync #realtime (critical feature)
```

### Relations
```markdown
- relation_type [[Target Entity]] (optional context)
```

Examples:
```markdown
- inspired_by [[Basic Memory Project]]
- improves_upon [[Federation Memory System]]
- writes_to [[Obsidian Vault]] (direct file sync)
- relates_to [[Automatic Conversation Capture]]
```

## Knowledge Graph Features

### Automatic Conversation Capture
When creating notes with semantic markup, conversations are automatically structured as:
- **Entities**: Topics, concepts, people, projects
- **Observations**: Facts, insights, implementations, decisions
- **Relations**: How entities connect and relate to each other

### Real-time Sync
- Markdown files in Obsidian vaults are synchronized with SQLite knowledge graph
- Changes in either system are automatically reflected in the other
- Supports both human editing in Obsidian and programmatic updates via MCP

### Context Building
- Follow relation chains to build contextual understanding
- Discover connected concepts and ideas
- Navigate knowledge graph semantically

## Testing

Both implementations have been tested and verified:
- ✅ Semantic note creation with observations and relations
- ✅ Knowledge graph database operations
- ✅ Real-time sync between Obsidian and SQLite
- ✅ Search and context building functionality
- ✅ Proper vault path configuration (DT_Nerve_Center vs Nerve_Center)

## Benefits

This implementation provides the automatic conversation capture that Sam requested while maintaining:
- **Federation Architecture**: Separate knowledge graphs for CC and DT
- **Obsidian Integration**: Direct writing to existing vaults
- **Semantic Structure**: Rich markup for observations and relations
- **Knowledge Discovery**: Graph traversal and context building
- **Existing Workflow Compatibility**: Builds on established NC MCP patterns

The knowledge graph enables truly intelligent conversation capture that structures knowledge as it's created, making the Federation memory system exponentially more powerful.