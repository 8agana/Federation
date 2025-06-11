#!/usr/bin/env python3
"""Test if MCP servers can start properly"""

import subprocess
import sys
import os

# Test CC MCP
print("Testing CC Federation Memory MCP...")
env = os.environ.copy()
env['PYTHONPATH'] = '/Users/samuelatagana/Documents/Federation/System/Memory/2_BridgeScripts'
env['PYTHONUNBUFFERED'] = '1'

try:
    # Start the process
    proc = subprocess.Popen(
        [sys.executable, '/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/core/cc_memory_mcp.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Try to read some output
    import time
    time.sleep(2)
    
    # Check if process is still running
    if proc.poll() is None:
        print("✅ CC MCP started successfully!")
        proc.terminate()
    else:
        stdout, stderr = proc.communicate()
        print("❌ CC MCP failed to start")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTesting DT Federation Memory MCP...")
try:
    # Start the process
    proc = subprocess.Popen(
        [sys.executable, '/Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/core/dt_memory_mcp.py'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Try to read some output
    time.sleep(2)
    
    # Check if process is still running
    if proc.poll() is None:
        print("✅ DT MCP started successfully!")
        proc.terminate()
    else:
        stdout, stderr = proc.communicate()
        print("❌ DT MCP failed to start")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        
except Exception as e:
    print(f"❌ Error: {e}")