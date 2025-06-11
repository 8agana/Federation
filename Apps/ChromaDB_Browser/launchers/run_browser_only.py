#!/usr/bin/env python3
"""
Run ChromaDB Browser V2 (assumes RAG server is already running)
"""

import os
import sys

# Set GROQ API key if provided
GROQ_KEY = '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'
if GROQ_KEY and not os.getenv('GROQ_API_KEY'):
    os.environ['GROQ_API_KEY'] = GROQ_KEY
    print("✓ GROQ API key set")

# Change to browser directory
browser_path = "/Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/src"
os.chdir(browser_path)

# Add to path
sys.path.insert(0, browser_path)

print("🚀 Starting ChromaDB Browser with RAG V2...")
print("=" * 50)
print("\nRAG V2 Features:")
print("  • 🚀 rag_query - Fast daily driver")
print("  • 📜 rag_query_history - Timeline explorer")
print("  • 🔍 rag_query_files - Code hunter")
print("  • 🧠 rag_query_full - Deep research")
print("  • 🤖 rag_auto - Smart auto-routing")
print("\nNote: RAG server should already be running on port 5100")
print()

# Import and run
from chromadb_rag_browser_v2 import MemoryBrowserRAGV2
import tkinter as tk

root = tk.Tk()
app = MemoryBrowserRAGV2(root)
root.mainloop()