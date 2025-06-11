#!/usr/bin/env python3
"""
Memory Import Script - Import extracted memories into federation system
"""

import json
import time
import sys

def load_extracted_memories(file_path: str):
    """Load extracted memories from JSON file"""
    try:
        with open(file_path, 'r') as f:
            memories = json.load(f)
        print(f"Loaded {len(memories)} memories from {file_path}")
        return memories
    except Exception as e:
        print(f"Error loading memories: {e}")
        return []

def import_dt_memories():
    """Import DT memories into federation system"""
    
    dt_memories = load_extracted_memories("/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_extracted.json")
    
    if not dt_memories:
        print("No DT memories to import")
        return 0
    
    print(f"Starting import of {len(dt_memories)} DT memories...")
    imported_count = 0
    errors = []
    
    # We'll import these in batches and use the actual MCP functions
    # For now, let's prepare the data and output what we would import
    
    for i, memory in enumerate(dt_memories):
        try:
            # Prepare memory for import
            content = memory['content']
            title = memory.get('title', 'Migrated Memory')
            tags = memory.get('tags', [])
            metadata = memory.get('metadata', {})
            
            # Clean up tags - remove empty ones
            tags = [tag for tag in tags if tag and tag.strip()]
            
            print(f"Memory {i+1}: {title[:50]}...")
            print(f"  Tags: {tags}")
            print(f"  Metadata keys: {list(metadata.keys())}")
            
            imported_count += 1
            
            # Small delay to prevent overwhelming
            if i % 10 == 0 and i > 0:
                print(f"Processed {i}/{len(dt_memories)} memories...")
                time.sleep(0.1)
            
        except Exception as e:
            error_msg = f"Error processing memory {i}: {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    print(f"\nDT Import Summary:")
    print(f"  Processed: {imported_count}/{len(dt_memories)} memories")
    print(f"  Errors: {len(errors)}")
    
    return imported_count

def main():
    """Main import function"""
    print("Starting Memory Import Process...")
    print("=" * 50)
    
    # Import DT memories
    dt_imported = import_dt_memories()
    
    print("=" * 50)
    print(f"Import Complete:")
    print(f"  DT Memories: {dt_imported}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
