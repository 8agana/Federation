#!/usr/bin/env python3
"""
Debug script for DT retrievers
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dt_federation_rag import rag

def test_queries():
    """Test the specific queries from DT's testing"""
    test_queries = [
        "trips",
        "inside jokes", 
        "federation rag",
        "semantic notes",
        "CCC",
        "decision tree"
    ]
    
    print("=== DT RETRIEVER DEBUG TEST ===\n")
    
    for query in test_queries:
        print(f"🔍 Testing query: '{query}'")
        print("=" * 50)
        
        # Test each retriever individually
        for source_name, retriever in rag.retrievers.items():
            print(f"\n📁 {source_name}:")
            try:
                results = retriever.retrieve(query, k=3)
                print(f"   Found {len(results)} results")
                for i, result in enumerate(results):
                    print(f"   {i+1}. {result['content'][:100]}...")
            except Exception as e:
                print(f"   ERROR: {e}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    test_queries()