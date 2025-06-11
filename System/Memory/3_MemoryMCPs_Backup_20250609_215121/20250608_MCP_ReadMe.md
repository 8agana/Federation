# Memory MCP Servers Layer - ReadMe
## Protocol Interface for Federation Memory System

*Created: 2025-06-08*
*Purpose: Layer 3 MCP servers that expose bridge functionality as tools*

---

## What This Layer Does

This layer provides **Model Context Protocol (MCP) servers** that:
- Expose Layer 2 bridge functions as tools
- Handle protocol communication
- Provide standardized tool interfaces
- Enable AI assistants to use federation memory

**Key Design**: MCP servers are thin wrappers around bridge scripts. They:
1. Parse tool requests
2. Call appropriate bridge functions  
3. Return standardized responses
4. Handle errors gracefully

---

## Directory Structure

### core/
**Individual instance MCP servers**
- `cc_memory_mcp.py` - CC's federation memory MCP server (640+ lines with KG)
- `dt_memory_mcp.py` - DT's federation memory MCP server (640+ lines with KG)
- `cc_run_server.py` - CC MCP runner with package management (36 lines)
- `dt_run_server.py` - DT MCP runner with package management (36 lines)

### Knowledge Graph Integration
The MCP servers now import from `/Federation/Memory/KnowledgeGraph/`:
- `storage.py` - JSON-based graph storage
- `extractor.py` - Zero-touch entity/relation extraction
- `models.py` - Entity and Relation dataclasses

### ~~shared/~~ (REMOVED)
**Federation operations integrated directly into instance MCPs** - Each instance has 8 tools including cross-instance search

---

## MCP Server Architecture

### Tool Naming Convention
```
{instance}_{operation}
Examples:
- cc_remember
- dt_recall
- federation_search
```

### Standard Tool Operations

#### Instance-Specific Tools (CC/DT)
1. **{instance}_remember** - Store new memory (default: federation_visible=true)
2. **{instance}_recall** - Search own memories  
3. **{instance}_update_memory** - Update existing memory
4. **{instance}_search_by_tags** - Tag-based search
5. **{instance}_health_check** - System health
6. **{instance}_memory_stats** - Statistics
7. **{instance}_search_{other}** - Search ONLY other instance's memories
8. **{instance}_federation_search** - Search BOTH instances

#### Knowledge Graph Tools (NEW - Added 2025-06-08)
9. **{instance}_kg_auto_extract** - Auto-extract entities/relations from text
10. **{instance}_kg_instant_briefing** - Generate instant context for token death recovery
11. **{instance}_kg_semantic_search** - Search entities by name/content
12. **{instance}_kg_find_related** - Find related entities via graph traversal
13. **{instance}_kg_get_active_context** - Get active tasks/files/problems
14. **{instance}_kg_stats** - Knowledge graph statistics

#### Privacy Model
- **Default**: `federation_visible: true` - Memory is shareable
- **Private**: `is_private: true` - Only visible to owner (and Sam for troubleshooting)
- **No explicit sharing** - The flags handle everything automatically

---

## Implementation Standards

### Tool Definition Format
```python
@server.tool()
async def cc_remember(
    content: str,
    title: Optional[str] = None,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Store a memory in CC's federation database"""
    # Call bridge function
    # Return standardized response
```

### Error Handling
All tools must:
1. Catch bridge exceptions
2. Return user-friendly error messages
3. Log errors for debugging
4. Never expose internal paths

### Response Format
```python
{
    "success": bool,
    "data": Any,  # Tool-specific data
    "message": str,
    "error": Optional[str]
}
```

---

## MCP Server Configuration

### CC Memory MCP
```json
{
  "cc-federation-memory": {
    "command": "python3",
    "args": [
      "/Federation/System/Memory/3_MemoryMCPs/core/cc_memory_mcp.py"
    ],
    "env": {
      "PYTHONPATH": "/Federation/System/Memory/2_BridgeScripts"
    }
  }
}
```

### DT Memory MCP  
```json
{
  "dt-federation-memory": {
    "command": "python3",
    "args": [
      "/Federation/System/Memory/3_MemoryMCPs/core/dt_memory_mcp.py"
    ],
    "env": {
      "PYTHONPATH": "/Federation/System/Memory/2_BridgeScripts"
    }
  }
}
```

### Dependencies
```bash
# Install required packages
pip install mcp chromadb
```

---

## Testing Strategy

### Unit Tests
1. Test each tool independently
2. Mock bridge responses
3. Verify error handling
4. Check response formats

### Integration Tests
1. Test with real bridge connections
2. Verify database operations
3. Test cross-instance features
4. Performance benchmarks

### End-to-End Tests
1. Install MCP servers
2. Use from AI assistant
3. Verify all features work
4. Test error scenarios

---

## Run Server Architecture

### Purpose
The `run_server.py` wrappers handle environment setup and package management:
- Check for required packages (chromadb, mcp)
- Attempt installation if missing
- Set up Python path for bridge imports
- Launch the actual MCP server

### Configuration
Both Claude Desktop (DT) and Claude Code (CC) configs point to run_server.py:
```json
"cc-federation-memory": {
  "command": "python3",
  "args": ["/path/to/cc_run_server.py"],
  "env": {
    "PYTHONPATH": "/path/to/2_BridgeScripts",
    "PYTHONUNBUFFERED": "1"
  }
}
```

This pattern ensures MCPs can start even if the MCP SDK isn't globally installed.

---

## Performance Requirements

- Tool response time: <100ms
- Memory operations: <200ms  
- Federation search: <500ms
- Health checks: <1s

---

## Security Considerations

1. **No Direct Database Access** - Only through bridges
2. **Input Validation** - Sanitize all tool inputs
3. **Path Protection** - Never expose filesystem paths
4. **Error Sanitization** - Clean error messages

---

## Success Criteria

### MCP Servers Complete When:
- [x] CC memory MCP exposes all 8 tools
- [x] DT memory MCP exposes all 8 tools  
- [x] ~~Federation MCP~~ integrated into instance MCPs
- [x] All tools have proper error handling
- [x] Response formats are consistent
- [x] Performance meets requirements
- [x] Installed in DT's config and ready to use

---

## Maintenance Notes

1. **Adding New Tools**: Add to bridge first, then expose via MCP
2. **Updating Tools**: Maintain backward compatibility
3. **Debugging**: Check bridge layer first, then MCP wrapper
4. **Performance**: Profile at bridge level, not MCP level

---

*Layer 3 completes the federation memory system architecture*