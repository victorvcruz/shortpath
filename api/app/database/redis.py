import os
import redis
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class RedisManager:
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> redis.Redis:
        try:
            client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
            return client
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def health_check(self) -> bool:
        try:
            self.client.ping()
            return True
        except redis.ConnectionError:
            logger.warning("Redis health check failed")
            return False
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Redis connection closed")

redis_manager = RedisManager()

def get_redis() -> redis.Redis:
    return redis_manager.client
