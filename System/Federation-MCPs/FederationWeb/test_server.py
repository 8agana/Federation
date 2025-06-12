#!/usr/bin/env python3
"""
Test script for FederationWeb MCP server
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test all imports work correctly"""
    try:
        print("Testing config import...")
        from federation_web.utils.config import Config
        print("✅ Config import successful")
        
        print("Testing context import...")
        from federation_web.core.context import FederationContext
        print("✅ Context import successful")
        
        print("Testing core modules...")
        from federation_web.core.providers import MultiProviderSearch
        from federation_web.core.extraction import ContentExtractor
        from federation_web.core.cache import WebCache
        from federation_web.core.react import ReactOrchestrator
        print("✅ Core modules import successful")
        
        print("Testing tools...")
        from federation_web.tools.base import BaseTool
        from federation_web.tools.research import ResearchTool
        from federation_web.tools.interests import InterestsTool
        print("✅ Tools import successful")
        
        print("Testing server...")
        from federation_web.server import FederationWebServer
        print("✅ Server import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_initialization():
    """Test server initialization"""
    try:
        print("\nTesting server initialization...")
        from federation_web.server import FederationWebServer
        
        server = FederationWebServer()
        print("✅ Server initialization successful")
        
        # Test tool schemas
        print("Testing tool schemas...")
        research_schema = server.research_tool.get_schema()
        interests_schema = server.interests_tool.get_schema()
        print(f"✅ Research tool schema: {len(research_schema.get('properties', {}))} properties")
        print(f"✅ Interests tool schema: {len(interests_schema.get('properties', {}))} properties")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing FederationWeb MCP Server...")
    
    if test_imports():
        if test_initialization():
            print("\n🎉 All tests passed! FederationWeb MCP server is ready.")
            sys.exit(0)
    
    print("\n💥 Tests failed. Check errors above.")
    sys.exit(1)