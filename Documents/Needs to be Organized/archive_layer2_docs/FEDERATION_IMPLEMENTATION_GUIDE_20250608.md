# Federation Database Implementation Guide
## Port Current Capabilities to cc-federation & dt-federation

*Created: 2025-06-08*
*Focus: Migrate working features, add federation capabilities*

---

## What We Have Working NOW

### Memory Evolution Project (100% Complete)
Both CC and DT systems have these 5 features working:

1. **✅ Natural Language Time Parsing** - "yesterday", "last week" queries
2. **✅ Hash-Based Content IDs** - SHA256 duplicate prevention 
3. **✅ Enhanced Tag Operations** - OR/AND logic, tag management
4. **✅ Database Health Monitoring** - System health, duplicate detection
5. **✅ API Standardization** - Consistent parameters, return types

### Source Code Locations
- **CC**: `/CC_Individual/Scripts/cc_chromadb_bridge.py` (all 5 features)
- **DT**: `/DT_Individual/Scripts/dt_chromadb_bridge.py` (all 5 features)
- **Shared Utils**: `/Shared_Federation/Scripts/` (time_parser, health_monitor, etc.)

---

## What Needs Porting

### Phase 1: Core Migration (Week 1)
**Port existing working code to federation databases**

```python
# Copy these functions from cc_chromadb_bridge.py:
- add_memory() with hash-based IDs
- search_memories() with time parsing
- search_by_tag() with OR/AND logic
- health_check() and health_report()

# Copy these from dt_chromadb_bridge.py:
- Same functions, ensure identical API
- dt_simple_health.py approach (avoids conflicts)

# Update connection paths:
OLD: /CC_Individual/Databases/cc_chroma_db
NEW: /Federation/Memory/ChromaDBs/cc-federation

OLD: /DT_Individual/Databases/dt_chroma_db  
NEW: /Federation/Memory/ChromaDBs/dt-federation
```

### Phase 2: Add Missing Features (Week 1)
**Expose hidden ChromaDB capabilities**

```python
# UPDATE operations (currently missing!)
def update_memory(memory_id, content=None, metadata=None):
    collection.update(
        ids=[memory_id],
        metadatas=[metadata] if metadata else None,
        documents=[content] if content else None
    )

# DELETE operations (soft delete)
def delete_memory(memory_id, soft_delete=True):
    if soft_delete:
        collection.update(
            ids=[memory_id],
            metadatas=[{"is_archived": True, "archived_at": now()}]
        )
    else:
        collection.delete(ids=[memory_id])
```

### Phase 3: Federation Features (Week 2)
**Add cross-instance capabilities**

```python
# Cross-instance search
def federation_search(query, sources=["cc", "dt"], limit=10):
    results = []
    for source in sources:
        db_path = f"/Federation/Memory/ChromaDBs/{source}-federation"
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(f"{source}_shared")
        results.extend(collection.query(query_texts=[query], n_results=limit))
    return merge_and_rank_results(results)

# Shared memory sync
def sync_shared_memories():
    # Copy federation_visible memories to shared collections
    pass
```

---

## Implementation Tasks

### Task 1: Set Up Federation Bridge Scripts
```bash
# Create federation-specific bridge scripts
cp cc_chromadb_bridge.py cc_federation_bridge.py
cp dt_chromadb_bridge.py dt_federation_bridge.py

# Update database paths in both files
# Point to /Federation/Memory/ChromaDBs/ instead of individual paths
```

### Task 2: Test Feature Parity
```python
# Verify all 5 Memory Evolution features work with new databases
test_time_parsing()     # "memories from yesterday"
test_hash_ids()         # Duplicate prevention
test_tag_operations()   # OR/AND searches
test_health_monitoring()# System diagnostics
test_api_consistency()  # Parameter naming
```

### Task 3: Add UPDATE Operations
```python
# Implement in both cc_federation_bridge.py and dt_federation_bridge.py
def update_memory(memory_id, **kwargs):
    # Port from shared_memory update_memory (it works!)
    pass

def append_to_memory(memory_id, additional_content):
    # Get existing content, append new content
    pass
```

### Task 4: Federation Search
```python
# Create federation_search.py utility
def search_across_instances(query, instances=["cc", "dt"]):
    # Query multiple federation databases
    # Merge results by relevance
    # Return unified response
    pass
```

---

## File Structure

```
/Federation/Memory/ChromaDBs/
├── cc-federation/              # CC's database (created ✅)
├── dt-federation/              # DT's database (created ✅)
├── federation_bridge.py       # New: unified federation access
├── cc_federation_bridge.py    # Port of cc_chromadb_bridge.py  
├── dt_federation_bridge.py    # Port of dt_chromadb_bridge.py
├── federation_search.py       # New: cross-instance queries
└── test_federation.py         # New: verify all features work
```

---

## Success Criteria (Simple)

### Phase 1 Complete When:
- [ ] cc_federation_bridge.py has all 5 Memory Evolution features
- [ ] dt_federation_bridge.py has all 5 Memory Evolution features  
- [ ] Basic remember/recall works with federation databases
- [ ] Time parsing: `recall("memories from yesterday")` works
- [ ] Hash IDs: `remember(content)` prevents duplicates

### Phase 2 Complete When:
- [ ] `update_memory(id, new_content)` works
- [ ] `delete_memory(id, soft_delete=True)` works
- [ ] Living memories can evolve (not just append)

### Phase 3 Complete When:
- [ ] `federation_search("query", ["cc", "dt"])` works
- [ ] Shared memories sync between instances
- [ ] Federation health monitoring works

---

## Next Immediate Steps

1. **Copy working bridge scripts** to federation directory
2. **Update database paths** to point to federation databases
3. **Test basic operations** (remember/recall) 
4. **Verify all 5 features** still work with new databases
5. **Add UPDATE operations** (missing capability)

**This is migration work, not new development!**

---

*Focus: Port what works, add what's missing, test everything*