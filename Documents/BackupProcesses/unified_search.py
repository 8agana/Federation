#!/usr/bin/env python3
"""
Unified Search - Search both ChromaDB memories and Obsidian notes
Author: CCD
Created: 2025-06-09
"""

import sys
import subprocess
from pathlib import Path

def search_all(query):
    """Search both memories and notes"""
    print(f"\n🔍 Searching for '{query}' across all systems...\n")
    
    # Search ChromaDB
    print("=" * 60)
    print("📚 CHROMADB MEMORIES")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "chromadb_emergency.py", "search", query],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(result.stdout)
        if result.stderr:
            print(f"Errors: {result.stderr}")
    except Exception as e:
        print(f"❌ Failed to search memories: {e}")
    
    # Search Nerve Center
    print("\n" + "=" * 60)
    print("🧠 NERVE CENTER NOTES")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "obsidian_emergency.py", "--vault", "nerve", "search", query],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ Failed to search Nerve Center: {e}")
    
    # Search SharedVault
    print("\n" + "=" * 60)
    print("📁 SHARED VAULT NOTES")
    print("=" * 60)
    try:
        result = subprocess.run(
            [sys.executable, "obsidian_emergency.py", "--vault", "shared", "search", query],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(result.stdout)
    except Exception as e:
        print(f"❌ Failed to search SharedVault: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 unified_search.py <query>")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    search_all(query)