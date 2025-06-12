#!/usr/bin/env python3
"""
Test Brave Search API integration
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

async def test_brave_search():
    """Test Brave Search provider with API key"""
    try:
        print("Testing Brave Search provider...")
        
        from federation_web.core.providers import BraveSearchProvider
        
        config = {
            "search_timeout": 30,
            "user_agent": "FederationWeb/1.0"
        }
        
        api_key = "BSAB8EYo0Fe3dDtEJrbfJhnjTc0ZQvs"
        provider = BraveSearchProvider(config, api_key)
        results = await provider.search("AI collaboration frameworks 2025", max_results=3)
        
        print(f"✅ Brave search successful: {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     {result['url']}")
            print(f"     {result['snippet'][:100]}...")
            print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Brave search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multi_provider_with_brave():
    """Test MultiProviderSearch with Brave API key"""
    try:
        print("\nTesting MultiProviderSearch with Brave...")
        
        from federation_web.core.providers import MultiProviderSearch
        
        config = {
            "brave_api_key": "BSAB8EYo0Fe3dDtEJrbfJhnjTc0ZQvs",
            "google_api_key": "",
            "google_search_engine_id": "",
            "fallback_chain": ["brave", "duckduckgo"],
            "search_timeout": 30,
            "user_agent": "FederationWeb/1.0"
        }
        
        search = MultiProviderSearch(config)
        result = await search.search("latest machine learning frameworks", max_results=5)
        
        print(f"✅ MultiProviderSearch with Brave")
        print(f"   Results: {len(result.get('results', []))}")
        print(f"   Providers used: {result.get('providers_used', [])}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Errors: {result.get('errors', 'None')}")
        
        if result.get('results'):
            print("\n   Sample results:")
            for i, res in enumerate(result['results'][:2], 1):
                print(f"   {i}. {res['title']}")
                print(f"      {res['url']}")
        
        return result.get('success', False) and len(result.get('results', [])) > 0
        
    except Exception as e:
        print(f"❌ MultiProviderSearch with Brave failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run Brave search tests"""
    print("🧪 Testing Brave Search Integration...")
    
    tests_passed = 0
    total_tests = 2
    
    if await test_brave_search():
        tests_passed += 1
    
    if await test_multi_provider_with_brave():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 Brave Search integration successful!")
        return True
    else:
        print("💥 Some Brave Search tests failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)