try:
    import redis  # type: ignore
except ImportError:
    redis = None
    # Redis client not installed; caching will be disabled gracefully
import json
from typing import Any, Optional
from app.config import settings
from app.utils.logger import logger


class CacheService:
    """Service for caching query results and schemas"""
    
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        if not redis:
            logger.warning("Redis client not installed. Caching disabled.")
            self.redis_client = None
            return

        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(value)
            return None
        
        except Exception as e:
            logger.error(f"Cache get failed: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = None
    ):
        """Set value in cache"""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            logger.info(f"Cached value for key: {key}")
        
        except Exception as e:
            logger.error(f"Cache set failed: {str(e)}")
    
    def delete(self, key: str):
        """Delete value from cache"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
            logger.info(f"Deleted cache key: {key}")
        
        except Exception as e:
            logger.error(f"Cache delete failed: {str(e)}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} keys matching pattern: {pattern}")
        
        except Exception as e:
            logger.error(f"Cache clear failed: {str(e)}")
    
    def generate_query_key(
        self,
        query: str,
        database_name: str
    ) -> str:
        """Generate cache key for query"""
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"query:{database_name}:{query_hash}"


# Global instance
cache_service = CacheService()
