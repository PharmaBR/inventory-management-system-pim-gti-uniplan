"""Redis cache configuration and utilities."""
from typing import Optional, Any
import json
from redis.asyncio import Redis, ConnectionPool

from src.core.config import settings
from src.core.logging import logger


# Global Redis connection pool
_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


async def get_redis_pool() -> ConnectionPool:
    """Get or create Redis connection pool."""
    global _redis_pool
    
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
        logger.info(f"Redis connection pool created: {settings.REDIS_URL}")
    
    return _redis_pool


async def get_redis() -> Redis:
    """
    Get Redis client instance.
    
    Returns:
        Redis client
    """
    global _redis_client
    
    if _redis_client is None:
        pool = await get_redis_pool()
        _redis_client = Redis(connection_pool=pool)
        logger.info("Redis client initialized")
    
    return _redis_client


async def close_redis():
    """Close Redis connections."""
    global _redis_client, _redis_pool
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None
    
    logger.info("Redis connections closed")


class Cache:
    """Helper class for cache operations."""
    
    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            redis = await get_redis()
            value = await redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            redis = await get_redis()
            serialized = json.dumps(value, default=str)
            await redis.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            redis = await get_redis()
            await redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @staticmethod
    async def invalidate_pattern(pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "tenant:123:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            redis = await get_redis()
            keys = await redis.keys(pattern)
            if keys:
                return await redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache invalidate pattern error for {pattern}: {e}")
            return 0


# Cache key builders
def tenant_cache_key(tenant_id: str) -> str:
    """Build cache key for tenant config."""
    return f"tenant:{tenant_id}:config"


def product_cache_key(tenant_id: str, product_id: str) -> str:
    """Build cache key for product."""
    return f"tenant:{tenant_id}:product:{product_id}"


def user_cache_key(user_id: str) -> str:
    """Build cache key for user."""
    return f"user:{user_id}"
