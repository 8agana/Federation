#!/usr/bin/env python3
"""
Federation RAG V2 - Command Line Interface
Simple CLI for testing RAG without GUI issues
"""

import os
import sys
import json
from datetime import datetime

# Set GROQ API key
os.environ['GROQ_API_KEY'] = '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'

# Add Federation RAG to path
sys.path.append('/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag')

from cc_federation_rag_v2 import CCFederationRAGv2

def print_banner():
    print("\n" + "="*60)
    print("🚀 Federation RAG V2 - CLI Interface")
    print("="*60)
    print("\nAvailable tools:")
    print("  1. query_auto   - Smart auto-routing (default)")
    print("  2. query_daily  - Fast daily driver")
    print("  3. query_history - Timeline explorer")
    print("  4. query_files  - Code hunter")
    print("  5. query_full   - Deep research")
    print("\nCommands:")
    print("  /tool <name>  - Switch tool (e.g., /tool query_files)")
    print("  /exit         - Exit the CLI")
    print("  /help         - Show this help")
    print("\n" + "="*60 + "\n")

def main():
    # Initialize RAG
    print("Initializing RAG...")
    try:
        rag = CCFederationRAGv2()
        print("✓ RAG initialized successfully!")
    except Exception as e:
        print(f"✗ Failed to initialize RAG: {e}")
        return
    
    print_banner()
    
    # Current tool
    current_tool = "query_auto"
    print(f"Current tool: {current_tool}")
    
    while True:
        try:
            # Get query
            query = input("\n🔍 Enter your query (or /command): ").strip()
            
            if not query:
                continue
                
            # Handle commands
            if query.startswith('/'):
                if query == '/exit':
                    print("Goodbye!")
                    break
                elif query == '/help':
                    print_banner()
                elif query.startswith('/tool '):
                    new_tool = query[6:].strip()
                    if hasattr(rag, new_tool):
                        current_tool = new_tool
                        print(f"✓ Switched to {current_tool}")
                    else:
                        print(f"✗ Unknown tool: {new_tool}")
                else:
                    print(f"✗ Unknown command: {query}")
                continue
            
            # Execute query
            print(f"\nSearching with {current_tool}...")
            print("-" * 60)
            
            try:
                # Get the method and call it
                method = getattr(rag, current_tool)
                result = method(query)
                
                # Display results
                print(f"\n✅ Found {result.get('contexts_found', 0)} contexts")
                print(f"Tool used: {result.get('tool_used', current_tool)}")
                print(f"Cache TTL: {result.get('cache_ttl', 'N/A')}")
                
                print("\n📝 Answer:")
                print("-" * 60)
                print(result.get('answer', 'No answer generated'))
                
                # Show sources
                sources = result.get('sources_searched', [])
                if sources:
                    print(f"\n📚 Sources searched ({len(sources)}):")
                    for source in sources:
                        print(f"  • {source}")
                
                # Performance stats
                stats = result.get('retrieval_stats', {})
                if stats:
                    print("\n⚡ Performance:")
                    total_time = 0
                    for source, data in stats.items():
                        if isinstance(data, dict):
                            count = data.get('count', 0)
                            time_ms = data.get('time', 0) * 1000
                            total_time += time_ms
                            print(f"  • {source}: {count} items in {time_ms:.1f}ms")
                    print(f"  • Total: {total_time:.1f}ms")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
                import traceback
                traceback.print_exc()
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()