# Federation Database Capabilities Document
## Complete Feature Specification for cc-federation & dt-federation

*Created: 2025-06-08*
*Based on: Memory Evolution Project (100% complete) + ChromaDB Tools Documentation*
*Purpose: Ensure federation databases implement ALL current capabilities*

---

## Feature Parity Requirements

### Memory Evolution Project Features (100% Complete)
Both cc-federation and dt-federation databases must support all 5 Memory Evolution features:

1. **✅ Natural Language Time Parsing**
2. **✅ Hash-Based Content IDs** 
3. **✅ Enhanced Tag Operations**
4. **✅ Database Health Monitoring**
5. **✅ API Standardization**

---

## 1. Natural Language Time Parsing

### Core Capability
Parse human-friendly time expressions and translate to database queries

### Supported Time Expressions
```python
# Relative expressions
"today", "yesterday", "this morning", "last week"
"3 days ago", "last Tuesday", "this afternoon"
"yesterday morning", "last Christmas", "Q3 2024"

# Time ranges
"from today", "from this morning", "between Monday and Friday"
"memories from the last hour", "testing from yesterday afternoon"
```

### Implementation Requirements
```python
# Federation database must support time-filtered queries
def time_aware_recall(query, time_expression, limit=5):
    """
    Search memories with natural language time filtering
    
    Args:
        query: Semantic search query
        time_expression: Human time like "yesterday", "last week"
        limit: Maximum results
        
    Returns:
        List of memories matching query AND time filter
    """
    # Parse time expression to datetime range
    start_time, end_time = parse_time_expression(time_expression)
    
    # Query with time metadata filter
    return collection.query(
        query_texts=[query],
        where={"created_at": {"$gte": start_time, "$lte": end_time}},
        n_results=limit
    )
```

### Database Schema Requirements
- **created_at**: ISO timestamp for all memories
- **updated_at**: ISO timestamp for modifications
- Time parsing utilities accessible to all federation queries

---

## 2. Hash-Based Content IDs

### Core Capability
Generate unique IDs based on content hash to prevent exact duplicates

### ID Format
```
{instance}_{YYYYMMDD}_{HHMMSS}_{hash8}

Examples:
cc_20250608_143052_a1b2c3d4
dt_20250608_143052_e5f6g7h8
```

### Implementation Requirements
```python
def generate_memory_id(content, instance_id):
    """
    Generate hash-based memory ID
    
    Args:
        content: Memory content string
        instance_id: "cc" or "dt"
        
    Returns:
        Unique ID string with embedded hash
    """
    # SHA256 hash of content
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    hash_short = content_hash[:8]
    
    # Timestamp component
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{instance_id}_{timestamp}_{hash_short}"

def check_duplicate_content(content):
    """
    Check if content already exists
    
    Returns:
        None if unique, existing_id if duplicate
    """
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    
    results = collection.query(
        where={"content_hash": {"$eq": content_hash}},
        n_results=1
    )
    
    return results['ids'][0] if results['ids'] else None
```

### Database Schema Requirements
- **content_hash**: SHA256 hash of content (full)
- **hash_short**: First 8 characters of hash
- Duplicate detection on content_hash field
- Memory IDs must include hash component

---

## 3. Enhanced Tag Operations

### Core Capability
Advanced tag management with array support and logical operations

### Supported Operations
```python
# OR Logic (any tag matches)
search_by_tag(["memory", "evolution", "test"])

# AND Logic (all tags must match)
search_by_all_tags(["memory", "evolution", "complete"])

# Tag Management
add_tags_to_memory(memory_id, ["new", "tags"])
remove_tags_from_memory(memory_id, ["old", "tags"])

# Tag Statistics
get_unique_tags()  # Returns count and list
get_memories_with_tags()  # Returns count
```

### Implementation Requirements
```python
def search_by_tag(tag_list, limit=10):
    """
    Search memories containing ANY of the specified tags (OR logic)
    """
    # Convert to contains queries
    or_conditions = [{"tags": {"$contains": tag}} for tag in tag_list]
    
    return collection.query(
        where={"$or": or_conditions},
        n_results=limit
    )

def search_by_all_tags(tag_list, limit=10):
    """
    Search memories containing ALL specified tags (AND logic)
    """
    # Convert to contains queries
    and_conditions = [{"tags": {"$contains": tag}} for tag in tag_list]
    
    return collection.query(
        where={"$and": and_conditions},
        n_results=limit
    )

def add_tags_to_memory(memory_id, new_tags):
    """
    Add tags to existing memory without replacing existing tags
    """
    # Get current memory
    current = collection.get(ids=[memory_id])
    current_tags = current['metadatas'][0].get('tags', '').split(',')
    
    # Merge tags
    all_tags = list(set(current_tags + new_tags))
    updated_tags = ','.join([tag.strip() for tag in all_tags if tag.strip()])
    
    # Update memory
    collection.update(
        ids=[memory_id],
        metadatas=[{"tags": updated_tags}]
    )
```

### Database Schema Requirements
- **tags**: Comma-separated string of tags
- Tag operations must preserve existing tags when adding/removing
- Support for both string and array inputs (converted to strings)

---

## 4. Database Health Monitoring

### Core Capability
Comprehensive health checks, diagnostics, and optimization recommendations

### Health Check Features
```python
def health_check():
    """
    Quick health overview
    
    Returns:
        Dict with status, counts, basic metrics
    """
    return {
        "status": "HEALTHY",
        "total_memories": collection.count(),
        "recent_24h": count_recent_memories(24),
        "collection_name": collection.name,
        "database_size": get_db_size(),
        "last_activity": get_last_activity()
    }

def health_report():
    """
    Detailed health analysis
    
    Returns:
        Comprehensive diagnostic information
    """
    return {
        "memory_metrics": get_memory_metrics(),
        "metadata_coverage": analyze_metadata_coverage(),
        "time_distribution": get_time_distribution(),
        "tag_analysis": analyze_tag_usage(),
        "performance_metrics": get_performance_metrics(),
        "optimization_tips": get_optimization_recommendations()
    }

def check_duplicates():
    """
    Find potential duplicate content
    
    Returns:
        List of duplicate groups by content hash
    """
    # Group by content_hash
    # Return any groups with > 1 memory
```

### Implementation Requirements
```python
def get_memory_metrics():
    """Database-specific metrics"""
    return {
        "total_count": collection.count(),
        "recent_24h": count_recent(24),
        "recent_7d": count_recent(168),
        "avg_daily": calculate_daily_average(),
        "growth_rate": calculate_growth_rate()
    }

def analyze_metadata_coverage():
    """Metadata completeness analysis"""
    all_memories = collection.get()
    
    field_coverage = {}
    for metadata in all_memories['metadatas']:
        for field in REQUIRED_FIELDS:
            field_coverage[field] = field_coverage.get(field, 0) + (1 if field in metadata else 0)
    
    return {
        "coverage_percent": calculate_coverage_percentage(field_coverage),
        "missing_fields": find_missing_fields(field_coverage),
        "completion_score": calculate_completion_score(field_coverage)
    }
```

### Database Schema Requirements
- Performance monitoring metadata
- Health check timestamps
- Diagnostic data collection
- Optimization recommendation storage

---

## 5. API Standardization

### Core Capability
Consistent parameter naming, return formats, and error handling

### Standardized Parameters
```python
# Consistent naming
limit (not n_results, count, or max_results)
query (not search_term, text, or q)
metadata_filter (not where, filter, or conditions)

# Standard function signatures
def recall(query: str, limit: int = 5, metadata_filter: dict = None) -> List[MemoryResult]
def remember(content: str, title: str = None, tags: List[str] = None, 
            metadata: dict = None) -> OperationResult
def update_memory(memory_id: str, content: str = None, title: str = None,
                 metadata: dict = None) -> OperationResult
```

### Standardized Return Types
```python
# Memory query results
class MemoryResult:
    id: str
    content: str
    metadata: dict
    distance: float  # For semantic search
    
# Operation results
class OperationResult:
    success: bool
    message: str
    data: Any
    error: str
    error_type: str

# Statistics
class MemoryStats:
    total_memories: int
    recent_24h: int
    recent_7d: int
    unique_tags: int
    last_activity: str
```

### Implementation Requirements
- Type hints throughout all functions
- Consistent error handling patterns
- Standardized logging format
- Uniform response structures

---

## Database Schema v5 (Current Standard)

### Core Metadata Fields
```python
METADATA_SCHEMA_V5 = {
    # Identity & Ownership
    "instance_id": str,  # "cc" or "dt"
    "federation_id": str,  # "cc-federation" or "dt-federation"
    "created_by": str,  # "cc", "dt", "system"
    
    # Temporal
    "created_at": str,  # ISO timestamp
    "updated_at": str,  # ISO timestamp
    "version": int,  # Version number (auto-increments)
    
    # Classification
    "domain": str,  # identity, technical, session, personal, relationship, operational, creative, historical
    "category": str,  # core, protocol, solution, context, learning, discovery
    "memory_type": str,  # living, reference, ephemeral, static
    
    # Importance
    "priority": int,  # 0-3 (3=core/essential)
    "significance": float,  # 0.0-3.0
    "confidence": float,  # 0.0-1.0
    
    # Federation
    "federation_visible": bool,  # Share with other instances?
    "is_private": bool,  # Keep private from federation?
    "shared_with": str,  # Comma-separated: "dt,all" or "none"
    
    # Flags
    "is_essential": bool,  # Must load at startup?
    "needs_review": bool,  # Requires attention?
    "is_archived": bool,  # Archived status?
    
    # Content
    "title": str,  # Memory title
    "tags": str,  # Comma-separated tags
    "content_hash": str,  # SHA256 hash of content
    "hash_short": str,  # 8-char hash
    
    # Relationships
    "parent_id": str,  # Parent memory ID or null
    "child_ids": str,  # Comma-separated child IDs
    "related_ids": str,  # Comma-separated related IDs
    
    # System
    "source": str,  # "cc_bridge", "dt_memory", "shared_memory"
    "type": str,  # "memory", "context", "task"
}
```

---

## CRUD Operations (Complete)

### Create
```python
def remember(content, title=None, tags=None, metadata=None, significance=1.0):
    """Create new memory with full v5 schema support"""
    
def bulk_remember(memories_list):
    """Efficient batch creation"""
```

### Read  
```python
def recall(query, limit=5, metadata_filter=None):
    """Semantic search with filtering"""
    
def get_memory(memory_id):
    """Get specific memory by ID"""
    
def recent_memories(hours=24, limit=10):
    """Time-based retrieval"""
    
def get_all_memories(limit=None):
    """Full collection dump"""
```

### Update (CRITICAL - Currently Missing)
```python
def update_memory(memory_id, content=None, title=None, tags=None, 
                 metadata=None, append_mode=False):
    """Update existing memory - LIVING MEMORIES!"""
    
def update_metadata(memory_id, metadata_updates):
    """Update only metadata fields"""
    
def append_to_memory(memory_id, additional_content):
    """Append content to existing memory"""
```

### Delete
```python
def delete_memory(memory_id, soft_delete=True):
    """Remove memory (soft delete by default)"""
    
def archive_memory(memory_id):
    """Archive instead of delete"""
```

---

## Federation-Specific Features

### Cross-Instance Queries
```python
def federation_search(query, sources=["cc_shared", "dt_shared"], limit=10):
    """Search across multiple federation databases"""
    
def shared_memory_sync():
    """Synchronize shared memories between instances"""
```

### Access Control
```python
def set_federation_visibility(memory_id, visible=True, shared_with=None):
    """Control memory sharing across federation"""
    
def get_shareable_memories(instance_filter=None):
    """Get memories marked for federation sharing"""
```

### Instance Communication
```python
def notify_federation_update(memory_id, change_type):
    """Notify other instances of memory changes"""
    
def federation_heartbeat():
    """Health check across all federation instances"""
```

---

## Performance Requirements

### Response Times
- **Basic CRUD**: <10ms
- **Semantic Search**: <100ms (with proper filtering)
- **Health Checks**: <50ms
- **Batch Operations**: <500ms per 100 items
- **Federation Queries**: <200ms

### Scalability Targets
- **Memory Count**: Support 10,000+ memories per instance
- **Concurrent Users**: Handle CC + DT simultaneously
- **Daily Growth**: Support 100+ new memories/day
- **Search Performance**: Maintain speed as collection grows

### Storage Efficiency
- **Metadata Size**: <1KB per memory
- **Index Size**: <10% of total storage
- **Backup Speed**: <5 minutes for full backup
- **Startup Time**: <3 seconds for collection loading

---

## Missing Capabilities Analysis

### Current Gaps vs Required Features

#### 1. UPDATE Operations (CRITICAL)
```
❌ MISSING: cc_update_memory() in main CC tools
❌ MISSING: dt_update_memory() in main DT tools
✅ PRESENT: Shared memory has update capability
✅ PRESENT: ChromaDB supports updates natively

PRIORITY: HIGH - Implement immediately
```

#### 2. Full CRUD Exposure
```
❌ MISSING: Delete operations in main tools
❌ MISSING: Archive/soft delete patterns
✅ PRESENT: Create and Read fully implemented

PRIORITY: MEDIUM - Add for completeness
```

#### 3. Advanced Health Monitoring
```
❌ MISSING: Performance trend analysis
❌ MISSING: Automated optimization recommendations
✅ PRESENT: Basic health checks working

PRIORITY: LOW - Enhancement feature
```

#### 4. Federation Coordination
```
❌ MISSING: Cross-instance query coordination
❌ MISSING: Automatic sync mechanisms
❌ MISSING: Federation-wide search

PRIORITY: HIGH - Core federation feature
```

---

## Implementation Priority

### Phase 1: Core CRUD (Week 1)
1. **Implement UPDATE operations** - Critical missing feature
2. **Add DELETE/ARCHIVE operations** - Complete CRUD
3. **Standardize API signatures** - Consistency across instances
4. **Full v5 schema support** - All metadata fields

### Phase 2: Federation Features (Week 2)
1. **Cross-instance queries** - True federation search
2. **Shared memory protocols** - Sync mechanisms
3. **Access control implementation** - Privacy controls
4. **Federation health monitoring** - System-wide health

### Phase 3: Advanced Features (Week 3)
1. **Performance optimization** - Speed improvements
2. **Advanced health analytics** - Trend analysis
3. **Automated maintenance** - Self-optimization
4. **Enhanced relationships** - Memory linking

### Phase 4: Polish & Testing (Week 4)
1. **Comprehensive testing** - All features validated
2. **Performance benchmarking** - Meet targets
3. **Documentation completion** - Full API docs
4. **Migration tools** - From existing systems

---

## Success Criteria

### Functional Requirements
- ✅ All 5 Memory Evolution features working
- ✅ Complete CRUD operations (including UPDATE)
- ✅ Full v5 metadata schema support
- ✅ Federation search capabilities
- ✅ API standardization compliance

### Performance Requirements
- ✅ <100ms semantic search response
- ✅ Support 10,000+ memories per instance
- ✅ Concurrent CC/DT access
- ✅ Real-time federation sync

### Quality Requirements
- ✅ 100% data integrity (no corruption)
- ✅ Comprehensive error handling
- ✅ Full API documentation
- ✅ Test coverage >90%
- ✅ Migration path from existing systems

---

*This document serves as the complete specification for federation database capabilities. All features must be implemented to achieve true federation parity.*