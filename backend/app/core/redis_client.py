"""Async Redis Client for ORBIT-X Constellation State Caching & Event Pub/Sub.

Strictly uses redis.asyncio to avoid any blocking calls on the asyncio event loop.
Provides graceful disconnected fallback if Redis is offline during local dev.
"""

import json
import logging
from typing import Optional, Dict, Any
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("orbitx.redis")


class AsyncRedisManager:
    """Manages strictly non-blocking async Redis connections with offline resilience."""

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None
        self._is_connected: bool = False
        self._warned_offline: bool = False

    async def connect(self):
        """Initializes async Redis client pool."""
        try:
            self.client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )
            # Test ping
            await self.client.ping()
            self._is_connected = True
            logger.info("Connected to Redis at %s", self.redis_url)
        except Exception as e:
            self._is_connected = False
            if not self._warned_offline:
                logger.warning("Redis is offline (%s) - running in in-memory fallback mode.", e)
                self._warned_offline = True

    async def set_json(self, key: str, value: Dict[str, Any], expire_seconds: int = 300) -> bool:
        """Sets a JSON serialized key asynchronously."""
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.set(key, json.dumps(value), ex=expire_seconds)
            return True
        except Exception:
            return False

    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Gets and parses JSON key asynchronously."""
        if not self._is_connected or not self.client:
            return None
        try:
            raw = await self.client.get(key)
            if raw:
                return json.loads(raw)
            return None
        except Exception:
            return None

    async def publish_event(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publishes an event to a Redis Pub/Sub channel asynchronously."""
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.publish(channel, json.dumps(message))
            return True
        except Exception:
            return False

    async def close(self):
        """Gracefully closes Redis connection pool."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
            self._is_connected = False


redis_manager = AsyncRedisManager()
