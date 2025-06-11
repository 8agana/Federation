# TaskTracker MCP - Complete Documentation
## AI-Human Collaborative Task Management System

**Status:** Production Ready  
**Version:** 2.0  
**Last Updated:** 2025-06-08

---

## Overview

TaskTracker MCP is a conversation-first task management system designed for AI-human collaboration. It captures the complete narrative evolution of ideas from inception to implementation, with integrated communication tools and quality gates.

### Core Features

- **Task Management**: Create, track, and organize tasks with chronological entries
- **Project Phylogeny**: Git-like task relationships (spawn, fork, merge, symbiosis, mutation)
- **Completion Checklist**: Quality gates ensuring documentation, memory creation, and cleanup
- **Wake Messaging**: Integrated CC↔DT communication tools
- **Auto-Organization**: Automatic folder movement (Complete, Backburner)
- **Federation Ready**: Shared across CC and DT instances

---

## MCP Tools Reference

### Core Task Operations

#### `create_task`
Create a new task with foundation entry.

**Parameters:**
- `title` (required): Task title
- `description` (required): Task description  
- `participants` (optional): List of participants
- `metadata` (optional): Additional metadata (priority, tags, estimated_effort)

**Example:**
```
create_task(
  title="Implement Auto-Save Feature",
  description="Add automatic conversation saving to prevent context loss",
  participants=["CC", "DT", "Sam"],
  metadata={"priority": "high", "tags": ["memory", "core"]}
)
```

#### `add_task_entry`
Add chronological entry to existing task.

**Parameters:**
- `task_id` (required): Task ID to add entry to
- `entry_type` (required): discussion, implementation, progress, complete
- `content` (required): Entry content
- `participants` (optional): Participants for this entry
- `metadata` (optional): Additional metadata

#### `get_task_details`
Get complete task details including all entries.

#### `list_active_tasks`
List all active (non-complete) tasks.

#### `update_task_status`
Update task status and optionally phase.

**Parameters:**
- `task_id` (required): Task ID to update
- `new_status` (required): foundation, active, blocked, complete, cancelled, backburner
- `phase` (optional): planning, discussing, implementing, testing, complete

### Quality Control

#### `complete_task_with_checklist`
Complete a task with mandatory quality checklist.

**Parameters:**
- `task_id` (required): Task ID to complete
- `documentation_done` (required): Documentation completed? (reminder only)
- `documentation_path` (optional): Path to documentation if done
- `memory_hash` (required): ChromaDB memory hash - MANDATORY
- `cleanup_done` (required): Cleanup/organization done? Must be true
- `tags` (optional): Tags for ChromaDB integration
- `metadata` (optional): Additional metadata
- `completion_notes` (optional): Completion notes

**Quality Gates:**
- ✅ Memory creation is REQUIRED (must provide memory_hash)
- ✅ Cleanup must be confirmed (cleanup_done=true)
- ✅ Documentation serves as reminder (not required but tracked)

### Communication Tools

#### `wake_dt`
Send wake message to Desktop Claude.

**Parameters:**
- `message` (required): Message to send (no quotes/apostrophes)
- `task_id` (optional): Task ID for context

#### `wake_cc`
Send wake message to Claude Code.

**Parameters:**
- `message` (required): Message to send (no quotes/apostrophes)  
- `task_id` (optional): Task ID for context

#### `auto_wake_config`
Configure automatic wake messages on task updates.

**Parameters:**
- `enabled` (required): Enable/disable auto-wake
- `target` (optional): "dt", "cc", or "both"
- `triggers` (optional): Array of ["create", "update", "complete", "status_change"]

**Default:** Auto-wake is DISABLED by default and must be manually enabled.

#### `get_wake_status`
Get current wake message configuration and status.

---

## Task Organization

### Automatic Folder Structure

```
/Federation/Tasks/
├── [active tasks]               # Tasks in foundation/active/blocked status
├── Complete/                    # Automatically moved when status = complete
│   └── [completed tasks]        
├── Backburner/                  # Automatically moved when status = backburner
│   └── [deferred tasks]
├── manifest.json               # Global task index
└── relationships.json          # Task relationship tracking
```

### Task Lifecycle

1. **Foundation** → Initial idea captured with basic details
2. **Active** → Work in progress with regular updates  
3. **Blocked** → Waiting on dependencies or decisions
4. **Complete** → Finished with required checklist (auto-moved to Complete/)
5. **Backburner** → Deferred for later (auto-moved to Backburner/)
6. **Cancelled** → No longer needed

### Project Phylogeny System

TaskTracker includes a revolutionary relationship tracking system based on evolutionary biology:

- **Spawn**: Parent task creates child task (most common)
- **Fork**: Alternative approaches to same problem
- **Merge**: Multiple tasks combine into one
- **Symbiosis**: Tasks that benefit each other
- **Mutation**: Unexpected evolution of task scope

Example phylogeny tree:
```
Federation Upgrade (parent)
├── Token Tracking (spawn)
├── Auto-Save System (spawn)  
├── Wake Scripts (spawn)
│   └── TaskTracker Integration (spawn)
└── Photography MCP (fork - different approach)
```

---

## Wake Message Integration

### Message Sanitization

All wake messages are automatically sanitized to prevent bash script syntax errors:
- Removes single and double quotes
- Removes backticks and dollar signs
- Limits message length
- Preserves meaning while ensuring script safety

### Auto-Wake Configuration

Auto-wake is **disabled by default** to prevent spam. Enable selectively:

```
auto_wake_config(
  enabled=true,
  target="dt",
  triggers=["complete", "status_change"]
)
```

### Wake Scripts Used

- **DT Wake**: `/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/Shared_Federation/Scripts/wake_desktop_claude.sh`
- **CC Wake**: `/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/Shared_Federation/Scripts/wake_claude_code.sh`

---

## Implementation Architecture

### Core Components

- **`tasktracker_mcp.py`** - Main MCP server with tool definitions
- **`task_operations.py`** - Core task management logic  
- **`task_relationships.py`** - Project phylogeny engine
- **`wake_manager.py`** - Wake message handling and sanitization

### Configuration Files

- **`wake_config.json`** - Wake message configuration (auto-created)
- **`manifest.json`** - Global task index
- **`relationships.json`** - Task relationship tracking

### Task Directory Structure

Each task creates a timestamped directory:

```
20250608_1750_Wake_Message_Integration_into_TaskTracker_MCP/
├── index.json                  # Task metadata
├── 20250608_1750_Foundation.json    # Initial entry
├── 20250608_1751_Discussion.json    # Design discussion
├── 20250608_1753_Implementation.json # Implementation details
└── 20250608_1756_Complete.json      # Completion entry
```

---

## Usage Examples

### Basic Workflow

1. **Create Task**
```
create_task(
  title="Add Database Indexing",
  description="Improve query performance for large datasets"
)
```

2. **Add Progress Updates**
```
add_task_entry(
  task_id="20250608_1800_Add_Database_Indexing", 
  entry_type="implementation",
  content="Added composite indexes on frequently queried columns"
)
```

3. **Complete with Quality Checklist**
```
complete_task_with_checklist(
  task_id="20250608_1800_Add_Database_Indexing",
  documentation_done=true,
  documentation_path="/docs/database-indexing.md",
  memory_hash="cc_20250608_180145_db_indexing_complete",
  cleanup_done=true,
  tags=["database", "performance", "optimization"]
)
```

### Communication Workflow

1. **Manual Wake Message**
```
wake_dt(
  message="Database indexing complete - ready for performance testing",
  task_id="20250608_1800_Add_Database_Indexing"
)
```

2. **Enable Auto-Wake for Task Completion**
```
auto_wake_config(
  enabled=true,
  target="dt", 
  triggers=["complete"]
)
```

### Relationship Tracking

1. **Create Related Task**
```
create_task(
  title="Performance Testing Suite",
  description="Test database performance improvements",
  metadata={"parent_task": "20250608_1800_Add_Database_Indexing"}
)
```

---

## Quality Control Protocol

### Completion Checklist

Every task completion requires:

1. **Documentation Check** (reminder only)
   - Did you document the work?
   - Path to documentation if created

2. **Memory Creation** (REQUIRED)
   - Must provide ChromaDB memory hash
   - Ensures knowledge is preserved
   - Prevents lost context

3. **Cleanup Confirmation** (REQUIRED)
   - Organization and tidiness verified
   - No loose ends left behind
   - Ready for handoff

### Memory Integration

TaskTracker integrates with the federation memory system:
- Completion checklist requires memory hash
- Tags enhance searchability
- Metadata includes task context
- Full narrative preserved for future reference

---

## Troubleshooting

### Common Issues

**Wake Messages Not Sending**
- Check script paths with `get_wake_status`
- Verify no quotes/apostrophes in message
- Check script permissions

**Auto-Wake Not Working**
- Confirm auto-wake is enabled (`get_wake_status`)
- Check trigger configuration
- Verify target instance is correct

**Task Not Moving to Complete Folder**
- Ensure using `complete_task_with_checklist` not just `update_task_status`
- Check directory permissions
- Verify cleanup_done=true

### Debugging Tools

- `get_wake_status` - Check wake configuration
- `list_active_tasks` - See current task states
- `get_task_details` - View complete task history

---

## Future Enhancements

### Planned Features

- **Visual Dashboard** - Web interface for task visualization
- **Timeline View** - Chronological task evolution display
- **Analytics** - Task completion metrics and patterns
- **Templates** - Pre-defined task structures for common workflows
- **Integration** - Git commit linking and external tool connections

### Extension Points

- Custom entry types beyond discussion/implementation/progress/complete
- Additional relationship types for complex project structures
- Enhanced metadata schemas for specific domains
- API endpoints for external tool integration

---

## Contributing

### Adding New Features

1. Create task using TaskTracker itself
2. Follow quality checklist protocol
3. Update documentation
4. Test wake messaging
5. Create memory with implementation details

### Code Structure

- Keep MCP tools simple and focused
- Core logic in separate modules
- Comprehensive error handling
- Configuration-driven behavior

---

## Installation & Setup

TaskTracker MCP is part of the Federation system. Installation involves:

1. MCP server configuration in Claude Desktop/Code
2. Automatic directory structure creation
3. Wake script verification
4. Initial configuration setup

Refer to Federation setup documentation for complete installation instructions.

---

*TaskTracker MCP: Turning conversations into coordinated action with complete narrative preservation.*