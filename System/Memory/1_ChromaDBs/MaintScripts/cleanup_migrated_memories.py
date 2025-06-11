#!/usr/bin/env python3
"""
Clean up migrated memories from Federation databases
Keeps only native memories created directly in Federation
"""

import chromadb
from datetime import datetime

def cleanup_database(db_path, collection_name):
    """Remove migrated memories, keep native ones"""
    
    print(f"\n🔍 Processing {db_path}")
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)
    
    # Get all memories
    results = collection.get(limit=10000)
    
    if not results['ids']:
        print("  No memories found")
        return
    
    # Identify migrated memories
    to_delete = []
    to_keep = []
    
    migration_markers = [
        'migration_date',
        'original_original_date', 
        'source_database',
        'migration_type',
        'original_import_timestamp',
        'original_migration_date',
        'migrated_from_old_cc',
        'migrated_from_old_dt'
    ]
    
    for i, meta in enumerate(results['metadatas']):
        # Check if this is a migrated memory
        if any(marker in meta for marker in migration_markers):
            to_delete.append(results['ids'][i])
        else:
            to_keep.append(results['ids'][i])
    
    print(f"  Total memories: {len(results['ids'])}")
    print(f"  To delete (migrated): {len(to_delete)}")
    print(f"  To keep (native): {len(to_keep)}")
    
    # Delete migrated memories
    if to_delete:
        print(f"\n  🗑️  Deleting {len(to_delete)} migrated memories...")
        # Delete in batches
        batch_size = 100
        for i in range(0, len(to_delete), batch_size):
            batch = to_delete[i:i+batch_size]
            collection.delete(ids=batch)
            print(f"    Deleted batch {i//batch_size + 1}/{(len(to_delete)-1)//batch_size + 1}")
        
        print(f"  ✅ Deletion complete")
    else:
        print("  ✅ No migrated memories to delete")
    
    # Verify final count
    final_count = collection.count()
    print(f"  📊 Final memory count: {final_count}")
    
    return len(to_delete), len(to_keep)

def main():
    print("🧹 Federation Memory Cleanup")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Clean CC Federation
    cc_deleted, cc_kept = cleanup_database(
        '/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation',
        'cc_memories'
    )
    
    # Clean DT Federation
    dt_deleted, dt_kept = cleanup_database(
        '/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation',
        'dt_memories'
    )
    
    print("\n" + "=" * 50)
    print("🎯 CLEANUP SUMMARY")
    print(f"CC: Deleted {cc_deleted}, Kept {cc_kept}")
    print(f"DT: Deleted {dt_deleted}, Kept {dt_kept}")
    print(f"Total deleted: {cc_deleted + dt_deleted}")
    print(f"Total kept: {cc_kept + dt_kept}")
    print("\n✅ Cleanup complete! Native memories preserved.")

if __name__ == "__main__":
    main()