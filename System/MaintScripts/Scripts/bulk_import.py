#!/usr/bin/env python3
"""
Bulk Memory Import Using Federation Bridge
Direct import into federation system
"""

import sys
import os
import json
import sqlite3
from datetime import datetime

# Add the federation system path
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/MCP')

def bulk_import_to_federation():
    """Import memories directly into federation database"""
    
    # Load prepared memories
    with open('/Users/samuelatagana/Documents/Federation/Scripts/dt_memories_prepared.json', 'r') as f:
        dt_memories = json.load(f)
    
    with open('/Users/samuelatagana/Documents/Federation/Scripts/cc_memories_prepared.json', 'r') as f:
        cc_memories = json.load(f)
    
    print(f"Bulk importing {len(dt_memories)} DT memories and {len(cc_memories)} CC memories...")
    
    # Write import data for processing
    import_data = {
        'dt_memories': dt_memories,
        'cc_memories': cc_memories,
        'import_timestamp': datetime.now().isoformat(),
        'total_count': len(dt_memories) + len(cc_memories)
    }
    
    # Save for bulk processing
    bulk_file = '/Users/samuelatagana/Documents/Federation/Scripts/bulk_import_data.json'
    with open(bulk_file, 'w') as f:
        json.dump(import_data, f, indent=2)
    
    print(f"Bulk import data prepared: {bulk_file}")
    print(f"Ready to import {import_data['total_count']} memories")
    
    return import_data

if __name__ == "__main__":
    result = bulk_import_to_federation()
    print("Bulk import preparation complete")
