#!/usr/bin/env python3
"""
Batch Memory Import Script
Uses the federation system to import all extracted memories
"""

import json
import time
import subprocess
import sys
import os

def import_memory_via_claude(memory_data):
    """Import a single memory using Claude's dt_remember function"""
    
    # Prepare the import command
    content = memory_data['content']
    title = memory_data.get('title', 'Migrated Memory')
    tags = memory_data.get('tags', [])
    metadata = memory_data.get('metadata', {})
    significance = memory_data.get('significance', 1.0)
    
    # Clean metadata - remove very long fields that might cause issues
    clean_metadata = {}
    for key, value in metadata.items():
        if key == 'chroma:document':
            continue  # Skip the full document content in metadata
        if isinstance(value, str) and len(value) > 200:
            clean_metadata[key] = value[:200] + "..."
        else:
            clean_metadata[key] = value
    
    # Create the memory import data
    import_data = {
        'content': content,
        'title': title,
        'tags': tags,
        'metadata': clean_metadata,
        'significance': significance
    }
    
    return import_data

def batch_import_dt_memories():
    """Import all DT memories in batches"""
    
    # Load DT memories
    with open('/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_extracted.json', 'r') as f:
        dt_memories = json.load(f)
    
    print(f"Starting batch import of {len(dt_memories)} DT memories...")
    
    # Prepare all memories for import
    import_data = []
    for i, memory in enumerate(dt_memories):
        try:
            prepared = import_memory_via_claude(memory)
            import_data.append(prepared)
            
            if (i + 1) % 20 == 0:
                print(f"Prepared {i + 1}/{len(dt_memories)} memories...")
                
        except Exception as e:
            print(f"Error preparing memory {i}: {e}")
    
    # Save prepared data for manual import if needed
    with open('/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json', 'w') as f:
        json.dump(import_data, f, indent=2)
    
    print(f"Prepared {len(import_data)} memories for import")
    print("Saved to: /Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json")
    
    return import_data

def batch_import_cc_memories():
    """Import all CC memories in batches"""
    
    # Load CC memories
    with open('/Users/samuelatagana/Documents/Federation/Scripts/cc_memories_extracted.json', 'r') as f:
        cc_memories = json.load(f)
    
    print(f"Starting batch import of {len(cc_memories)} CC memories...")
    
    # Prepare all memories for import
    import_data = []
    for i, memory in enumerate(cc_memories):
        try:
            prepared = import_memory_via_claude(memory)
            import_data.append(prepared)
            
            if (i + 1) % 50 == 0:
                print(f"Prepared {i + 1}/{len(cc_memories)} memories...")
                
        except Exception as e:
            print(f"Error preparing memory {i}: {e}")
    
    # Save prepared data for manual import if needed
    with open('/Users/samuelatagana/Documents/Federation/Scripts/cc_memories_prepared.json', 'w') as f:
        json.dump(import_data, f, indent=2)
    
    print(f"Prepared {len(import_data)} memories for import")
    print("Saved to: /Users/samuelatagana/Documents/Federation/Scripts/cc_memories_prepared.json")
    
    return import_data

def main():
    """Main batch import function"""
    print("Starting Batch Memory Import Process...")
    print("=" * 60)
    
    # Prepare DT memories
    dt_prepared = batch_import_dt_memories()
    
    print("\n" + "=" * 60)
    
    # Prepare CC memories
    cc_prepared = batch_import_cc_memories()
    
    print("\n" + "=" * 60)
    print(f"Batch Preparation Complete:")
    print(f"  DT Memories Prepared: {len(dt_prepared)}")
    print(f"  CC Memories Prepared: {len(cc_prepared)}")
    print(f"  Total: {len(dt_prepared) + len(cc_prepared)} memories")
    print("\nPrepared files saved for manual import via MCP system")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
