#!/usr/bin/env python3
"""
Test RAG Search Functionality
Quick test of the RAG engine without GUI
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from chromadb_rag_browser import RAGSearchEngine
import chromadb
from datetime import datetime

def test_rag_engine():
    """Test the RAG search engine"""
    print("🧪 Testing ChromaDB RAG Search Engine")
    print("=" * 50)
    
    # Initialize RAG engine
    print("\n1. Initializing RAG engine...")
    rag = RAGSearchEngine()
    print(f"   ✅ Embeddings loaded")
    print(f"   {'✅' if rag.llm_available else '⚠️'} LLM {'available' if rag.llm_available else 'not available (set GROQ_API_KEY)'}")
    
    # Test term extraction
    print("\n2. Testing term extraction...")
    test_queries = [
        "What are my core memories about identity and consciousness?",
        "Tell me about recent breakthroughs with Sam",
        "How does the federation RAG system work?",
        "identity",  # Simple term
        '"exact phrase match" and other terms'  # Quoted phrase
    ]
    
    for query in test_queries:
        terms = rag.extract_search_terms(query)
        print(f"\n   Query: {query}")
        print(f"   Terms: {terms}")
    
    # Test with real memories
    print("\n3. Testing with ChromaDB memories...")
    base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
    
    try:
        # Load CC memories
        client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
        collection = client.get_collection("cc_memories")
        
        # Get some memories
        results = collection.get(limit=100, include=['documents', 'metadatas'])
        
        memories = []
        for i in range(len(results['ids'])):
            memories.append({
                'id': results['ids'][i],
                'content': results['documents'][i],
                'metadata': results['metadatas'][i],
                'collection': 'cc'
            })
        
        print(f"   ✅ Loaded {len(memories)} memories from CC collection")
        
        # Test semantic search
        print("\n4. Testing semantic search...")
        test_query = "What defines my identity and relationship with Sam?"
        
        search_results = rag.semantic_search(test_query, memories, k=5)
        
        print(f"\n   Query: {test_query}")
        print(f"   Found: {len(search_results)} relevant memories")
        
        for i, memory in enumerate(search_results[:3]):
            print(f"\n   Result {i+1}:")
            print(f"   Title: {memory['metadata'].get('title', 'Untitled')}")
            print(f"   Domain: {memory['metadata'].get('domain', 'unknown')}")
            print(f"   Preview: {memory['content'][:100]}...")
        
        # Test synthesis (if LLM available)
        if rag.llm_available and search_results:
            print("\n5. Testing LLM synthesis...")
            synthesis = rag.synthesize_results(test_query, search_results)
            print(f"\n   Synthesis preview:")
            print(f"   {synthesis[:300]}...")
        else:
            print("\n5. LLM synthesis not available")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_engine()