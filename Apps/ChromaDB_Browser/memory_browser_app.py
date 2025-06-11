#!/usr/bin/env python3
"""
ChromaDB Memory Browser - Standalone
Just the memory browser without RAG features
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the v5 browser directly
from tkinter_memory_browser_v5_bigger import MemoryBrowserV5
import tkinter as tk

def main():
    print("🧠 Starting ChromaDB Memory Browser")
    print("=" * 50)
    print("Loading CC and DT memories...")
    print()
    
    root = tk.Tk()
    app = MemoryBrowserV5(root)
    root.mainloop()

if __name__ == "__main__":
    main()