#!/usr/bin/env python3
"""
Test DT Federation RAG Federated Query
Debug why federated queries fail when individual retrievers work
"""

import os
import sys
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("federated_test")

def test_federated_query():
    """Test the federated query specifically"""
    print("=" * 60)
    print("FEDERATED QUERY DEBUG TEST")
    print("=" * 60)
    
    try:
        from dt_federation_rag import DTFederationRAG
        
        print("Initializing DT Federation RAG...")
        rag = DTFederationRAG()
        
        print(f"Available retrievers: {list(rag.retrievers.keys())}")
        
        # Test the exact query that DT used
        test_query = "What are my core memories and identity?"
        print(f"\nTesting federated query: '{test_query}'")
        
        # First test individual retrievers to confirm they work
        print("\n" + "-" * 40)
        print("INDIVIDUAL RETRIEVER TESTING")
        print("-" * 40)
        
        for source_name, retriever in rag.retrievers.items():
            print(f"\nTesting {source_name} individually...")
            try:
                results = retriever.retrieve(test_query, k=5)
                print(f"  Results: {len(results)}")
                if results:
                    print(f"  Sample: {results[0]['content'][:100]}...")
            except Exception as e:
                print(f"  Error: {e}")
                import traceback
                traceback.print_exc()
        
        # Now test federated query
        print("\n" + "-" * 40)
        print("FEDERATED QUERY TESTING")
        print("-" * 40)
        
        result = rag.federated_query(test_query)
        
        print(f"Query: {test_query}")
        print(f"Sources searched: {result['sources_searched']}")
        print(f"Total contexts found: {result['contexts_found']}")
        print(f"Retrieval stats: {result['retrieval_stats']}")
        
        # Check if there are any errors in retrieval stats
        for source, stats in result['retrieval_stats'].items():
            if 'error' in stats:
                print(f"ERROR in {source}: {stats['error']}")
            else:
                print(f"{source}: {stats['count']} results in {stats['time']:.4f}s")
        
        if result['contexts_found'] > 0:
            print(f"\nFirst context preview:")
            print(f"  {result.get('source_metadata', [{}])[0]}")
        
    except Exception as e:
        print(f"Error in federated query test: {e}")
        import traceback
        traceback.print_exc()

def test_specific_source_issue():
    """Test the specific sources that are failing"""
    print("\n" + "=" * 60)
    print("SPECIFIC SOURCE FAILURE ANALYSIS")
    print("=" * 60)
    
    try:
        from dt_federation_rag import DTFederationRAG
        
        rag = DTFederationRAG()
        
        # Test specific sources that DT reported as failing
        failing_sources = ['dt_knowledge_graph', 'dt_obsidian_notes']
        test_query = "identity"
        
        for source in failing_sources:
            print(f"\n{'-' * 30}")
            print(f"TESTING {source.upper()}")
            print(f"{'-' * 30}")
            
            if source in rag.retrievers:
                retriever = rag.retrievers[source]
                
                # Test direct retrieval
                print("Direct retrieval test:")
                try:
                    direct_results = retriever.retrieve(test_query, k=3)
                    print(f"  Direct results: {len(direct_results)}")
                    for i, result in enumerate(direct_results):
                        print(f"    {i+1}. {result['source']} - {result['content'][:80]}...")
                except Exception as e:
                    print(f"  Direct retrieval error: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Test through federation with just this source
                print(f"\nFederated retrieval test (single source):")
                try:
                    fed_result = rag.federated_query(test_query, sources=[source])
                    print(f"  Federated results: {fed_result['contexts_found']}")
                    print(f"  Retrieval stats: {fed_result['retrieval_stats']}")
                    
                    if source in fed_result['retrieval_stats']:
                        stats = fed_result['retrieval_stats'][source]
                        if 'error' in stats:
                            print(f"  ERROR: {stats['error']}")
                        else:
                            print(f"  Success: {stats['count']} results")
                    
                except Exception as e:
                    print(f"  Federated retrieval error: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"  Source {source} not found in retrievers!")
    
    except Exception as e:
        print(f"Error in specific source test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("DT Federation RAG Federated Query Debug")
    print("Investigating why federation fails when individual retrievers work")
    print("\n")
    
    test_federated_query()
    test_specific_source_issue()
    
    print("\n" + "=" * 60)
    print("FEDERATED QUERY DEBUG COMPLETE")
    print("=" * 60)