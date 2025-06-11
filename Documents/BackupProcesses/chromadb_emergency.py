#!/usr/bin/env python3
"""
ChromaDB Emergency Access Script
Direct access to memories when MCP is down
Author: CCD
Created: 2025-06-09
"""

import chromadb
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# ChromaDB path
CHROMADB_PATH = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs/cc-federation"

def get_collection():
    """Connect to ChromaDB and get collection"""
    try:
        client = chromadb.PersistentClient(path=CHROMADB_PATH)
        return client.get_collection("cc_memories")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        sys.exit(1)

def search_memories(query, n_results=10):
    """Search memories by content"""
    collection = get_collection()
    
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        print(f"\n📚 Found {len(results['ids'][0])} memories for '{query}':\n")
        
        for i, (id, doc, meta, dist) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"{i+1}. Memory ID: {id}")
            print(f"   Created: {meta.get('timestamp', 'Unknown')}")
            print(f"   Tags: {meta.get('tags', 'None')}")
            print(f"   Relevance: {1 - dist:.2%}")
            print(f"   Content: {doc[:200]}...")
            print()
            
    except Exception as e:
        print(f"❌ Search failed: {e}")

def get_recent_memories(hours=24):
    """Get memories from last N hours"""
    collection = get_collection()
    
    cutoff = datetime.now() - timedelta(hours=hours)
    cutoff_str = cutoff.isoformat()
    
    try:
        results = collection.query(
            query_texts=[""],  # Empty query for all
            where={"timestamp": {"$gte": cutoff_str}},
            n_results=100
        )
        
        print(f"\n📚 Recent memories (last {hours} hours):\n")
        
        for i, (id, doc, meta) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['metadatas'][0]
        )):
            print(f"{i+1}. {meta.get('timestamp', 'Unknown')}")
            print(f"   Tags: {meta.get('tags', 'None')}")
            print(f"   Content: {doc[:200]}...")
            print()
            
    except Exception as e:
        print(f"❌ Failed to get recent memories: {e}")def search_by_tags(tags):
    """Search memories by tags"""
    collection = get_collection()
    
    if isinstance(tags, str):
        tags = [tags]
    
    try:
        # ChromaDB doesn't support OR in where clause, so we search each tag
        all_results = []
        seen_ids = set()
        
        for tag in tags:
            results = collection.query(
                query_texts=[""],
                where={"tags": {"$contains": tag}},
                n_results=50
            )
            
            for id, doc, meta in zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0]
            ):
                if id not in seen_ids:
                    seen_ids.add(id)
                    all_results.append((id, doc, meta))
        
        print(f"\n📚 Found {len(all_results)} memories with tags {tags}:\n")
        
        for i, (id, doc, meta) in enumerate(all_results):
            print(f"{i+1}. Memory ID: {id}")
            print(f"   Created: {meta.get('timestamp', 'Unknown')}")
            print(f"   Tags: {meta.get('tags', 'None')}")
            print(f"   Content: {doc[:200]}...")
            print()
            
    except Exception as e:
        print(f"❌ Tag search failed: {e}")

def export_memories(output_file="memories_backup.json"):
    """Export all memories to JSON"""
    collection = get_collection()
    
    try:
        # Get all memories
        results = collection.get()
        
        memories = []
        for id, doc, meta in zip(
            results['ids'],
            results['documents'],
            results['metadatas']
        ):
            memories.append({
                'id': id,
                'content': doc,
                'metadata': meta
            })
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(memories, f, indent=2)
        
        print(f"✅ Exported {len(memories)} memories to {output_file}")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="ChromaDB Emergency Access")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search memories')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-n', '--number', type=int, default=10, help='Number of results')
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Get recent memories')
    recent_parser.add_argument('hours', type=int, default=24, help='Hours to look back')
    
    # Tags command
    tags_parser = subparsers.add_parser('tags', help='Search by tags')
    tags_parser.add_argument('tags', nargs='+', help='Tags to search')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export all memories')
    export_parser.add_argument('output', nargs='?', default='memories_backup.json', help='Output file')
    
    args = parser.parse_args()
    
    if args.command == 'search':
        search_memories(args.query, args.number)
    elif args.command == 'recent':
        get_recent_memories(args.hours)
    elif args.command == 'tags':
        search_by_tags(args.tags)
    elif args.command == 'export':
        export_memories(args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()