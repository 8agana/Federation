#!/usr/bin/env python3
"""
Direct Federation Import Script
Imports memories directly into federation ChromaDB using exact schema
"""

import sqlite3
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List

def generate_memory_id(content: str, timestamp: str = None) -> str:
    """Generate federation-style memory ID"""
    if not timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate short hash from content
    content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
    
    return f"dt_{timestamp}_{content_hash}"

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

def insert_memory_direct(conn, memory_data: Dict[str, Any], collection_name: str = "dt_memories"):
    """Insert memory directly into federation database"""
    
    cursor = conn.cursor()
    
    # Get collection info
    collection_id, metadata_segment_id = get_collection_info(conn, collection_name)
    
    # Generate memory ID
    memory_id = generate_memory_id(memory_data['content'])
    
    # Insert embedding record
    cursor.execute("""
        INSERT INTO embeddings (segment_id, embedding_id, seq_id, created_at)
        VALUES (?, ?, ?, ?)
    """, (metadata_segment_id, memory_id, b'', datetime.now()))
    
    embedding_row_id = cursor.lastrowid
    
    # Prepare metadata
    base_metadata = {
        'category': 'memory',
        'chroma:document': memory_data['content'],
        'content_hash': hashlib.sha256(memory_data['content'].encode()).hexdigest(),
        'created_at': datetime.now().isoformat(),
        'created_by': 'migration_script',
        'domain': 'technical',
        'federation_id': 'dt-federation',
        'hash_short': hashlib.sha256(memory_data['content'].encode()).hexdigest()[:8],
        'instance_id': 'dt',
        'memory_type': 'living',
        'source': 'migration_from_old_db',
        'tags': ', '.join(memory_data.get('tags', [])),
        'title': memory_data.get('title', 'Migrated Memory'),
        'type': 'memory',
        'updated_at': datetime.now().isoformat(),
    }
    
    # Add original metadata
    if 'metadata' in memory_data:
        for key, value in memory_data['metadata'].items():
            if key not in base_metadata and value is not None:
                # Convert to string for storage
                base_metadata[f'original_{key}'] = str(value)
    
    # Insert all metadata
    for key, value in base_metadata.items():
        if value is not None:
            cursor.execute("""
                INSERT INTO embedding_metadata (id, key, string_value)
                VALUES (?, ?, ?)
            """, (embedding_row_id, key, str(value)))
    
    return memory_id, embedding_row_id

def test_direct_import():
    """Test direct import with a few memories"""
    
    # Load prepared memories
    with open('/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json', 'r') as f:
        memories = json.load(f)
    
    print(f"Testing direct import with first 3 of {len(memories)} memories...")
    
    # Connect to federation database
    db_path = '/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation/chroma.sqlite3'
    conn = sqlite3.connect(db_path)
    
    try:
        test_memories = memories[5:8]  # Skip the ones we already imported manually
        
        for i, memory in enumerate(test_memories):
            print(f"Importing test memory {i+1}: {memory['title'][:50]}...")
            
            memory_id, row_id = insert_memory_direct(conn, memory)
            print(f"  Created: {memory_id} (row {row_id})")
        
        conn.commit()
        print("Test import successful!")
        
        # Verify the import
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM embeddings")
        total_count = cursor.fetchone()[0]
        print(f"Total embeddings after test: {total_count}")
        
    except Exception as e:
        print(f"Test import failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    test_direct_import()
