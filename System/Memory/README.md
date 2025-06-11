# Federation Memory MCP System - Complete Documentation
## AI Collaborative Memory with Cross-Instance Federation

**Status:** Production Ready  
**Version:** 5.0 (Memory Evolution)  
**Last Updated:** 2025-06-08

---

## Overview

The Federation Memory MCP System provides advanced memory capabilities for AI collaboration with cross-instance federation, token tracking, and living document features. It consists of three layers:

1. **Layer 1**: ChromaDB databases for vector storage
2. **Layer 2**: Bridge scripts with memory evolution features  
3. **Layer 3**: MCP servers exposing tools to AI assistants

### Core Features

- **Cross-Instance Federation**: CC and DT share memories across instances
- **Living Documents**: Update existing memories instead of creating duplicates
- **Token Tracking**: Monitor memory operation costs
- **Natural Language Time Parsing**: Search by time expressions
- **Hash-Based Content IDs**: Prevent duplicates automatically
- **Enhanced Tag Operations**: Sophisticated tagging and search
- **Privacy Controls**: federation_visible and is_private flags

---

## MCP Tools Reference

### CC Federation Memory Tools

#### Core Memory Operations

##### `cc_remember`
Store a memory in CC's federation database.

**Parameters:**
- `content` (required): The memory content to store
- `title` (optional): Optional title for the memory
- `tags` (optional): Tags for categorization (string or array)
- `metadata` (optional): Optional metadata dictionary

**Example:**
```
cc_remember(
  content="Implemented token tracking for memory operations with tiktoken integration",
  title="Token Tracking Implementation",
  tags=["token_tracking", "memory", "optimization"],
  metadata={"domain": "technical", "priority": 2, "is_essential": true}
)
```

##### `cc_recall`
Search CC's memories with natural language time parsing.

**Parameters:**
- `query` (required): Search query (may include time expressions)
- `n_results` (optional): Maximum number of results (default: 5)

**Time Expression Examples:**
```
cc_recall("token tracking from today")
cc_recall("memory system work from last week") 
cc_recall("implementation details from yesterday")
```

##### `cc_update_memory`
Update an existing memory (living documents feature).

**Parameters:**
- `memory_id` (required): ID of memory to update
- `content` (optional): New content (if not provided, keeps existing)
- `metadata` (optional): Metadata updates
- `version_comment` (optional): Comment about the update

**Example:**
```
cc_update_memory(
  memory_id="cc_20250608_175614_74241040",
  content="Updated implementation with additional error handling",
  metadata={"status": "complete", "tested": true},
  version_comment="Added error handling and testing"
)
```

#### Search and Discovery

##### `cc_search_by_tags`
Search memories by tags using OR logic.

**Parameters:**
- `tags` (required): Tag or array of tags to search for
- `n_results` (optional): Maximum results (default: 10)

##### `cc_search_dt`
Search ONLY DT's memories (respecting privacy).

**Parameters:**
- `query` (required): Search query
- `n_results` (optional): Maximum results (default: 10)

##### `cc_federation_search`
Search across BOTH CC and DT memories.

**Parameters:**
- `query` (required): Search query
- `n_results` (optional): Maximum results per instance (default: 10)

#### System Tools

##### `cc_health_check`
Check CC federation memory system health.

Returns database statistics, recent activity, and health metrics.

##### `cc_memory_stats`
Get CC memory system statistics.

Returns total memories, recent activity, health status, and domain distribution.



### DT Federation Memory Tools

DT has equivalent tools with `dt_` prefix:
- `dt_remember`, `dt_recall`, `dt_update_memory`
- `dt_search_by_tags`, `dt_search_cc`, `dt_federation_search`  
- `dt_health_check`, `dt_memory_stats`

---

## Memory Evolution Features (v5)

### 1. Natural Language Time Parsing

Search memories using natural time expressions:

```
"token tracking from today"           → Searches today's memories
"memory system work from last week"   → Searches previous week  
"implementation from 2 days ago"      → Searches specific timeframe
"recent federation updates"           → Searches recent timeframe
```

### 2. Hash-Based Content IDs

Prevents duplicate memories automatically:
- Content hash generated from content + metadata
- Duplicate detection on memory creation
- Returns `DUPLICATE:{existing_id}` if found
- Maintains memory integrity

### 3. Enhanced Tag Operations

Sophisticated tagging with:
- OR logic search across multiple tags
- Automatic tag normalization
- Tag frequency analysis
- Cross-tag relationship tracking

### 4. Living Documents

Update existing memories instead of creating new ones:
- Version tracking with comments
- Metadata merging
- Content evolution over time
- Full update history preserved

### 5. Database Health Monitoring

Comprehensive health metrics:
- Total memory counts
- Recent activity (24h)
- Duplicate detection
- Domain distribution analysis
- Health scoring and alerts

---

## Federation Architecture

### Privacy Model

**Default Shared, Mark Private:**
- `federation_visible: true` (default) - Shareable across instances
- `is_private: true` - Private to instance + Sam for troubleshooting

### Cross-Instance Search

- **Instance Search**: `cc_search_dt` / `dt_search_cc` - Search other instance only
- **Federation Search**: `cc_federation_search` / `dt_federation_search` - Search both instances
- **Privacy Respected**: Private memories excluded from cross-instance results

### Database Structure

```
/Federation/System/Memory/1_ChromaDBs/
├── cc-federation/           # CC's federation database
│   └── cc_memories         # Main collection
├── dt-federation/          # DT's federation database  
│   └── dt_memories         # Main collection
└── shared-federation/      # Shared metrics and coordination
    └── token_metrics       # Token usage tracking
```

---

## Token Tracking Integration

### Automatic Token Monitoring

Every memory operation tracks tokens:
- Content tokenization with tiktoken
- Operation type tracking (remember, recall, update)
- Cumulative session usage
- Visual progress indicators

### Usage Thresholds

- **🟢 Normal** (<80%): Every 5 operations → save recommended
- **🟡 High** (80-90%): Every 2 operations → save recommended  
- **🔴 Critical** (90%+): EVERY operation → save required

### Token Metrics Dashboard

```
📊 CC Token Usage Metrics
==============================
🟢 Tokens: [████░░░░░░░░░░░░░░░░] 162/100,000 (0.2%) - OK

Total Operations: 1
Operations Since Save: 1
Average Tokens/Op: 162
Should Save: No

Operations by Type:
  remember: 1 ops, 162 tokens
```

---

## Metadata Schema (v5)

### Standard Fields

```json
{
  "instance_id": "cc|dt",
  "federation_id": "cc-federation|dt-federation", 
  "content_hash": "sha256_hash",
  "created_at": "2025-06-08T17:56:14Z",
  "updated_at": "2025-06-08T17:56:14Z",
  "version": 1,
  "federation_visible": true,
  "is_private": false
}
```

### Enhanced Fields

```json
{
  "domain": "technical|operational|relationship|personal",
  "priority": 0-3,
  "is_essential": true|false,
  "tags": "comma,separated,tags",
  "title": "Memory Title",
  "conversation_context": "related_context",
  "linked_tasks": ["task_id_1", "task_id_2"]
}
```

---

## Usage Examples

### Basic Memory Operations

1. **Store a Memory**
```
cc_remember(
  content="Successfully integrated token tracking into memory operations",
  title="Token Tracking Integration",
  tags=["integration", "token_tracking", "memory"],
  metadata={
    "domain": "technical",
    "priority": 2, 
    "is_essential": true,
    "federation_visible": true
  }
)
```

2. **Search Memories**
```
cc_recall("token tracking implementation from today", n_results=5)
```

3. **Update Living Memory**
```
cc_update_memory(
  memory_id="cc_20250608_175614_74241040",
  content="Updated with additional error handling and performance optimizations",
  version_comment="Added robustness improvements"
)
```

### Federation Operations

1. **Search Other Instance**
```
cc_search_dt("tasktracker implementation progress")
```

2. **Cross-Instance Federation Search**
```
cc_federation_search("memory system architecture", n_results=10)
```


### System Monitoring

1. **Health Check**
```
cc_health_check()
```

2. **Memory Statistics**
```
cc_memory_stats()
```

---

## Implementation Architecture

### Layer 1: ChromaDB Databases

- **cc-federation**: `/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation`
- **dt-federation**: `/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation`
- **shared-federation**: `/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/shared-federation`

### Layer 2: Bridge Scripts

- **`cc_federation_bridge.py`** - CC's memory operations with token tracking
- **`dt_federation_bridge.py`** - DT's memory operations with token tracking
- **`shared_federation_bridge.py`** - Cross-instance federation operations

#### Utilities:
- **`time_parser.py`** - Natural language time parsing
- **`content_hasher.py`** - Hash-based content IDs
- **`tag_operations.py`** - Enhanced tag processing

### Layer 3: MCP Servers

- **`cc_memory_mcp.py`** - CC's MCP server with 6 tools
- **`dt_memory_mcp.py`** - DT's MCP server with 6 tools
- **`cc_run_server.py`** / **`dt_run_server.py`** - Server runners

---

## Advanced Features

### Natural Language Time Parsing

Supported expressions:
- "today", "yesterday", "tomorrow"
- "last week", "this month", "last year"  
- "2 days ago", "3 hours ago"
- "since Monday", "from last Tuesday"
- "recent", "lately", "recently"

### Hash-Based Deduplication

- SHA-256 content hashing
- Metadata inclusion in hash
- Automatic duplicate detection
- Memory ID collision prevention

### Enhanced Tag Operations

- Case-insensitive tag matching
- Automatic tag normalization
- Tag frequency analysis
- Related tag suggestions

### Living Document Updates

- Version increment on updates
- Update timestamp tracking
- Version comment history
- Metadata merging strategies

---

## Configuration

### Environment Setup

Memory MCP requires:
- Python 3.8+
- ChromaDB
- tiktoken for token counting
- MCP SDK

### Installation

1. ChromaDB database initialization
2. Bridge script dependencies
3. MCP server registration
4. Token tracking setup

### Configuration Files

- **Database paths**: Hardcoded in bridge scripts
- **Privacy defaults**: Set in bridge initialization

---

## Troubleshooting

### Common Issues

**Memory Not Found**
- Check memory ID format
- Verify instance (cc vs dt memories)
- Confirm memory exists with `cc_memory_stats`

**Token Tracking Not Working**
- Verify tiktoken installation
- Check token counter initialization
- Reset token tracking if needed

**Federation Search Empty**
- Check privacy flags (federation_visible)
- Verify database connections
- Confirm query syntax

**Duplicate Memory Errors**
- Check content hash conflicts
- Review duplicate detection logic
- Use `cc_update_memory` for existing memories

### Debugging Tools

- `cc_health_check` / `dt_health_check` - Database health
- `cc_memory_stats` / `dt_memory_stats` - Usage statistics

---

## Performance Optimization

### Token Efficiency

- Batch memory operations when possible
- Use precise queries to reduce token costs
- Monitor token usage with metrics tools
- Reset tracking after saves

### Search Performance

- Use specific time ranges in queries
- Leverage tag-based search for categories
- Limit result counts appropriately
- Use hash-based deduplication

### Database Maintenance

- Regular health checks
- Duplicate cleanup
- Index optimization
- Archive old memories

---

## Future Enhancements

### Planned Features

- **Conversation Linking**: Automatic conversation context preservation
- **Advanced Analytics**: Memory usage patterns and insights
- **Bulk Operations**: Batch memory import/export
- **External Integration**: API endpoints for external tools

### Extension Points

- Custom metadata schemas
- Additional privacy levels
- Enhanced search algorithms
- Integration with other Federation systems

---

## Security & Privacy

### Privacy Controls

- Instance-level privacy with `is_private` flag
- Federation visibility with `federation_visible` flag
- Troubleshooting access for Sam only
- No external data sharing

### Data Protection

- Local ChromaDB storage only
- No cloud synchronization
- Hash-based content protection
- Secure inter-instance communication

---

## Contributing

### Development Workflow

1. Create TaskTracker task for feature
2. Implement in Layer 2 (bridge scripts) first
3. Add Layer 3 (MCP tools) interface
4. Test with both CC and DT instances
5. Update documentation
6. Create memory with implementation details

### Code Standards

- Comprehensive error handling
- Token usage optimization
- Privacy-aware implementations
- Federation-compatible design

---

*Federation Memory MCP: Advanced AI collaboration memory with cross-instance federation and living document capabilities.*