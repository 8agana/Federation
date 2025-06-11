#!/usr/bin/env python3
"""Test ChromaDB connection and collection names"""

import chromadb

def test_collections():
    base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
    
    print("Testing ChromaDB Collections")
    print("=" * 50)
    
    # Test CC Federation
    print("\nCC Federation:")
    try:
        cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
        collections = cc_client.list_collections()
        print(f"Collections found: {len(collections)}")
        for col in collections:
            print(f"  - {col.name}: {col.count()} items")
            
        # Try to get specific collection
        try:
            cc_memories = cc_client.get_collection("cc_memories")
            print(f"✓ 'cc_memories' collection: {cc_memories.count()} items")
        except:
            print("✗ Could not find 'cc_memories' collection")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Test DT Federation  
    print("\nDT Federation:")
    try:
        dt_client = chromadb.PersistentClient(path=f"{base_path}/dt-federation")
        collections = dt_client.list_collections()
        print(f"Collections found: {len(collections)}")
        for col in collections:
            print(f"  - {col.name}: {col.count()} items")
            
        # Try to get specific collection
        try:
            dt_memories = dt_client.get_collection("dt_memories")
            print(f"✓ 'dt_memories' collection: {dt_memories.count()} items")
        except:
            print("✗ Could not find 'dt_memories' collection")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_collections()