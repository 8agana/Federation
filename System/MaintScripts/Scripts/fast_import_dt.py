#!/usr/bin/env python3
"""
Fast Memory Import Script
Imports all prepared memories efficiently
"""

import json
import time

# Load the prepared memories
with open('/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json', 'r') as f:
    dt_memories = json.load(f)

print(f"Importing {len(dt_memories)} DT memories...")

# Process memories in groups
batch_size = 20
total_imported = 0

for batch_start in range(0, len(dt_memories), batch_size):
    batch_end = min(batch_start + batch_size, len(dt_memories))
    batch = dt_memories[batch_start:batch_end]
    
    print(f"Processing batch {batch_start//batch_size + 1}: memories {batch_start+1}-{batch_end}")
    
    # Create import commands for this batch
    import_commands = []
    for memory in batch:
        cmd = {
            'content': memory['content'],
            'title': memory['title'],
            'tags': memory['tags'],
            'metadata': memory['metadata'],
            'significance': memory['significance']
        }
        import_commands.append(cmd)
    
    # Save this batch for manual import
    batch_file = f"/Users/samuelatagana/Documents/Federation/Scripts/dt_batch_{batch_start//batch_size + 1}.json"
    with open(batch_file, 'w') as f:
        json.dump(import_commands, f, indent=2)
    
    total_imported += len(batch)
    print(f"  Prepared {len(batch)} memories in {batch_file}")

print(f"\nDT Import Preparation Complete:")
print(f"  Total memories prepared: {total_imported}")
print(f"  Number of batch files: {(len(dt_memories) + batch_size - 1) // batch_size}")
print("\nBatch files ready for import via MCP system")
