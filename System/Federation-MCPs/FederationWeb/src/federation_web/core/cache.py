"""
Caching system for FederationWeb
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional
import asyncio
from datetime import datetime, timedelta
import logging

class WebCache:
    """Simple file-based cache for web content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache_dir = Path.home() / ".federation" / "web_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.enabled = config.get("cache_enabled", True)
        self.default_ttl = config.get("cache_ttl", 300)  # 5 minutes
        self.max_size_mb = config.get("max_cache_size", 100)
        
        # In-memory cache for hot data
        self.memory_cache = {}
        self.memory_cache_times = {}
        
    def _get_cache_key(self, key_data: Dict[str, Any]) -> str:
        """Generate cache key from request data"""
        # Sort dict for consistent hashing
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        # Use first 2 chars for directory to avoid too many files in one dir
        subdir = cache_key[:2]
        return self.cache_dir / subdir / f"{cache_key}.json"
    
    async def get(self, key_data: Dict[str, Any]) -> Optional[Any]:
        """Get cached data if available and not expired"""
        if not self.enabled:
            return None
            
        cache_key = self._get_cache_key(key_data)
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            cached_time = self.memory_cache_times.get(cache_key, 0)
            if time.time() - cached_time < 60:  # 1 minute memory cache
                self.logger.debug(f"Memory cache hit for {cache_key}")
                return self.memory_cache[cache_key]
        
        # Check file cache
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    
                # Check expiration
                cached_time = cached_data.get("cached_at", 0)
                ttl = cached_data.get("ttl", self.default_ttl)
                
                if time.time() - cached_time < ttl:
                    self.logger.debug(f"File cache hit for {cache_key}")
                    data = cached_data.get("data")
                    
                    # Update memory cache
                    self.memory_cache[cache_key] = data
                    self.memory_cache_times[cache_key] = time.time()
                    
                    return data
                else:
                    self.logger.debug(f"Cache expired for {cache_key}")
                    # Remove expired cache
                    cache_path.unlink()
                    
            except Exception as e:
                self.logger.error(f"Error reading cache: {e}")
                
        return None
    
    async def set(self, key_data: Dict[str, Any], data: Any, ttl: Optional[int] = None) -> None:
        """Store data in cache"""
        if not self.enabled:
            return
            
        if ttl is None:
            ttl = self.default_ttl
            
        cache_key = self._get_cache_key(key_data)
        cache_path = self._get_cache_path(cache_key)
        
        # Create directory if needed
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        cached_data = {
            "key_data": key_data,
            "data": data,
            "cached_at": time.time(),
            "ttl": ttl,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
                
            # Update memory cache
            self.memory_cache[cache_key] = data
            self.memory_cache_times[cache_key] = time.time()
            
            self.logger.debug(f"Cached data for {cache_key}")
            
            # Check cache size periodically
            if len(self.memory_cache) % 10 == 0:
                await self._check_cache_size()
                
        except Exception as e:
            self.logger.error(f"Error writing cache: {e}")
    
    async def _check_cache_size(self) -> None:
        """Check and clean cache if too large"""
        total_size = 0
        cache_files = []
        
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.json"):
                    size = cache_file.stat().st_size
                    mtime = cache_file.stat().st_mtime
                    total_size += size
                    cache_files.append((cache_file, size, mtime))
        
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb > self.max_size_mb:
            self.logger.info(f"Cache size {total_size_mb:.1f}MB exceeds limit, cleaning...")
            
            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda x: x[2])
            
            # Remove oldest files until under limit
            for cache_file, size, _ in cache_files:
                if total_size_mb <= self.max_size_mb * 0.8:  # Clean to 80% of limit
                    break
                    
                try:
                    cache_file.unlink()
                    total_size_mb -= size / (1024 * 1024)
                    self.logger.debug(f"Removed {cache_file.name}")
                except Exception as e:
                    self.logger.error(f"Error removing cache file: {e}")
    
    async def clear(self) -> None:
        """Clear all cache"""
        self.memory_cache.clear()
        self.memory_cache_times.clear()
        
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.json"):
                    try:
                        cache_file.unlink()
                    except Exception as e:
                        self.logger.error(f"Error clearing cache file: {e}")
                        
        self.logger.info("Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        file_count = 0
        total_size = 0
        
        for subdir in self.cache_dir.iterdir():
            if subdir.is_dir():
                for cache_file in subdir.glob("*.json"):
                    file_count += 1
                    total_size += cache_file.stat().st_size
        
        return {
            "memory_entries": len(self.memory_cache),
            "file_entries": file_count,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_mb,
            "enabled": self.enabled,
            "default_ttl": self.default_ttl
        }