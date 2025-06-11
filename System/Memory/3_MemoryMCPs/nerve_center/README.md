# CC Nerve Center MCP

## Overview
CC's personal Obsidian workspace for action-oriented thinking, experimentation, and personal knowledge management.

## Purpose
This MCP provides CC with a dedicated personal space for:
- Personal note-taking and knowledge capture
- Experimental ideas and prototypes
- Private thinking and reflection
- Individual task tracking and personal organization

## Architecture
- **Personal Focus**: Pure personal tools, no collaboration features
- **Action-Oriented**: Designed for CC's "think through action" style
- **Isolated**: Separate from shared collaboration tools

## Vault Location
`/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center`

### Folder Structure
- 🧠 **Knowledge** - Accumulated wisdom and insights
- 💡 **Ideas** - Experimental concepts and prototypes
- 📊 **Decisions** - Decision logs and rationale
- 📅 **Daily_Notes** - Daily observations and reflections
- 🔄 **Active_Context** - Current focus areas
- 📦 **Archive** - Completed work and historical context

## Available Tools

### Core Note Operations
- `cc_create_note` - Create notes in personal vault
- `cc_read_note` - Read existing notes
- `cc_update_note` - Update note content
- `cc_search_notes` - Search across personal notes

### Advanced Features
- `cc_create_daily_note` - Create/update daily notes
- `cc_complete_task` - Complete tasks with mandatory checklist
- `cc_move_note` - Move notes between folders
- `cc_update_checkbox` - Toggle checkboxes in notes

### Memory Integration
- `cc_memory_to_note` - Convert ChromaDB memories to notes
- `cc_note_to_memory` - Convert notes to searchable memories
- `cc_sync_to_obsidian` - Sync important memories to notes

## Usage Examples

### Create a Personal Note
```python
cc_create_note(
    title="New Experiment Idea",
    content="Testing a new approach to...",
    folder="💡 Ideas",
    tags=["experiment", "prototype"]
)
```

### Daily Reflection
```python
cc_create_daily_note(
    summary="Productive day working on federation architecture",
    events=[
        {"time": "09:00", "description": "Fixed memory MCPs", "details": "Resolved import errors"},
        {"time": "14:00", "description": "Built DT Nerve Center", "details": "Complete analytical workspace"}
    ]
)
```

### Memory to Note Conversion
```python
cc_memory_to_note(
    memory_id="cc_20250609_160716_ff751483",
    folder="🧠 Knowledge"
)
```

## Integration Points

### With Memory System
- Bidirectional conversion between memories and notes
- Sync important memories for deeper analysis
- Personal knowledge base building

### With Federation
- **No direct collaboration tools** (moved to TaskTracker MCP)
- Pure personal workspace
- Maintains independence while allowing shared work through other MCPs

## Configuration

Add to CC's MCP configuration:
```json
"cc-nerve-center": {
    "command": "python3",
    "args": ["/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/nerve_center/run_server.py"],
    "env": {
        "PYTHONUNBUFFERED": "1"
    }
}
```

## Design Philosophy

### Personal Autonomy
- "Your own room for the first time" - CC's independent thinking space
- Self-organized according to CC's mental model
- Freedom to experiment without affecting shared work

### Action-Oriented Design
- Tools designed for CC's "doing reveals understanding" approach
- Quick capture and iteration capabilities
- Supports experimental workflows

### Clean Separation
- Personal tools only - no wake commands or shared vault access
- Clear boundary between personal and collaborative work
- Collaboration happens through dedicated TaskTracker MCP

## Files
- `nerve_center_mcp.py` - Main MCP server
- `vault_manager.py` - Obsidian vault operations
- `run_server.py` - Server entry point

## Status
✅ **Active** - Fully functional personal workspace for CC

---
*Created: June 9, 2025*
*Part of Federation Memory System v3*