#!/usr/bin/env python3
"""Test script to diagnose browser issues"""

import os
import sys

print("=== Testing ChromaDB Browser Issues ===\n")

# Test 1: ChromaDB connection
print("1. Testing ChromaDB connection...")
try:
    import chromadb
    client = chromadb.PersistentClient(
        path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
    )
    collections = client.list_collections()
    print(f"✓ Found {len(collections)} collections")
    for col in collections:
        print(f"  - {col.name}: {col.count()} items")
except Exception as e:
    print(f"✗ ChromaDB error: {e}")

print("\n2. Testing memory loading...")
try:
    # Test CC memories
    cc_collection = client.get_collection("memories")
    cc_memories = cc_collection.get()
    print(f"✓ Loaded {len(cc_memories['ids'])} CC memories")
except Exception as e:
    print(f"✗ CC memory error: {e}")

try:
    # Test DT memories
    dt_client = chromadb.PersistentClient(
        path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation"
    )
    dt_collection = dt_client.get_collection("memories")
    dt_memories = dt_collection.get()
    print(f"✓ Loaded {len(dt_memories['ids'])} DT memories")
except Exception as e:
    print(f"✗ DT memory error: {e}")

print("\n3. Testing RAG V2 import...")
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag')

# Set GROQ key
os.environ['GROQ_API_KEY'] = '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'

try:
    from cc_federation_rag_v2 import CCFederationRAGv2
    print("✓ Import successful")
    
    print("\n4. Testing RAG V2 initialization...")
    rag = CCFederationRAGv2()
    print("✓ RAG V2 initialized")
    
    print("\n5. Testing RAG query...")
    result = rag.rag_query({"query": "test"})
    print(f"✓ Query returned {result.get('contexts_found', 0)} contexts")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")