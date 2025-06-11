#!/usr/bin/env python3
"""
Simple Memory Viewer - Lightweight CLI interface
No complex GUI, just browse memories efficiently
"""

import chromadb
import json
from datetime import datetime
import textwrap

class SimpleMemoryViewer:
    def __init__(self):
        base_path = "/Users/samuelatagana/Documents/Federation/System/Memory/1_ChromaDBs"
        
        # Load collections
        self.collections = {}
        try:
            cc_client = chromadb.PersistentClient(path=f"{base_path}/cc-federation")
            self.collections['cc'] = cc_client.get_collection("cc_memories")
            print(f"✓ Loaded CC: {self.collections['cc'].count()} memories")
        except Exception as e:
            print(f"✗ CC Error: {e}")
            
        try:
            dt_client = chromadb.PersistentClient(path=f"{base_path}/dt-federation")
            self.collections['dt'] = dt_client.get_collection("dt_memories")
            print(f"✓ Loaded DT: {self.collections['dt'].count()} memories")
        except Exception as e:
            print(f"✗ DT Error: {e}")
    
    def search(self, query, collection='all', limit=10):
        """Search memories across collections"""
        results = []
        
        collections_to_search = []
        if collection == 'all':
            collections_to_search = list(self.collections.items())
        elif collection in self.collections:
            collections_to_search = [(collection, self.collections[collection])]
        
        for name, coll in collections_to_search:
            if coll:
                try:
                    res = coll.query(
                        query_texts=[query],
                        n_results=limit
                    )
                    
                    for i in range(len(res['ids'][0])):
                        results.append({
                            'id': res['ids'][0][i],
                            'content': res['documents'][0][i],
                            'metadata': res['metadatas'][0][i],
                            'distance': res['distances'][0][i] if res['distances'] else None,
                            'collection': name
                        })
                except Exception as e:
                    print(f"Error searching {name}: {e}")
        
        # Sort by relevance
        results.sort(key=lambda x: x.get('distance', 999))
        return results
    
    def browse(self, collection='cc', offset=0, limit=20):
        """Browse memories with pagination"""
        if collection not in self.collections:
            return []
            
        coll = self.collections[collection]
        if not coll:
            return []
            
        try:
            # Get all IDs first
            all_results = coll.get(limit=1000)
            total = len(all_results['ids'])
            
            # Return paginated slice
            results = []
            for i in range(offset, min(offset + limit, total)):
                results.append({
                    'id': all_results['ids'][i],
                    'content': all_results['documents'][i],
                    'metadata': all_results['metadatas'][i],
                    'collection': collection
                })
            
            return results, total
        except Exception as e:
            print(f"Error browsing: {e}")
            return [], 0
    
    def display_memory(self, memory):
        """Display a single memory nicely"""
        print("\n" + "="*80)
        print(f"ID: {memory['id']}")
        print(f"Collection: {memory['collection'].upper()}")
        
        metadata = memory.get('metadata', {})
        if metadata:
            print(f"Title: {metadata.get('title', 'No title')}")
            print(f"Created: {metadata.get('created_at', 'Unknown')}")
            print(f"Tags: {metadata.get('tags', 'No tags')}")
            
            # V5 metadata
            if 'priority' in metadata:
                print(f"Priority: {metadata['priority']}")
            if 'domain' in metadata:
                print(f"Domain: {metadata['domain']}")
        
        print("\nContent:")
        print("-"*80)
        # Wrap long content
        wrapped = textwrap.fill(memory['content'], width=78)
        print(wrapped)
        print("="*80)

def main():
    viewer = SimpleMemoryViewer()
    
    print("\n" + "="*60)
    print("🧠 Federation Memory Viewer - Simple CLI")
    print("="*60)
    
    print("\nCommands:")
    print("  search <query>     - Search memories")
    print("  browse [cc/dt]     - Browse memories (default: cc)")
    print("  show <id>          - Show specific memory by ID")
    print("  stats              - Show collection statistics")
    print("  help               - Show this help")
    print("  exit               - Exit viewer")
    print()
    
    # Current browse state
    current_collection = 'cc'
    current_offset = 0
    page_size = 10
    
    while True:
        try:
            cmd = input("\n> ").strip()
            
            if not cmd:
                continue
                
            parts = cmd.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command == 'exit':
                break
                
            elif command == 'help':
                print("\nCommands:")
                print("  search <query>     - Search across all memories")
                print("  browse [cc/dt]     - Browse collection (use n/p for next/prev)")
                print("  show <id>          - Show specific memory")
                print("  stats              - Show statistics")
                print("  n                  - Next page")
                print("  p                  - Previous page")
                
            elif command == 'stats':
                print("\nMemory Statistics:")
                for name, coll in viewer.collections.items():
                    if coll:
                        print(f"  {name.upper()}: {coll.count()} memories")
                        
            elif command == 'search':
                if not args:
                    print("Usage: search <query>")
                    continue
                    
                print(f"\nSearching for: '{args}'...")
                results = viewer.search(args, limit=10)
                
                if results:
                    print(f"\nFound {len(results)} results:")
                    for i, res in enumerate(results):
                        title = res['metadata'].get('title', res['id'])
                        preview = res['content'][:100] + "..." if len(res['content']) > 100 else res['content']
                        print(f"\n{i+1}. [{res['collection'].upper()}] {title}")
                        print(f"   {preview}")
                    
                    # Allow viewing
                    choice = input("\nEnter number to view (or press Enter to continue): ").strip()
                    if choice.isdigit() and 1 <= int(choice) <= len(results):
                        viewer.display_memory(results[int(choice)-1])
                else:
                    print("No results found.")
                    
            elif command == 'browse':
                if args and args in ['cc', 'dt']:
                    current_collection = args
                    current_offset = 0
                
                results, total = viewer.browse(current_collection, current_offset, page_size)
                
                if results:
                    print(f"\nBrowsing {current_collection.upper()} memories ({current_offset+1}-{current_offset+len(results)} of {total}):")
                    for i, res in enumerate(results):
                        title = res['metadata'].get('title', res['id'])
                        print(f"{current_offset+i+1}. {title}")
                    
                    print(f"\nPage {current_offset//page_size + 1} of {(total-1)//page_size + 1}")
                    print("Commands: (n)ext, (p)revious, or enter number to view")
                else:
                    print("No memories found.")
                    
            elif command == 'n':
                # Next page
                results, total = viewer.browse(current_collection, current_offset, page_size)
                if current_offset + page_size < total:
                    current_offset += page_size
                    cmd = f"browse {current_collection}"
                    continue
                else:
                    print("Already at last page")
                    
            elif command == 'p':
                # Previous page
                if current_offset > 0:
                    current_offset = max(0, current_offset - page_size)
                    cmd = f"browse {current_collection}"
                    continue
                else:
                    print("Already at first page")
                    
            elif command == 'show':
                if not args:
                    print("Usage: show <memory_id>")
                    continue
                    
                # Find memory by ID
                found = False
                for name, coll in viewer.collections.items():
                    if coll:
                        try:
                            result = coll.get(ids=[args])
                            if result['ids']:
                                memory = {
                                    'id': result['ids'][0],
                                    'content': result['documents'][0],
                                    'metadata': result['metadatas'][0],
                                    'collection': name
                                }
                                viewer.display_memory(memory)
                                found = True
                                break
                        except:
                            pass
                
                if not found:
                    print(f"Memory '{args}' not found")
                    
            elif command.isdigit():
                # View memory by number from last browse
                num = int(command)
                results, total = viewer.browse(current_collection, current_offset, page_size)
                idx = num - current_offset - 1
                if 0 <= idx < len(results):
                    viewer.display_memory(results[idx])
                else:
                    print("Invalid number")
                    
            else:
                print(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()