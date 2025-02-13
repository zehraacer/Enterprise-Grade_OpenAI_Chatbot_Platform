# utils/cache_manager.py
from typing import Any, Optional
import pickle
import redis
from datetime import timedelta

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url)

    def set(self, key: str, value: Any, expire_in: int = 3600):
        """Store value in cache with expiration"""
        serialized_value = pickle.dumps(value)
        self.redis_client.setex(key, timedelta(seconds=expire_in), serialized_value)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        value = self.redis_client.get(key)
        if value:
            return pickle.loads(value)
        return None

    def delete(self, key: str):
        """Remove value from cache"""
        self.redis_client.delete(key)

    def clear(self):
        """Clear all cache"""
        self.redis_client.flushall()