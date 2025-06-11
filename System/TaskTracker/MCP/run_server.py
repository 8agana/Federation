#!/usr/bin/env python3
"""
Portable MCP server runner for SharedVault
Works across Python versions and handles package installation
"""
import sys
import subprocess
import os

# List of required packages
REQUIRED_PACKAGES = ["mcp"]

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
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the server
    import asyncio
    from tasktracker_mcp import main
    asyncio.run(main())