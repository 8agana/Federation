#!/usr/bin/env python3
"""
ChromaDB Memory Browser Launcher
Starts the browser with RAG V2 Direct integration
"""

import os
import sys

# Set GROQ API key
os.environ['GROQ_API_KEY'] = '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'

# Add src to path and run the direct version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("🚀 Starting ChromaDB Memory Browser with RAG V2")
print("=" * 50)
print("\nThis version uses direct RAG integration (no server needed)")
print("\nFeatures:")
print("  • Regular memory browsing (770 CC + 565 DT memories)")
print("  • RAG V2 Search tab with all 5 specialized tools")
print("  • Direct integration - no MCP server required")
print()

from chromadb_rag_browser_v2_direct import main
main()