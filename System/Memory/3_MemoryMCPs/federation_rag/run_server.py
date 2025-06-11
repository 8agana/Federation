#!/usr/bin/env python3
"""
Federation RAG MCP Server Runner
"""
import sys
import os

if __name__ == "__main__":
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Try to import and run the server directly
        from federation_rag_mcp import mcp
        
        # Log startup info to stderr
        sys.stderr.write("\n🚀 Starting Federation RAG MCP Server...\n")
        sys.stderr.write("Available tools:\n")
        sys.stderr.write("  - rag_query: Query across federated sources\n")
        sys.stderr.write("  - rag_sources: List available sources\n")
        sys.stderr.write("  - rag_clear_cache: Clear query cache\n")
        sys.stderr.write("  - rag_test: Test system functionality\n")
        sys.stderr.write("\nNote: Set GROQ_API_KEY environment variable for LLM features\n")
        
        mcp.run()
        
    except ImportError as e:
        sys.stderr.write(f"❌ Missing dependencies: {e}\n")
        sys.stderr.write("\nPlease install dependencies manually:\n")
        sys.stderr.write("pip install mcp langchain langchain-community chromadb sentence-transformers langchain-groq python-dotenv\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"❌ Failed to start server: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)