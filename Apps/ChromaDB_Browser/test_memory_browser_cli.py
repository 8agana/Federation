#!/usr/bin/env python3
"""Test memory browser initialization without GUI"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chromadb

def test_memory_loading():
    """Test the memory loading logic"""
    base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
    
    clients = {}
    collections = {}
    all_memories = []
    
    print("Testing Memory Browser Initialization")
    print("=" * 50)
    
    # CC Federation Database
    try:
        print("\nConnecting to CC Federation...")
        clients['cc'] = chromadb.PersistentClient(
            path=f"{base_path}/cc-federation"
        )
        collections['cc'] = clients['cc'].get_collection("cc_memories")
        print(f"✓ Loaded CC Federation collection with {collections['cc'].count()} memories")
    except Exception as e:
        print(f"✗ Could not load CC Federation collection: {e}")
        collections['cc'] = None
    
    # DT Federation Database
    try:
        print("\nConnecting to DT Federation...")
        clients['dt'] = chromadb.PersistentClient(
            path=f"{base_path}/dt-federation"
        )
        collections['dt'] = clients['dt'].get_collection("dt_memories")
        print(f"✓ Loaded DT Federation collection with {collections['dt'].count()} memories")
    except Exception as e:
        print(f"✗ Could not load DT Federation collection: {e}")
        collections['dt'] = None
    
    # Load memories
    print("\nLoading memories...")
    print(f"Collections available: {list(collections.keys())}")
    
    for collection_name, collection in collections.items():
        if collection is not None:
            try:
                print(f"\nLoading from {collection_name}...")
                results = collection.get(limit=10)  # Just get 10 for testing
                
                print(f"  Found {len(results['ids'])} memories (limited to 10)")
                print(f"  First memory ID: {results['ids'][0] if results['ids'] else 'None'}")
                
                # Show first memory content preview
                if results['documents']:
                    preview = results['documents'][0][:100] + "..." if len(results['documents'][0]) > 100 else results['documents'][0]
                    print(f"  First memory preview: {preview}")
                
            except Exception as e:
                print(f"Error loading {collection_name}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Collection {collection_name} is None")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_memory_loading()