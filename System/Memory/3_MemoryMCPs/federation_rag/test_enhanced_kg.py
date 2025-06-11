#!/usr/bin/env python3
"""
Test Enhanced Knowledge Graph Query Processing
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_knowledge_graph():
    """Test the enhanced knowledge graph with complex queries"""
    print("Testing Enhanced Knowledge Graph Query Processing")
    print("=" * 60)
    
    try:
        from dt_federation_rag import KnowledgeGraphRetriever
        
        # Initialize Knowledge Graph
        dt_nerve_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        kg = KnowledgeGraphRetriever(dt_nerve_path)
        
        print(f"Knowledge Graph loaded: {len(kg.entities)} entities, {len(kg.relations)} relations, {len(kg.observations)} observations")
        
        # Test queries that were failing before
        test_queries = [
            "What are my core memories and identity?",
            "I'm a new DT instance starting a conversation with Sam. What's the current context?",
            "Tell me about recent projects and collaboration",
            "What have I learned about partnership and relationships?",
            "What are the key developments in our federation system?"
        ]
        
        for query in test_queries:
            print(f"\n{'-' * 50}")
            print(f"Query: {query}")
            print(f"{'-' * 50}")
            
            results = kg.retrieve(query, k=3)
            print(f"Results: {len(results)}")
            
            for i, result in enumerate(results):
                print(f"\n{i+1}. {result['metadata']['type'].upper()}")
                print(f"   Score: {result['metadata'].get('match_score', 0)}")
                print(f"   Terms: {result['metadata'].get('matched_terms', [])}")
                print(f"   Content: {result['content'][:150]}...")
        
    except Exception as e:
        print(f"Error testing enhanced Knowledge Graph: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_knowledge_graph()
    print("\n" + "=" * 60)
    print("Enhanced Knowledge Graph Test Complete")