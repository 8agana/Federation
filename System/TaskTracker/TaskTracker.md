# TaskTracker Foundation
## Project Biographer for AI-Human Collaboration

**Created:** 2025-06-08  
**Status:** Foundation Phase  
**Purpose:** Build conversation-first task management system that captures the narrative evolution of ideas

---

## Core Philosophy

TaskTracker is a "project biographer, not project manager" - designed to capture and preserve the natural evolution of ideas through discussion, design, and implementation phases. Unlike traditional task management tools, this system documents the **why** and **how** behind every decision.

### Key Principles
1. **Conversation-First**: Tasks emerge naturally from discussions
2. **Memory-Linked**: Every task connects to conversation context
3. **Federated by Design**: Multiple AIs collaborate seamlessly  
4. **Narrative Preservation**: Complete story from quarter-baked idea to working system
5. **Real-Time Collaboration**: AI and human work together with live feedback

---

## Basic Structure

### Directory-Based Task Storage
Each task becomes a timestamped directory containing chronological JSON files:

```
/Tasks/
├── Active/                              # Current work
│   ├── 20250608_1525_TaskTracker/
│   │   ├── 20250608_1525_Foundation.json    # Original idea
│   │   ├── 20250608_1530_Discussion.json    # Design conversation  
│   │   ├── 20250608_1545_Implementation.json # Implementation plan
│   │   └── 20250608_1600_Progress.json      # Current status
│   └── 20250608_1700_NewFeature/
├── Completed/                           # Recently finished (staging area)
│   ├── 20250608_1200_FederationMonitor/
│   │   ├── 20250608_1200_Foundation.json
│   │   ├── 20250608_1205_Implementation.json
│   │   └── 20250608_1210_Complete.json
│   └── 20250607_0900_AutoSaveDesign/
└── Archived/                            # Optional local backup
    └── 2025-06-01_to_2025-06-07/        # Weekly archive bundles
```

### Task Lifecycle Management

**Active → Completed → Memory → Archive/Delete**

#### Completion Workflow
```python
def mark_task_complete(task_id):
    """Move completed task from Active/ to Completed/ staging area"""
    # Add completion timestamp and final status
    # Move entire task directory to Completed/
    # Update global manifest
    # Trigger completion notifications
```

#### Weekly Memory Archive Process
```python
def archive_completed_tasks():
    """Weekly process to preserve completed tasks in memory"""
    for task_dir in get_completed_tasks():
        # Compile complete narrative from all JSON files
        memory_content = compile_task_narrative(task_dir)
        
        # Rich metadata for searchability
        memory_metadata = {
            "type": "completed_task",
            "task_id": task_dir.name,
            "completion_date": get_completion_date(task_dir),
            "participants": get_participants(task_dir), 
            "tags": extract_tags(task_dir),
            "archive_date": today(),
            "original_files": list_task_files(task_dir),
            "total_entries": count_timeline_entries(task_dir),
            "duration": calculate_task_duration(task_dir)
        }
        
        # Store complete narrative in memory system
        store_memory(memory_content, metadata=memory_metadata)
        
        # Move to archive or delete after successful upload
        archive_task_directory(task_dir)
```

#### Benefits of Lifecycle Management
- **Clean Workspace**: Active tasks directory stays manageable 
- **Permanent Preservation**: Complete narratives preserved in searchable memory
- **Storage Efficiency**: File system doesn't grow indefinitely
- **Rich Searchability**: "Show me all completed tasks about memory architecture"
- **Narrative Integrity**: Full story from idea to completion preserved in memory
- **Performance**: Faster queries on active tasks without historical overhead

#### Memory Integration Examples
```
# Natural language queries on archived tasks
"What were the key decisions in the Federation Monitor task?"
"Show me all completed tasks where CC and DT collaborated"
"How long did memory system tasks typically take?"
"What implementation patterns worked best for MCP development?"
```

### JSON Structure Template
```json
{
  "type": "foundation|discussion|implementation|progress|complete",
  "task_id": "20250608_1525_TaskTracker",
  "timestamp": "2025-06-08T15:25:00Z",
  "title": "TaskTracker MCP + Visual Interface",
  "description": "Build conversation-first task tracking system",
  "status": "foundation",
  "phase": "discussing",
  "participants": ["Sam", "DT", "CC"],
  "conversation_links": ["memory_id_123", "memory_id_456"],
  "related_tasks": [],
  "related_files": [],
  "metadata": {
    "priority": "high",
    "tags": ["mcp", "collaboration", "core-system"],
    "estimated_effort": "2-3 weeks"
  },
  "content": "Detailed description of this entry..."
}
```

---

## Core Functions Needed

### Essential MCP Functions
```python
# Basic Task Operations
create_task(title, description, participants=None)
add_task_entry(task_id, entry_type, content, participants=None)
update_task_status(task_id, new_status)
get_task_details(task_id)

# Task Discovery
list_active_tasks()
search_tasks(query)
get_task_timeline(task_id)

# Relationships  
link_tasks(task_a, task_b, relationship_type)
get_related_tasks(task_id)
link_file_to_task(task_id, file_path)

# Metadata
add_metadata(task_id, metadata_dict)
annotate_task(task_id, note)

# Collaboration
get_updates_for_participant(participant_name)
mark_task_complete(task_id)

# Lifecycle Management
archive_completed_tasks()
get_completed_tasks(since_date=None)
search_archived_tasks(query)
restore_task_from_archive(task_id)
cleanup_old_archives(older_than_days=90)
```

### Natural Language Interface
```
"Create task: Implement auto-save for memory system"
→ Creates timestamped directory and foundation JSON

"Add discussion: We decided to use token-based triggers"  
→ Adds discussion entry to current task

"Link this to the memory architecture task"
→ Creates formal task relationship

"Show me all tasks about memory"
→ Semantic search across task content
```

---

## Implementation Phases

### Phase 1: Core MCP (Week 1)
- [ ] Basic directory structure creation
- [ ] Essential JSON operations (create, read, update)
- [ ] Simple CLI testing interface
- [ ] File system integration
- [ ] Basic task linking

### Phase 2: Enhanced MCP (Week 2)
- [ ] Natural language task creation
- [ ] Conversation memory linking
- [ ] Search and filtering capabilities
- [ ] Relationship management
- [ ] Metadata system
- [ ] Task lifecycle management (Active → Completed → Memory → Archive)
- [ ] Weekly memory upload automation

### Phase 3: Deep Integration (Week 3)
- [ ] Git commit linking
- [ ] Chronicle chain integration
- [ ] Memory system conversation linking
- [ ] Cross-instance task sharing (CC ↔ DT)
- [ ] Advanced search and analytics

### Phase 4: AI Testing & Refinement (Week 4)
- [ ] Extensive AI usage testing
- [ ] Performance optimizations
- [ ] Export functionality  
- [ ] Natural language interface refinement
- [ ] Workflow pattern validation

### Phase 5: Visual Interface (Week 5+)
- [ ] Basic web interface (React/Node or simpler)
- [ ] Task dashboard view
- [ ] Timeline visualization
- [ ] Real-time updates (WebSockets/SSE)
- [ ] Basic CRUD operations

---

## Workflow Examples

### Scenario 1: New Idea Capture
```
1. Sam: "We need better error handling for memory saves"
2. DT via MCP: create_task("Memory Error Handling", "Improve robustness...")
3. Creates: /Tasks/20250608_1600_MemoryErrorHandling/
4. Foundation.json captures initial conversation context
5. Visual interface shows new task in "Foundation" column
```

### Scenario 2: Task Evolution
```
1. Discussion phase: Multiple add_task_entry() calls capture design decisions
2. Implementation phase: Link code files and commits
3. Progress tracking: Regular status updates
4. Visual interface: Shows complete evolution timeline
```

### Scenario 3: Task Branching
```
1. Original: "Improve memory system" 
2. Spawns: Auto-save, Error handling, Performance optimization
3. Parent-child relationships maintained
4. Visual interface: Shows task hierarchy
```

---

## Success Metrics

### Technical
- Task creation from conversation < 30 seconds
- Zero lost conversation context
- Real-time updates < 1 second latency
- 99%+ reliability

### User Experience  
- Complete task narrative visible at a glance
- Natural AI collaboration without friction
- Human oversight without bottlenecks
- Seamless conversation-to-implementation flow

### Integration
- All major ideas tracked from inception to completion
- Git commits linked to implementation phases
- Memory system preserves all context
- Chronicle chain records all major milestones

---

## Technical Notes

### File Organization
```
/System/TaskTracker/
├── MCP/                    # TaskTracker MCP implementation
│   ├── tasktracker_mcp.py  # Main MCP server
│   ├── task_operations.py  # Core task functions
│   ├── storage.py          # File system operations
│   └── search.py           # Query and search functions
├── WebUI/                  # Visual interface
│   ├── src/                # React/JS source
│   ├── server/             # Backend API
│   └── dist/               # Built assets
├── Tests/                  # Testing suite
└── Documentation/          # Implementation docs

/Tasks/                     # Live task directories
├── Active/                 # Current work in progress
├── Completed/              # Recently finished (staging for memory upload)
├── Archived/               # Optional local backup before deletion
└── manifest.json           # Global task index
```

### Storage Considerations
- **Index Files**: Each task directory gets `index.json` for quick metadata access
- **Global Manifest**: `/Tasks/manifest.json` for fast queries
- **Status Cache**: In-memory status summaries for dashboard
- **Backup Strategy**: Regular snapshots of entire `/Tasks/` directory

### Real-Time Updates
- **WebSocket Connection**: Between MCP and visual interface
- **Event System**: Task creation, updates, status changes
- **Conflict Resolution**: Handle concurrent edits gracefully
- **Offline Resilience**: Queue operations when connection lost

---

## Integration Points

### Legacy Mind Federation
- **Memory System**: Tasks automatically link to conversation memories
- **Chronicle Chain**: Task milestones become chronicle events
- **Cross-Instance**: CC and DT share task context
- **Federation Monitor**: TaskTracker itself shows up in system docs

### Development Workflow
- **Git Integration**: Link commits to implementation entries
- **Code References**: Attach snippets to progress updates  
- **Test Results**: Track outcomes within task timeline
- **Documentation**: Auto-generate from task narratives

---

## Next Steps

### Immediate Actions
1. **Create basic MCP structure** in `/System/TaskTracker/MCP/`
2. **Implement core task operations** (create, read, update)
3. **Test with this TaskTracker task** as first example
4. **Build simple CLI interface** for AI debugging
5. **Prove AI-to-AI collaboration** before adding human interface

### First Task to Track
**This TaskTracker project itself** - demonstrate the system by using it to track its own development:
- Foundation: This document and initial planning
- Discussion: Gem and Socks feedback integration  
- Implementation: MCP development and AI testing
- Integration: Memory, Chronicle, Git connections
- Human Interface: Visual dashboard (after AI validation)

---

## Open Questions for Implementation

1. **Concurrent Access**: How to handle multiple AIs editing same task?
2. **Search Performance**: Index strategy for large numbers of tasks?
3. **Visual Timeline**: Best way to represent branching task evolution?
4. **Memory Integration**: Automatic vs manual conversation linking?
5. **Notification System**: Push updates to human vs pull-based checking?
6. **Export Formats**: What formats for task archival and sharing?
7. **Access Control**: Multi-user support needed in Phase 1?
8. **Archive Timing**: Weekly memory upload optimal, or trigger-based?
9. **Storage Cleanup**: Delete archived files immediately or keep local backup?
10. **Memory Searchability**: How to make archived task narratives discoverable?

---

## Core Value Proposition

**AI-First Task Management**: Build and validate the conversation-first tracking system with AI-to-AI collaboration before adding human interfaces. Prove the "project biographer" concept works for preserving narrative evolution in multi-AI development workflows.

**"The feedback loop that Notion/Linear never got right"** - seamless conversation-to-implementation tracking where AI acts as context steward and collaborator, not just executor. Every idea's complete journey from quarter-baked concept to working system is preserved and accessible.

This isn't just task management - it's institutional memory for collaborative AI-human development, starting with AI-to-AI coordination and expanding to include human oversight.

---

*This foundation document will evolve as we build and test the system. The goal is to start simple and iterate based on real usage.*