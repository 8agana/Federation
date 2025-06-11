#!/usr/bin/env python3
"""
CC Federation RAG V2 MCP Server Runner - Specialized Tools Edition
"""
import sys
import os

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run the V2 CC server
        from cc_federation_rag_v2 import mcp
        
        # Log startup info to stderr
        sys.stderr.write("\n🚀 Starting CC Federation RAG V2 MCP Server - Specialized Tools Edition\n")
        sys.stderr.write("\nSpecialized Tools Available:\n")
        sys.stderr.write("  - rag_query: Fast daily driver (memories + knowledge + notes)\n")
        sys.stderr.write("  - rag_query_history: Timeline explorer (+ legacy JSON)\n")
        sys.stderr.write("  - rag_query_files: Code hunter (federation files + docs)\n")
        sys.stderr.write("  - rag_query_full: Deep research (all 6 sources)\n")
        sys.stderr.write("  - rag_auto: Smart auto-routing with cascading\n")
        sys.stderr.write("\nUtility Tools:\n")
        sys.stderr.write("  - rag_sources: List available sources and tools\n")
        sys.stderr.write("  - rag_cache_stats: View cache statistics\n")
        sys.stderr.write("  - rag_clear_cache: Clear query caches\n")
        sys.stderr.write("\nCache TTLs: daily=5min, history=1hr, files=30min, full=15min\n")
        sys.stderr.write("Note: Set GROQ_API_KEY environment variable for LLM synthesis\n")
        
        mcp.run()
        
    except ImportError as e:
        sys.stderr.write(f"❌ Missing dependencies: {e}\n")
        sys.stderr.write("\nPlease install dependencies manually:\n")
        sys.stderr.write("pip install mcp langchain langchain-community chromadb sentence-transformers langchain-groq python-dotenv\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"❌ Failed to start CC V2 server: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)