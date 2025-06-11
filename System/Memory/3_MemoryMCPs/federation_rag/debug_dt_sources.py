#!/usr/bin/env python3
"""
Debug DT Federation RAG Sources
Investigate why Knowledge Graph and Obsidian retrievers return 0 results
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("dt_debug")

def debug_path_access():
    """Debug file path accessibility"""
    print("=" * 60)
    print("PATH ACCESS DEBUGGING")
    print("=" * 60)
    
    paths_to_check = [
        "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center",
        "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
        "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation",
        "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
    ]
    
    for path in paths_to_check:
        exists = os.path.exists(path)
        readable = os.access(path, os.R_OK) if exists else False
        
        print(f"\nPath: {path}")
        print(f"  Exists: {exists}")
        print(f"  Readable: {readable}")
        
        if exists and readable:
            try:
                items = os.listdir(path)
                print(f"  Items: {len(items)} files/folders")
                if len(items) <= 10:
                    for item in items[:5]:
                        print(f"    - {item}")
                    if len(items) > 5:
                        print(f"    ... and {len(items) - 5} more")
                else:
                    print(f"    (showing first 5 of {len(items)})")
                    for item in items[:5]:
                        print(f"    - {item}")
            except Exception as e:
                print(f"  Error listing contents: {e}")


def debug_knowledge_graph():
    """Debug Knowledge Graph retriever"""
    print("\n" + "=" * 60)
    print("KNOWLEDGE GRAPH DEBUGGING")
    print("=" * 60)
    
    try:
        from dt_federation_rag import KnowledgeGraphRetriever
        
        dt_nerve_path = "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        
        print(f"Initializing Knowledge Graph with path: {dt_nerve_path}")
        kg = KnowledgeGraphRetriever(dt_nerve_path)
        
        print(f"Entities found: {len(kg.entities)}")
        print(f"Relations found: {len(kg.relations)}")
        print(f"Observations found: {len(kg.observations)}")
        
        if len(kg.entities) > 0:
            print("\nSample entities:")
            for i, (entity, data) in enumerate(kg.entities.items()):
                if i >= 3:
                    break
                print(f"  - {entity} (type: {data.get('type', 'unknown')})")
        
        if len(kg.relations) > 0:
            print("\nSample relations:")
            for i, (rel_key, data) in enumerate(kg.relations.items()):
                if i >= 3:
                    break
                print(f"  - {rel_key}")
        
        if len(kg.observations) > 0:
            print("\nSample observations:")
            for i, (obs_key, data) in enumerate(kg.observations.items()):
                if i >= 3:
                    break
                print(f"  - [{data.get('category', 'unknown')}] {data['content'][:100]}...")
        
        # Test retrieval
        print("\n" + "-" * 40)
        print("TESTING KNOWLEDGE GRAPH RETRIEVAL")
        print("-" * 40)
        
        test_queries = ["memory", "identity", "trips", "federation"]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = kg.retrieve(query, k=3)
            print(f"  Results: {len(results)}")
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['source']} - {result['content'][:100]}...")
        
    except Exception as e:
        print(f"Error debugging Knowledge Graph: {e}")
        import traceback
        traceback.print_exc()


def debug_obsidian_notes():
    """Debug Obsidian notes retriever"""
    print("\n" + "=" * 60)
    print("OBSIDIAN NOTES DEBUGGING")
    print("=" * 60)
    
    try:
        from dt_federation_rag import ObsidianRetriever
        
        vault_paths = [
            "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault",
            "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/DT_Nerve_Center"
        ]
        
        print(f"Initializing Obsidian retriever with paths:")
        for path in vault_paths:
            print(f"  - {path}")
        
        obsidian = ObsidianRetriever(vault_paths)
        
        print(f"Notes loaded: {len(obsidian.notes)}")
        
        if len(obsidian.notes) > 0:
            print("\nSample notes:")
            for i, (filepath, note_data) in enumerate(obsidian.notes.items()):
                if i >= 5:
                    break
                print(f"  - {note_data['title']} ({note_data['vault']})")
                print(f"    Path: {filepath}")
                print(f"    Modified: {note_data['modified']}")
        
        # Test retrieval
        print("\n" + "-" * 40)
        print("TESTING OBSIDIAN NOTES RETRIEVAL")
        print("-" * 40)
        
        test_queries = ["memory", "identity", "trips", "federation", "rag"]
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = obsidian.retrieve(query, k=3)
            print(f"  Results: {len(results)}")
            for i, result in enumerate(results):
                print(f"    {i+1}. {result['source']} - {result['metadata']['title']}")
                print(f"        Score: {result['metadata']['score']}")
        
    except Exception as e:
        print(f"Error debugging Obsidian notes: {e}")
        import traceback
        traceback.print_exc()


def debug_chromadb():
    """Debug ChromaDB retrievers for comparison"""
    print("\n" + "=" * 60)
    print("CHROMADB DEBUGGING (FOR COMPARISON)")
    print("=" * 60)
    
    try:
        from dt_federation_rag import ChromaDBRetriever
        
        # Test DT memories
        print("Testing DT memories...")
        dt_chroma = ChromaDBRetriever(
            collection_name="dt_memories",
            chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/dt-federation"
        )
        
        results = dt_chroma.retrieve("identity", k=2)
        print(f"DT memories results: {len(results)}")
        
        # Test CC memories
        print("\nTesting CC memories...")
        cc_chroma = ChromaDBRetriever(
            collection_name="cc_memories", 
            chroma_path="/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"
        )
        
        results = cc_chroma.retrieve("identity", k=2)
        print(f"CC memories results: {len(results)}")
        
    except Exception as e:
        print(f"Error debugging ChromaDB: {e}")
        import traceback
        traceback.print_exc()


def debug_full_system():
    """Debug the full DT system"""
    print("\n" + "=" * 60)
    print("FULL DT SYSTEM DEBUGGING")
    print("=" * 60)
    
    try:
        from dt_federation_rag import DTFederationRAG
        
        print("Initializing DT Federation RAG system...")
        rag = DTFederationRAG()
        
        print(f"Available retrievers: {list(rag.retrievers.keys())}")
        
        # Test each retriever individually
        for source_name, retriever in rag.retrievers.items():
            print(f"\nTesting {source_name} directly...")
            try:
                results = retriever.retrieve("identity", k=2)
                print(f"  Results: {len(results)}")
                if results:
                    print(f"  Sample: {results[0]['content'][:100]}...")
            except Exception as e:
                print(f"  Error: {e}")
        
        # Test federated query
        print("\n" + "-" * 40)
        print("TESTING FEDERATED QUERY")
        print("-" * 40)
        
        result = rag.federated_query("What are my core memories and identity?")
        print(f"Sources searched: {result['sources_searched']}")
        print(f"Contexts found: {result['contexts_found']}")
        print(f"Retrieval stats: {result['retrieval_stats']}")
        
    except Exception as e:
        print(f"Error debugging full system: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("DT Federation RAG Sources Debug Script")
    print("Testing why Knowledge Graph and Obsidian retrievers return 0 results")
    print("\n")
    
    # Run all debug functions
    debug_path_access()
    debug_chromadb()
    debug_knowledge_graph()
    debug_obsidian_notes()
    debug_full_system()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)