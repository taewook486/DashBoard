"""
Caching service for DashBoard application.
@SPEC:IMPROVE-001 REQ-PERF-002
"""

import time
import hashlib
import json
from typing import Optional, Any, Dict, Callable
from functools import wraps
import structlog

logger = structlog.get_logger(__name__)


class CacheService:
    """
    In-memory cache service with TTL support.
    @SPEC:IMPROVE-001 REQ-PERF-002

    Note: For production, consider using Redis for distributed caching.
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache service.

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
        logger.info("Cache service initialized", default_ttl=default_ttl)

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check expiration
        if entry['expires_at'] < time.time():
            del self._cache[key]
            logger.debug("Cache entry expired", key=key)
            return None

        logger.debug("Cache hit", key=key)
        return entry['value']

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
        """
        ttl = ttl or self._default_ttl
        expires_at = time.time() + ttl

        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }

        logger.debug("Cache set", key=key, ttl=ttl)

    def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug("Cache deleted", key=key)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info("Cache cleared", entries_removed=count)

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry['expires_at'] < current_time
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            logger.info("Cache cleanup", entries_removed=len(expired_keys))

        return len(expired_keys)

    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """
        Generate a cache key from arguments.
        Skips the first argument if it's a class instance (self).

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hash-based cache key
        """
        # Skip 'self' or 'cls' for methods (first arg if not a primitive type)
        if args and hasattr(args[0], '__class__') and not isinstance(args[0], (str, int, float, bool, list, dict, tuple)):
            args = args[1:]  # Skip self/cls

        # Convert args to strings for serialization
        try:
            key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fallback to string representation
            key_data = str({'args': args, 'kwargs': kwargs})
        return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: Optional[int] = None, key_prefix: str = ''):
    """
    Decorator for caching function results.
    @SPEC:IMPROVE-001 REQ-PERF-002

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Usage:
        @cached(ttl=300, key_prefix='market_data')
        def get_market_data(ticker):
            ...
    """
    def decorator(func: Callable) -> Callable:
        _cache = CacheService(default_ttl=ttl or 300)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key (skips self for methods)
            cache_key = f"{key_prefix}:{CacheService.generate_key(*args, **kwargs)}"

            # Try to get from cache
            cached_result = _cache.get(cache_key)
            if cached_result is not None:
                logger.debug(
                    "Cache hit for function",
                    function=func.__name__,
                    key=cache_key
                )
                return cached_result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result)

            logger.debug(
                "Cache miss for function",
                function=func.__name__,
                key=cache_key
            )

            return result

        # Add cache management methods to wrapper
        wrapper.cache_clear = _cache.clear
        wrapper.cache_cleanup = _cache.cleanup_expired

        return wrapper

    return decorator


# Global cache instance
_global_cache: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get or create global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheService()
    return _global_cache


def init_cache(default_ttl: int = 300) -> CacheService:
    """Initialize global cache with custom TTL."""
    global _global_cache
    _global_cache = CacheService(default_ttl=default_ttl)
    return _global_cache
