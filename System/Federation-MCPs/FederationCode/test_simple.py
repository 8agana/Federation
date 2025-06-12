#!/usr/bin/env python3
"""Simple test of Federation Code MCP core functionality without ChromaDB."""

import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_core():
    print("Testing Federation Code MCP core components...")
    
    # Test AsyncEngine
    from federation_code.core import AsyncEngine
    engine = AsyncEngine(max_workers=2, max_processes=1)
    await engine.start()
    print("✅ AsyncEngine started")
    
    # Test analyzer imports
    from federation_code.analyzers.ast_analyzer import ASTAnalyzer
    ast_analyzer = ASTAnalyzer()
    print("✅ ASTAnalyzer imported")
    
    # Test tools
    from federation_code.tools.analyze import AnalyzeTool
    analyze_tool = AnalyzeTool(engine)
    print("✅ AnalyzeTool created")
    
    await engine.stop()
    print("✅ AsyncEngine stopped")
    print("🎉 All core components working!")

if __name__ == "__main__":
    asyncio.run(test_core())