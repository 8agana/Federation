#!/usr/bin/env python3
"""
Test script for FederationWeb search providers
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

async def test_duckduckgo_search():
    """Test DuckDuckGo search provider"""
    try:
        print("Testing DuckDuckGo search provider...")
        
        from federation_web.core.providers import DuckDuckGoProvider
        
        config = {
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "search_timeout": 30
        }
        
        provider = DuckDuckGoProvider(config)
        results = await provider.search("AI collaboration frameworks 2025", max_results=3)
        
        print(f"✅ DuckDuckGo search successful: {len(results)} results")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
            print(f"     {result['url']}")
            print(f"     {result['snippet'][:100]}...")
            print()
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multi_provider_search():
    """Test MultiProviderSearch"""
    try:
        print("\nTesting MultiProviderSearch...")
        
        from federation_web.core.providers import MultiProviderSearch
        
        config = {
            "brave_api_key": "",
            "google_api_key": "",
            "google_search_engine_id": "",
            "fallback_chain": ["duckduckgo"],
            "search_timeout": 30,
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        search = MultiProviderSearch(config)
        result = await search.search("collaborative AI development", max_results=3)
        
        print(f"✅ MultiProviderSearch successful")
        print(f"   Results: {len(result.get('results', []))}")
        print(f"   Providers used: {result.get('providers_used', [])}")
        print(f"   Success: {result.get('success', False)}")
        
        return result.get('success', False) and len(result.get('results', [])) > 0
        
    except Exception as e:
        print(f"❌ MultiProviderSearch failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing FederationWeb Search Providers...")
    
    tests_passed = 0
    total_tests = 2
    
    if await test_duckduckgo_search():
        tests_passed += 1
    
    if await test_multi_provider_search():
        tests_passed += 1
    
    print(f"\n📊 Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All search tests passed!")
        return True
    else:
        print("💥 Some search tests failed.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)