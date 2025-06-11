#!/usr/bin/env python3
"""
Portable MCP server runner for DT Federation Memory
Works across Python versions and handles package installation
"""
import sys
import subprocess
import os

# List of required packages
REQUIRED_PACKAGES = ["chromadb", "mcp"]

# Check and install missing packages
for package in REQUIRED_PACKAGES:
    try:
        __import__(package)
    except ImportError:
        print(f"{package} not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", package])
        except:
            print(f"Warning: Could not install {package}, hoping it's available in environment")

# Now run the actual server
if __name__ == "__main__":
    # Add bridge scripts to Python path
    bridge_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "2_BridgeScripts"))
    sys.path.insert(0, bridge_path)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the server
    import asyncio
    from dt_memory_mcp import main
    asyncio.run(main())