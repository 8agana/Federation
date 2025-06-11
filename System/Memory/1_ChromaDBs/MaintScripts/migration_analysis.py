#!/usr/bin/env python3
"""
Analyze old databases to prepare migration plan
"""

import chromadb
import os
from datetime import datetime
from collections import defaultdict

def analyze_old_database(db_path, collection_names):
    """Analyze an old database"""
    if not os.path.exists(db_path):
        return None
    
    results = {
        'path': db_path,
        'collections': {},
        'total_memories': 0,
        'date_range': {'earliest': None, 'latest': None},
        'id_patterns': defaultdict(int)
    }
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        
        for coll_name in collection_names:
            try:
                collection = client.get_collection(coll_name)
                count = collection.count()
                results['collections'][coll_name] = count
                results['total_memories'] += count
                
                # Sample memories to understand structure
                if count > 0:
                    memories = collection.get(limit=min(count, 1000))
                    
                    # Analyze ID patterns
                    for id in memories['ids']:
                        if '_' in id:
                            prefix = id.split('_')[0]
                            results['id_patterns'][prefix] += 1
                            
                            # Try to extract date
                            parts = id.split('_')
                            if len(parts) >= 2 and parts[1].isdigit() and len(parts[1]) == 8:
                                date_str = parts[1]
                                if not results['date_range']['earliest'] or date_str < results['date_range']['earliest']:
                                    results['date_range']['earliest'] = date_str
                                if not results['date_range']['latest'] or date_str > results['date_range']['latest']:
                                    results['date_range']['latest'] = date_str
                    
            except Exception as e:
                results['collections'][coll_name] = f"Error: {e}"
    
    except Exception as e:
        results['error'] = str(e)
    
    return results

def main():
    print("🔍 MIGRATION ANALYSIS REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define databases to check
    databases = {
        'CC': [
            {
                'path': '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/CC_Individual/Databases/cc_chroma_db',
                'collections': ['cc_conversations', 'cc_memories']
            }
        ],
        'DT': [
            {
                'path': '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/dt_memory_v5',
                'collections': ['dt_unified_memories']
            },
            {
                'path': '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/dt_chroma_db',
                'collections': ['dt_memories', 'dt_identity_board', 'dt_messages', 'dt_memories_v5']
            },
            {
                'path': '/Users/samuelatagana/Documents/Claude_Home/System/Memory/ChromaDB_Systems/DT_Individual/Databases/archived_old_databases/dt_chroma_db',
                'collections': ['dt_memories', 'dt_identity_board', 'dt_messages', 'dt_memories_v5']
            }
        ]
    }
    
    # Analyze each instance
    for instance, db_list in databases.items():
        print(f"\n{'='*20} {instance} DATABASES {'='*20}")
        
        total_unique_memories = 0
        all_dates = []
        
        for db_info in db_list:
            print(f"\n📁 {db_info['path'].split('/')[-3:]}")
            
            result = analyze_old_database(db_info['path'], db_info['collections'])
            
            if result:
                if 'error' in result:
                    print(f"   ❌ Error: {result['error']}")
                else:
                    print(f"   Total memories: {result['total_memories']}")
                    print(f"   Collections:")
                    for coll, count in result['collections'].items():
                        print(f"     - {coll}: {count}")
                    
                    if result['date_range']['earliest']:
                        earliest = result['date_range']['earliest']
                        latest = result['date_range']['latest']
                        print(f"   Date range: {earliest[:4]}-{earliest[4:6]}-{earliest[6:8]} to {latest[:4]}-{latest[4:6]}-{latest[6:8]}")
                        all_dates.extend([earliest, latest])
                    
                    if result['id_patterns']:
                        print(f"   ID patterns: {dict(result['id_patterns'])}")
                    
                    total_unique_memories += result['total_memories']
            else:
                print(f"   ❌ Database not found")
        
        if all_dates:
            all_dates.sort()
            print(f"\n📊 {instance} SUMMARY:")
            print(f"   Potential memories to migrate: ~{total_unique_memories}")
            print(f"   Date range: {all_dates[0][:4]}-{all_dates[0][4:6]}-{all_dates[0][6:8]} to {all_dates[-1][:4]}-{all_dates[-1][4:6]}-{all_dates[-1][6:8]}")
    
    print("\n" + "="*60)
    print("\n🎯 MIGRATION CHALLENGES:")
    print("1. DT has fragmented memories across multiple databases")
    print("2. Need to deduplicate DT memories during consolidation")
    print("3. Must preserve original dates in new IDs")
    print("4. Should maintain metadata but mark as 'migrated_properly'")
    print("5. Need to handle different collection names and schemas")

if __name__ == "__main__":
    main()