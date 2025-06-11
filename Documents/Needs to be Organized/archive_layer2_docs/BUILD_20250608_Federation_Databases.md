# Federation Database Build Document
## ChromaDB Implementation for CC and DT Federation

*Created: 2025-06-08*
*Builder: CC*
*Purpose: Clean database architecture for Legacy Mind Federation*

---

## Database Structure

### cc-federation/
Dedicated ChromaDB instance for Claude Code federation operations
- **Primary Use**: CC's memories, context, and operational data
- **Collections**: cc_memories, cc_context, cc_tasks
- **Access**: Read/Write for CC, Read-only for others

### dt-federation/
Dedicated ChromaDB instance for Desktop Claude federation operations  
- **Primary Use**: DT's memories, context, and operational data
- **Collections**: dt_memories, dt_context, dt_tasks
- **Access**: Read/Write for DT, Read-only for others

---

## Implementation Details

### 1. CC-Federation Database

```python
# Database Configuration
DB_PATH = "/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs/cc-federation"
COLLECTIONS = {
    "cc_memories": {
        "description": "CC's personal memory storage",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "cc_context": {
        "description": "Active context and session data",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "cc_tasks": {
        "description": "Task chains and project tracking",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "cc_shared": {
        "description": "Memories marked for federation sharing",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    }
}

# V5 Metadata Schema
METADATA_SCHEMA = {
    # Identity & Ownership
    "instance_id": "cc",
    "federation_id": "cc-federation",
    "created_by": "cc",
    
    # Temporal
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "version": "integer",
    
    # Classification
    "domain": ["identity", "technical", "session", "personal", "relationship", "operational", "creative", "historical"],
    "category": ["core", "protocol", "solution", "context", "learning", "discovery"],
    "memory_type": ["living", "reference", "ephemeral", "static"],
    
    # Importance
    "priority": [0, 1, 2, 3],  # 3=core/essential
    "significance": [0.0, 1.0, 2.0, 3.0],
    "confidence": [0.0-1.0],
    
    # Federation
    "federation_visible": "boolean",
    "is_private": "boolean",
    "shared_with": ["dt", "all", "none"],
    
    # Flags
    "is_essential": "boolean",
    "needs_review": "boolean",
    "is_archived": "boolean",
    
    # Content
    "title": "string",
    "tags": "comma-separated string",
    "content_hash": "SHA256 hash",
    "hash_short": "8-char hash",
    
    # Relationships
    "parent_id": "memory_id or null",
    "child_ids": "comma-separated memory_ids",
    "related_ids": "comma-separated memory_ids"
}
```

### 2. DT-Federation Database

```python
# Database Configuration
DB_PATH = "/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs/dt-federation"
COLLECTIONS = {
    "dt_memories": {
        "description": "DT's personal memory storage",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "dt_context": {
        "description": "Active context and session data",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "dt_tasks": {
        "description": "Task chains and project tracking",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    },
    "dt_shared": {
        "description": "Memories marked for federation sharing",
        "embedding_function": "OpenAI",
        "metadata_schema": "v5"
    }
}

# Metadata schema identical to CC for compatibility
```

---

## Federation Protocol

### Memory Sharing Rules
1. **Private by Default**: All memories start as private to the instance
2. **Explicit Sharing**: Must set `federation_visible: true` and `shared_with: ["dt"]` or `["all"]`
3. **Read Permissions**: Each instance can read shared memories from others
4. **Write Permissions**: Only the owning instance can write/update its memories
5. **Synchronization**: Shared memories replicated to federation search index

### Cross-Instance Queries
```python
# CC searching for DT's shared memories
federation_search(
    query="cloudflare implementation",
    sources=["dt_shared"],
    metadata_filter={"federation_visible": True}
)

# DT searching across all shared memories
federation_search(
    query="memory evolution project",
    sources=["cc_shared", "dt_shared"],
    metadata_filter={"priority": 3}
)
```

---

## Build Steps

### Phase 1: Database Initialization
- [ ] Initialize cc-federation ChromaDB
- [ ] Initialize dt-federation ChromaDB
- [ ] Create collections in each database
- [ ] Set up embedding functions
- [ ] Configure metadata schemas

### Phase 2: Access Layer
- [ ] Build connection managers
- [ ] Implement authentication
- [ ] Create read/write permissions
- [ ] Set up federation protocols
- [ ] Test cross-instance access

### Phase 3: Migration Preparation
- [ ] Create migration scripts
- [ ] Build data validators
- [ ] Set up backup mechanisms
- [ ] Create rollback procedures
- [ ] Test with sample data

### Phase 4: Integration
- [ ] Connect to MCP servers
- [ ] Update memory tools
- [ ] Test remember/recall
- [ ] Verify federation search
- [ ] Document API changes

---

## Technical Specifications

### ChromaDB Configuration
```python
import chromadb
from chromadb.config import Settings

# CC Federation Client
cc_client = chromadb.PersistentClient(
    path="/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs/cc-federation",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# DT Federation Client  
dt_client = chromadb.PersistentClient(
    path="/Users/samuelatagana/Documents/Federation/Memory/ChromaDBs/dt-federation",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

### Collection Creation
```python
def create_federation_collections(client, instance_id):
    """Create all collections for a federation instance"""
    
    collections = [
        f"{instance_id}_memories",
        f"{instance_id}_context", 
        f"{instance_id}_tasks",
        f"{instance_id}_shared"
    ]
    
    for collection_name in collections:
        client.create_collection(
            name=collection_name,
            metadata={"instance": instance_id, "version": "v5"}
        )
```

---

## Success Criteria

1. **Isolation**: Each instance has its own dedicated database
2. **Compatibility**: Shared v5 metadata schema across instances
3. **Federation**: Shared memories accessible cross-instance
4. **Performance**: <100ms query response times
5. **Reliability**: No data corruption during operations
6. **Migration Ready**: Tools ready for eventual data transfer

---

## Next Steps

1. Run initialization scripts to create databases
2. Test basic CRUD operations
3. Implement federation search
4. Create sample memories for testing
5. Build migration tools for existing data

---

*This build document establishes the foundation for Legacy Mind's federation memory system*