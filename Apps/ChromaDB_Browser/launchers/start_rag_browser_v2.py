#!/usr/bin/env python3
"""
Start the ChromaDB Browser with Federation RAG V2
"""

import os
import sys
import subprocess
import time
import socket

def check_port(port):
    """Check if a port is in use"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def start_rag_server():
    """Start the RAG V2 server if not running"""
    if check_port(5100):
        print("✓ RAG V2 server is already running on port 5100")
        return True
    
    print("Starting RAG V2 server...")
    server_path = "/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag"
    
    # Start server in background
    process = subprocess.Popen(
        [sys.executable, "run_cc_server_v2.py"],
        cwd=server_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    for i in range(10):
        time.sleep(1)
        if check_port(5100):
            print("✓ RAG V2 server started successfully")
            return True
    
    print("✗ Failed to start RAG V2 server")
    return False

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Start ChromaDB Browser with RAG V2')
    parser.add_argument('--no-server', action='store_true', help='Skip starting the RAG server')
    args = parser.parse_args()
    
    print("🚀 Starting ChromaDB Browser with Federation RAG V2")
    print("=" * 50)
    
    # Check GROQ API key
    if not os.getenv('GROQ_API_KEY'):
        print("\n⚠️  Warning: GROQ_API_KEY not set. LLM synthesis will be unavailable.")
        print("To enable LLM synthesis, set your GROQ API key:")
        print("  export GROQ_API_KEY='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'")
        print()
    
    # Ensure RAG server is running (unless --no-server flag is used)
    if not args.no_server:
        if not start_rag_server():
            print("\nPlease start the RAG server manually:")
            print("  cd /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/federation_rag")
            print("  python3 run_cc_server_v2.py")
            sys.exit(1)
    else:
        print("\nSkipping server check (--no-server flag used)")
    
    # Change to browser directory
    browser_path = "/Users/samuelatagana/Documents/Federation/Apps/ChromaDB_Browser/src"
    os.chdir(browser_path)
    
    # Add src directory to Python path
    sys.path.insert(0, browser_path)
    
    print("\nStarting ChromaDB Browser...")
    print("\nRAG V2 Features:")
    print("  • 🚀 rag_query - Fast daily driver")
    print("  • 📜 rag_query_history - Timeline explorer")
    print("  • 🔍 rag_query_files - Code hunter")
    print("  • 🧠 rag_query_full - Deep research")
    print("  • 🤖 rag_auto - Smart auto-routing")
    print()
    
    # Import and run the browser
    try:
        from chromadb_rag_browser_v2 import main as run_browser
        run_browser()
    except Exception as e:
        print(f"\n✗ Error starting browser: {e}")
        print("\nTrying alternative import method...")
        
        # Alternative: run as subprocess
        subprocess.run([sys.executable, "chromadb_rag_browser_v2.py"], cwd=browser_path)

if __name__ == "__main__":
    main()