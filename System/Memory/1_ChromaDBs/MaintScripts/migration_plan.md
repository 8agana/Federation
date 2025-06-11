# Federation Memory Migration Plan

## Overview
Migrate historical memories from Claude_Home to Federation while preserving original dates and cleaning up metadata.

## Current State (Post-Cleanup)
- **CC Federation**: 131 native memories
- **DT Federation**: 46 native memories
- **Backups**: Saved at `/backups/20250609_pre_cleanup/`

## Migration Sources

### CC Migration (Phase 1)
**Source**: `/Claude_Home/System/Memory/ChromaDB_Systems/CC_Individual/Databases/cc_chroma_db`
- Collection: `cc_conversations`
- Count: 769 memories
- Date Range: May 28-30, 2025
- Complexity: Low (single source)

### DT Migration (Phase 2)
**Sources**: Multiple databases need consolidation
1. `/DT_Individual/Databases/dt_memory_v5` (134 memories)
2. `/archived_old_databases/dt_chroma_db` (358 memories across 4 collections)
- Total: ~492 memories (before deduplication)
- Date Range: June 1-8, 2025
- Complexity: High (fragmentation, duplicates)

## Implementation Steps

### Step 1: Backup Current State
```bash
cd /Federation/System/Memory/1_ChromaDBs
mkdir -p backups/20250609_pre_migration
cp -r cc-federation dt-federation backups/20250609_pre_migration/
```

### Step 2: CC Migration Script
Key features:
- Preserve original date in ID (from memory content or ID)
- Clean metadata (remove migration markers)
- Add single "migration_source": "claude_home_proper"
- Maintain original content integrity

### Step 3: DT Consolidation & Migration
Key features:
- Merge memories from multiple sources
- Deduplicate by content hash
- Preserve earliest timestamp for duplicates
- Consolidate identity_board and messages
- Generate proper IDs with original dates

### Step 4: Validation
- Compare counts (before/after)
- Verify date ranges preserved
- Test memory retrieval
- Check for missing memories

## ID Format Standards

### Current (Problematic)
`cc_20250608_195902_hash` - Shows migration date for May 28 memory

### New (Correct)
`cc_20250528_originaltime_hash` - Shows actual creation date

## Metadata Cleanup

### Remove
- `migration_date`
- `original_original_date`
- `original_import_timestamp`
- All `original_*` prefixed fields

### Keep/Add
- `created_at`: Original creation timestamp
- `migration_source`: "claude_home_proper"
- `migrated_at`: Current timestamp
- Essential metadata (tags, domain, category)

## Success Metrics
1. CC: ~900 total memories (131 native + 769 migrated)
2. DT: ~400-500 total memories (46 native + deduplicated migrations)
3. All memories have correct date-based IDs
4. Clean metadata without redundancy
5. Full audit trail of migration

## Rollback Plan
If issues occur:
1. Restore from `/backups/20250609_pre_migration/`
2. Analyze what went wrong
3. Fix migration script
4. Retry with improvements

## Next Actions
1. Create `migrate_cc_memories.py`
2. Create `migrate_dt_memories.py`
3. Run test migrations on small batches
4. Execute full migration
5. Validate results