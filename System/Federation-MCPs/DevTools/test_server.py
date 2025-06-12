#!/usr/bin/env python3
"""Test DevTools MCP server initialization"""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("Testing imports...")
    from devtools_mcp import server, docker
    print("✓ Main server imported successfully")
    print(f"✓ Docker handler initialized: {docker.__class__.__name__}")
    
    # Try to import GitHub handler but don't fail if token missing
    from devtools_mcp import github
    github_available = github is not None
    
    if github_available:
        print(f"✓ GitHub handler initialized: {github.__class__.__name__}")
    else:
        print(f"⚠️  GitHub handler unavailable: GITHUB_PERSONAL_ACCESS_TOKEN not set")
        print("   To enable GitHub tools, set GITHUB_PERSONAL_ACCESS_TOKEN environment variable")
    
    print("\nTesting tool list...")
    import asyncio
    from devtools_mcp import handle_list_tools
    
    async def test():
        tools = await handle_list_tools()
        docker_tools = [t for t in tools if t.name.startswith("docker_")]
        github_tools = [t for t in tools if t.name.startswith("github_")]
        
        print(f"\n✓ Found {len(tools)} tools total:")
        print(f"  - Docker tools: {len(docker_tools)}")
        print(f"  - GitHub tools: {len(github_tools)}")
        
        if docker_tools:
            print("\nDocker tools available:")
            for tool in docker_tools:
                print(f"  - {tool.name}: {tool.description}")
        
        if github_tools:
            print("\nGitHub tools available:")
            for tool in github_tools:
                print(f"  - {tool.name}: {tool.description}")
    
    asyncio.run(test())
    
    if github_available:
        print("\n✅ All tests passed! DevTools MCP is ready with all features.")
    else:
        print("\n✅ Tests passed! DevTools MCP is ready (Docker tools only).")
        print("   To enable GitHub tools, set GITHUB_PERSONAL_ACCESS_TOKEN")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nPlease run: ./install_dependencies.sh")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)