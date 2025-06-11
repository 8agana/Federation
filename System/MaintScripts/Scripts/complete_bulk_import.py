#!/usr/bin/env python3
"""
Complete Bulk Import Script - Finishes the migration CC is taking over from DT
Imports all remaining memories directly into federation ChromaDB
"""

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List
import sys

def generate_memory_id(content: str, timestamp: str = None, prefix: str = "dt") -> str:
    """Generate federation-style memory ID"""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate short hash from content
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
    
    return f"{prefix}_{timestamp}_{content_hash}"

def get_collection_info(conn, collection_name: str):
    """Get collection ID and metadata segment ID"""
    cursor = conn.cursor()
    
    # Find collection by name
    cursor.execute("SELECT id FROM collections WHERE name = ?", (collection_name,))
    collection_result = cursor.fetchone()
    
    if not collection_result:
        raise ValueError(f"Collection {collection_name} not found")
    
    collection_id = collection_result[0]
    
    # Find metadata segment for this collection
    cursor.execute("""
        SELECT id FROM segments 
        WHERE collection = ? AND scope = 'METADATA'
    """, (collection_id,))
    
    segment_result = cursor.fetchone()
    if not segment_result:
        raise ValueError(f"Metadata segment not found for collection {collection_name}")
    
    return collection_id, segment_result[0]

def insert_memory_direct(conn, memory_data: Dict[str, Any], collection_name: str, instance_prefix: str):
    """Insert memory directly into federation database"""
    
    cursor = conn.cursor()
    
    # Get collection info
    collection_id, metadata_segment_id = get_collection_info(conn, collection_name)
    
    # Generate memory ID
    memory_id = generate_memory_id(memory_data['content'], prefix=instance_prefix)
    
    # Insert embedding record
    cursor.execute("""
        INSERT INTO embeddings (segment_id, embedding_id, seq_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (metadata_segment_id, memory_id, b'', datetime.now()))
    
    embedding_row_id = cursor.lastrowid
    
    # Prepare metadata
    base_metadata = {
        'category': memory_data.get('metadata', {}).get('category', 'memory'),
        'chroma:document': memory_data['content'],
        'content_hash': hashlib.sha256(memory_data['content'].encode()).hexdigest(),
        'created_at': memory_data.get('metadata', {}).get('created_at', datetime.now().isoformat()),
        'created_by': memory_data.get('metadata', {}).get('created_by', 'migration_script'),
        'domain': memory_data.get('metadata', {}).get('domain', 'operational'),
        'federation_id': f'{instance_prefix}-federation',
        'hash_short': hashlib.sha256(memory_data['content'].encode()).hexdigest()[:8],
        'instance_id': instance_prefix,
        'memory_type': memory_data.get('metadata', {}).get('memory_type', 'living'),
        'source': 'migration_from_old_db',
        'tags': ', '.join(memory_data.get('tags', [])),
        'title': memory_data.get('title', 'Migrated Memory'),
        'type': 'memory',
        'updated_at': memory_data.get('metadata', {}).get('updated_at', datetime.now().isoformat()),
    }
    
    # Add significance if present
    if 'significance' in memory_data:
        base_metadata['significance'] = str(memory_data['significance'])
    
    # Add original metadata fields
    if 'metadata' in memory_data:
        for key, value in memory_data['metadata'].items():
            if key not in base_metadata and value is not None:
                # Preserve original metadata with prefix
                base_metadata[f'original_{key}'] = str(value)
    
    # Insert all metadata
    for key, value in base_metadata.items():
        if value is not None:
            cursor.execute("""
                INSERT INTO embedding_metadata (id, key, string_value)
                VALUES (?, ?, ?)
            """, (embedding_row_id, key, str(value)))
    
    return memory_id, embedding_row_id

def bulk_import_memories(memories_file: str, db_path: str, collection_name: str, instance_prefix: str, skip_count: int = 0):
    """Bulk import memories from prepared JSON file"""
    
    # Load prepared memories
    print(f"Loading memories from {memories_file}...")
    with open(memories_file, 'r') as f:
        memories = json.load(f)
    
    total_memories = len(memories)
    memories_to_import = memories[skip_count:]
    
    print(f"Total memories: {total_memories}")
    print(f"Already imported: {skip_count}")
    print(f"To import: {len(memories_to_import)}")
    print(f"Target database: {db_path}")
    print(f"Collection: {collection_name}")
    print("=" * 60)
    
    # Connect to federation database
    conn = sqlite3.connect(db_path)
    
    try:
        # Get initial count
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        initial_count = cursor.fetchone()[0]
        print(f"Initial embedding count: {initial_count}")
        
        imported = 0
        failed = 0
        
        for i, memory in enumerate(memories_to_import):
            try:
                # Progress indicator
                if i % 10 == 0:
                    print(f"Progress: {i}/{len(memories_to_import)} ({(i/len(memories_to_import)*100):.1f}%)")
                
                memory_id, row_id = insert_memory_direct(conn, memory, collection_name, instance_prefix)
                imported += 1
                
                # Commit every 50 memories for safety
                if imported % 50 == 0:
                    conn.commit()
                    
            except Exception as e:
                failed += 1
                print(f"  ERROR importing memory {skip_count + i}: {e}")
                print(f"  Memory title: {memory.get('title', 'Unknown')[:50]}")
                continue
        
        # Final commit
        conn.commit()
        
        # Get final count
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        final_count = cursor.fetchone()[0]
        
        print("=" * 60)
        print(f"IMPORT COMPLETE!")
        print(f"Successfully imported: {imported}")
        print(f"Failed: {failed}")
        print(f"Final embedding count: {final_count} (added {final_count - initial_count})")
        
    except Exception as e:
        print(f"Bulk import failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def main():
    """Main function to complete the migration"""
    
    print("=" * 60)
    print("COMPLETING FEDERATION MEMORY MIGRATION")
    print("Taking over from DT's handoff")
    print("=" * 60)
    
    # Import remaining DT memories (134 total - 8 already done = 126 remaining)
    print("\n1. IMPORTING DT MEMORIES...")
    bulk_import_memories(
        memories_file='/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json',
        db_path='/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation/chroma.sqlite3',
        collection_name='dt_memories',
        instance_prefix='dt',
        skip_count=8  # Skip the 8 already imported
    )
    
    # Import all CC memories (768 total)
    print("\n2. IMPORTING CC MEMORIES...")
    bulk_import_memories(
        memories_file='/Users/samuelatagana/Documents/Federation/Scripts/cc_memories_prepared.json',
        db_path='/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation/chroma.sqlite3',
        collection_name='cc_memories',
        instance_prefix='cc',
        skip_count=0  # Import all CC memories
    )
    
    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("All historical memories (May 30 - June 6) now available in federation system")
    print("=" * 60)

if __name__ == "__main__":
    main()