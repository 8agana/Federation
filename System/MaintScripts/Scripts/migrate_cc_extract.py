#!/usr/bin/env python3
"""
CC Memory Migration Script - Phase 1: Extract and Prepare
Extracts all memories from old CC Individual ChromaDB with complete metadata
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any

def extract_cc_memories() -> List[Dict[str, Any]]:
    """Extract all CC memories with complete metadata from old database"""
    
    old_db_path = '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/CC_Individual/Databases/cc_chroma_db/chroma.sqlite3'
    
    if not os.path.exists(old_db_path):
        raise FileNotFoundError(f"Old CC database not found: {old_db_path}")
    
    conn = sqlite3.connect(old_db_path)
    cursor = conn.cursor()
    
    # Get all embeddings
    cursor.execute("SELECT id, embedding_id FROM embeddings")
    embeddings = cursor.fetchall()
    print(f"Found {len(embeddings)} embeddings in old CC database")
    
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
        
        # Extract content - CC might have different field names
        content = None
        if 'content' in metadata:
            content = metadata['content']
        elif 'conversation_summary' in metadata:
            content = metadata['conversation_summary']
        elif 'summary' in metadata:
            content = metadata['summary']
        elif 'title' in metadata:
            content = metadata['title']
        else:
            content = f"CC Memory (ID: {chroma_id})"
        
        # Extract title
        title = metadata.get('title', 
               metadata.get('conversation_title',
               content[:50] + "..." if len(content) > 50 else content))
        
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
        
        # Add CC-specific tags based on metadata
        if 'conversation_date' in metadata:
            tags.append(f"date_{metadata['conversation_date']}")
        if 'source_file' in metadata:
            tags.append('from_file')
        if 'migration_type' in metadata:
            tags.append(f"migration_{metadata['migration_type']}")
        
        # Add migration tag
        tags.append('migrated_from_old_cc')
        
        # Determine significance
        significance = 1.0  # default
        if 'is_essential' in metadata and metadata['is_essential']:
            significance = 2.0
        elif 'priority' in metadata:
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
                'source_database': 'CC_Individual',
                **metadata  # Include all original metadata
            }
        }
        
        memories.append(memory)
    
    conn.close()
    print(f"Extracted {len(memories)} CC memories with complete metadata")
    return memories

def main():
    """Extract CC memories and save for import"""
    print("Extracting CC memories from old database...")
    print("=" * 50)
    
    try:
        memories = extract_cc_memories()
        
        # Save extracted memories
        output_file = "/Users/samuelatagana/Documents/Federation/Scripts/cc_memories_extracted.json"
        with open(output_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        print(f"Successfully extracted {len(memories)} CC memories")
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
