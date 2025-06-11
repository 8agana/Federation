#!/usr/bin/env python3
"""
DT Memory Migration Script - Phase 1: Extract and Prepare
Extracts all memories from old DT Individual ChromaDB with complete metadata
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def extract_dt_memories() -> List[Dict[str, Any]]:
    """Extract all DT memories with complete metadata from old database"""
    
    old_db_path = '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/dt_memory_v5/chroma.sqlite3'
    
    if not os.path.exists(old_db_path):
        raise FileNotFoundError(f"Old DT database not found: {old_db_path}")
    
    conn = sqlite3.connect(old_db_path)
    cursor = conn.cursor()
    
    # Get all embeddings - we need to check the actual table structure
    cursor.execute("PRAGMA table_info(embeddings)")
    embedding_columns = [col[1] for col in cursor.fetchall()]
    print(f"Embedding columns: {embedding_columns}")
    
    # Get embeddings with their IDs
    cursor.execute("SELECT id, embedding_id FROM embeddings")
    embeddings = cursor.fetchall()
    print(f"Found {len(embeddings)} embeddings in old DT database")
    
    memories = []
    
    for embedding_id, chroma_id in embeddings:
        # Get all metadata for this embedding
        cursor.execute("""
            SELECT key, string_value, int_value, float_value, bool_value
            FROM embedding_metadata 
            WHERE id = ?
        """, (embedding_id,))
        
        metadata_rows = cursor.fetchall()
        
        # Build metadata dictionary
        metadata = {}
        for key, str_val, int_val, float_val, bool_val in metadata_rows:
            if str_val is not None:
                metadata[key] = str_val
            elif int_val is not None:
                metadata[key] = int_val
            elif float_val is not None:
                metadata[key] = float_val
            elif bool_val is not None:
                metadata[key] = bool(bool_val)
        
        # Try to get the actual content/document
        content = None
        
        # Check if there's a documents table or content in metadata
        if 'content' in metadata:
            content = metadata['content']
        elif 'title' in metadata:
            # Use title as content if no content field
            content = metadata.get('title', 'DT Memory')
        else:
            content = f"DT Memory (ID: {chroma_id})"
        
        # Extract title
        title = metadata.get('title', content[:50] + "..." if len(content) > 50 else content)
        
        # Extract and clean tags
        tags = []
        if 'tags' in metadata and metadata['tags']:
            tags_str = metadata['tags']
            # Handle different tag formats
            if ':' in tags_str:
                tags = [tag.strip() for tag in tags_str.split(':') if tag.strip()]
            elif ',' in tags_str:
                tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            else:
                tags = [tags_str.strip()]
        
        # Add migration tag
        tags.append('migrated_from_old_dt')
        
        # Determine significance from metadata
        significance = 1.0  # default
        if 'priority' in metadata:
            if metadata['priority'] == 'high':
                significance = 2.0
            elif metadata['priority'] == 'low':
                significance = 0.5
        
        memory = {
            'content': content,
            'title': title,
            'tags': tags,
            'significance': significance,
            'metadata': {
                'original_id': chroma_id,
                'original_embedding_id': embedding_id,
                'migration_date': datetime.now().isoformat(),
                'source_database': 'DT_Individual',
                **metadata  # Include all original metadata
            }
        }
        
        memories.append(memory)
    
    conn.close()
    print(f"Extracted {len(memories)} DT memories with complete metadata")
    return memories

def main():
    """Extract DT memories and save for import"""
    print("Extracting DT memories from old database...")
    print("=" * 50)
    
    try:
        memories = extract_dt_memories()
        
        # Save extracted memories
        output_file = "/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_extracted.json"
        with open(output_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        print(f"Successfully extracted {len(memories)} DT memories")
        print(f"Saved to: {output_file}")
        
        # Show sample memory structure
        if memories:
            print("\nSample memory structure:")
            print(json.dumps(memories[0], indent=2)[:500] + "...")
        
        return 0
        
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
