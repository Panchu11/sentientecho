"""
Caching utilities for improved performance.
"""

import asyncio
import time
import hashlib
import json
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from collections import OrderedDict

try:
    from .logger import get_logger
except ImportError:
    # For direct execution/testing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from logger import get_logger

logger = get_logger(__name__)


class LRUCache:
    """Thread-safe LRU cache implementation."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of items to cache
            ttl_seconds: Time to live for cache entries in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self._lock = asyncio.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        async with self._lock:
            if key not in self.cache:
                return None
            
            # Check if expired
            if self._is_expired(key):
                del self.cache[key]
                del self.timestamps[key]
                return None
            
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            
            return value
    
    async def set(self, key: str, value: Any) -> None:
        """Set item in cache."""
        async with self._lock:
            # Remove if already exists
            if key in self.cache:
                del self.cache[key]
            
            # Add new item
            self.cache[key] = value
            self.timestamps[key] = time.time()
            
            # Remove oldest items if over capacity
            while len(self.cache) > self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]
    
    async def delete(self, key: str) -> bool:
        """Delete item from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                del self.timestamps[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            self.timestamps.clear()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self.timestamps:
            return True
        
        age = time.time() - self.timestamps[key]
        return age > self.ttl_seconds
    
    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count removed."""
        removed_count = 0
        async with self._lock:
            expired_keys = [
                key for key in self.cache.keys()
                if self._is_expired(key)
            ]
            
            for key in expired_keys:
                del self.cache[key]
                del self.timestamps[key]
                removed_count += 1
        
        if removed_count > 0:
            logger.debug(f"Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        async with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "oldest_entry": min(self.timestamps.values()) if self.timestamps else None,
                "newest_entry": max(self.timestamps.values()) if self.timestamps else None
            }


class QueryCache:
    """Specialized cache for query results."""
    
    def __init__(self, max_size: int = 500, ttl_seconds: int = 300):
        """Initialize query cache."""
        self.cache = LRUCache(max_size, ttl_seconds)
        self.hit_count = 0
        self.miss_count = 0
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for consistent caching."""
        # Convert to lowercase and strip whitespace
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        # Remove common punctuation that doesn't affect meaning
        normalized = normalized.replace('?', '').replace('!', '').replace('.', '')
        
        return normalized
    
    async def get_cached_result(self, query: str) -> Optional[Any]:
        """Get cached result for query."""
        normalized_query = self._normalize_query(query)
        key = f"query:{normalized_query}"
        
        result = await self.cache.get(key)
        
        if result is not None:
            self.hit_count += 1
            logger.debug(f"Cache hit for query: {query[:50]}...")
        else:
            self.miss_count += 1
            logger.debug(f"Cache miss for query: {query[:50]}...")
        
        return result
    
    async def cache_result(self, query: str, result: Any) -> None:
        """Cache result for query."""
        normalized_query = self._normalize_query(query)
        key = f"query:{normalized_query}"
        
        await self.cache.set(key, result)
        logger.debug(f"Cached result for query: {query[:50]}...")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        cache_stats = await self.cache.get_stats()
        
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **cache_stats,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


def cache_async_function(cache: LRUCache, ttl_seconds: Optional[int] = None):
    """
    Decorator to cache async function results.
    
    Args:
        cache: Cache instance to use
        ttl_seconds: Override TTL for this function
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"func:{func.__name__}:{cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = await cache.get(key)
            if result is not None:
                logger.debug(f"Cache hit for function {func.__name__}")
                return result
            
            # Execute function
            logger.debug(f"Cache miss for function {func.__name__}, executing...")
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache.set(key, result)
            
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """Manages multiple cache instances."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.query_cache = QueryCache(max_size=500, ttl_seconds=300)  # 5 minutes
        self.post_cache = LRUCache(max_size=1000, ttl_seconds=600)    # 10 minutes
        self.ai_cache = LRUCache(max_size=200, ttl_seconds=1800)      # 30 minutes

        # Cleanup task will be started when needed
        self._cleanup_task = None
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure cache manager is initialized with cleanup task."""
        if not self._initialized:
            self._start_cleanup_task()
            self._initialized = True

    def _start_cleanup_task(self):
        """Start background cleanup task."""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(60)  # Run every minute

                    # Cleanup expired entries
                    await self.query_cache.cache.cleanup_expired()
                    await self.post_cache.cleanup_expired()
                    await self.ai_cache.cleanup_expired()

                except Exception as e:
                    logger.error(f"Error in cache cleanup: {e}")

        try:
            self._cleanup_task = asyncio.create_task(cleanup_loop())
        except RuntimeError:
            # No event loop running, will start later
            pass
    
    async def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all caches."""
        await self._ensure_initialized()
        return {
            "query_cache": await self.query_cache.get_cache_stats(),
            "post_cache": await self.post_cache.get_stats(),
            "ai_cache": await self.ai_cache.get_stats()
        }
    
    async def clear_all_caches(self) -> None:
        """Clear all caches."""
        await self.query_cache.cache.clear()
        await self.post_cache.clear()
        await self.ai_cache.clear()
        logger.info("Cleared all caches")
    
    async def shutdown(self):
        """Shutdown cache manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass


# Global cache manager instance
cache_manager = CacheManager()


# Convenience functions
async def get_cached_query_result(query: str) -> Optional[Any]:
    """Get cached result for query."""
    await cache_manager._ensure_initialized()
    return await cache_manager.query_cache.get_cached_result(query)


async def cache_query_result(query: str, result: Any) -> None:
    """Cache result for query."""
    await cache_manager._ensure_initialized()
    await cache_manager.query_cache.cache_result(query, result)


async def get_cache_stats() -> Dict[str, Any]:
    """Get all cache statistics."""
    return await cache_manager.get_all_stats()
