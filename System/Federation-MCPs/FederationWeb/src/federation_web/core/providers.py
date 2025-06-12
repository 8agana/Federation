"""
Search providers for FederationWeb
"""

import asyncio
import httpx
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
import logging
from bs4 import BeautifulSoup
import re

class SearchProvider(ABC):
    """Base class for search providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Execute search and return results"""
        pass
    
    def format_result(self, title: str, url: str, snippet: str, **kwargs) -> Dict[str, Any]:
        """Format search result consistently"""
        return {
            "title": title,
            "url": url,
            "snippet": snippet,
            "provider": self.__class__.__name__,
            **kwargs
        }

class BraveSearchProvider(SearchProvider):
    """Brave Search API provider"""
    
    def __init__(self, config: Dict[str, Any], api_key: str):
        super().__init__(config)
        self.api_key = api_key
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Brave Search API"""
        if not self.api_key:
            raise ValueError("Brave API key not configured")
            
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        
        params = {
            "q": query,
            "count": min(max_results, 20),  # Brave max is 20
            "safesearch": "moderate",
            "search_lang": "en",
            "country": "us"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=self.config.get("search_timeout", 30)
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append(self.format_result(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        age=item.get("age"),
                        favicon=item.get("favicon")
                    ))
                
                return results
                
            except httpx.HTTPError as e:
                self.logger.error(f"Brave search error: {e}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in Brave search: {e}")
                raise

class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo search provider (no API key required)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = "https://html.duckduckgo.com/html"
        
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo HTML interface"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        data = {
            "q": query,
            "b": "",
            "kl": "us-en"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.base_url,
                    data=data,
                    headers=headers,
                    timeout=self.config.get("search_timeout", 30),
                    follow_redirects=True
                )
                response.raise_for_status()
                
                # Parse HTML response with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Find search result containers in DuckDuckGo HTML
                result_links = soup.find_all('a', class_='result__a')
                
                for link in result_links[:max_results]:
                    try:
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        
                        # Find the snippet/description
                        parent = link.find_parent('div', class_='result__body')
                        snippet = ""
                        if parent:
                            snippet_elem = parent.find('a', class_='result__snippet')
                            if snippet_elem:
                                snippet = snippet_elem.get_text(strip=True)
                        
                        if not snippet:
                            snippet = "No description available"
                        
                        if url and title and not url.startswith('javascript:'):
                            results.append(self.format_result(
                                title=title,
                                url=url,
                                snippet=snippet
                            ))
                            
                    except Exception as e:
                        self.logger.warning(f"Error parsing DuckDuckGo result: {e}")
                        continue
                
                self.logger.info(f"DuckDuckGo search found {len(results)} results for: {query}")
                return results
                
            except Exception as e:
                self.logger.error(f"DuckDuckGo search error: {e}")
                raise

class GoogleSearchProvider(SearchProvider):
    """Google Custom Search API provider"""
    
    def __init__(self, config: Dict[str, Any], api_key: str, search_engine_id: str):
        super().__init__(config)
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API"""
        if not self.api_key or not self.search_engine_id:
            raise ValueError("Google API key or Search Engine ID not configured")
            
        params = {
            "key": self.api_key,
            "cx": self.search_engine_id,
            "q": query,
            "num": min(max_results, 10)  # Google max is 10 per request
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    params=params,
                    timeout=self.config.get("search_timeout", 30)
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", []):
                    results.append(self.format_result(
                        title=item.get("title", ""),
                        url=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        mime_type=item.get("mime"),
                        file_format=item.get("fileFormat")
                    ))
                
                return results
                
            except Exception as e:
                self.logger.error(f"Google search error: {e}")
                raise

class MultiProviderSearch:
    """Orchestrates multiple search providers with fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = self._initialize_providers()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _initialize_providers(self) -> Dict[str, Optional[SearchProvider]]:
        """Initialize available search providers"""
        providers = {}
        
        # Brave Search
        brave_key = self.config.get("brave_api_key") or self.config.get("search", {}).get("brave_api_key")
        if brave_key:
            providers["brave"] = BraveSearchProvider(self.config, brave_key)
        
        # DuckDuckGo (always available)
        providers["duckduckgo"] = DuckDuckGoProvider(self.config)
        
        # Google (if configured)
        google_key = self.config.get("google_api_key") or self.config.get("search", {}).get("google_api_key")
        google_cx = self.config.get("google_search_engine_id") or self.config.get("search", {}).get("google_search_engine_id")
        if google_key and google_cx:
            providers["google"] = GoogleSearchProvider(self.config, google_key, google_cx)
            
        return providers
    
    async def search(self, query: str, sources: List[str] = None, max_results: int = 10) -> Dict[str, Any]:
        """Search across multiple providers with fallback"""
        if sources is None or "auto" in sources:
            sources = self.config.get("fallback_chain", ["brave", "duckduckgo"])
            
        all_results = []
        errors = []
        used_providers = []
        
        for source in sources:
            if source not in self.providers:
                self.logger.warning(f"Provider {source} not available")
                continue
                
            provider = self.providers[source]
            try:
                self.logger.info(f"Searching with {source}: {query}")
                results = await provider.search(query, max_results)
                
                if results:
                    all_results.extend(results)
                    used_providers.append(source)
                    
                    # If we have enough results, stop
                    if len(all_results) >= max_results:
                        break
                        
            except Exception as e:
                self.logger.error(f"Error with {source}: {e}")
                errors.append({"provider": source, "error": str(e)})
                
                # Continue with fallback if enabled
                if self.config.get("fallback_enabled", True):
                    continue
                else:
                    raise
        
        # Deduplicate results by URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
                
        return {
            "query": query,
            "results": unique_results[:max_results],
            "total_results": len(unique_results),
            "providers_used": used_providers,
            "errors": errors if errors else None,
            "success": len(unique_results) > 0
        }