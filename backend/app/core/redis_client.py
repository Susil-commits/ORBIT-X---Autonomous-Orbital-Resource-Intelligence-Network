"""Async Redis Client for ORBIT-X Constellation State Caching, Distributed Locks & Event Pub/Sub.

Strictly uses redis.asyncio to avoid any blocking calls on the asyncio event loop.
Provides graceful in-memory disconnected fallback if Redis is offline during local development.
"""

import json
import time
import uuid
import random
import asyncio
import logging
from typing import Optional, Dict, Any, AsyncIterator, Tuple
from contextlib import asynccontextmanager
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("orbitx.redis")

# Safe Lua script for atomic unlock (only release if token matches)
UNLOCK_LUA_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class DistributedLockError(Exception):
    """Raised when distributed lock cannot be acquired within the timeout window."""
    pass


class AsyncRedisManager:
    """Production-grade non-blocking async Redis manager with distributed locking,

    caching abstractions, idempotency, and in-memory resilience fallback.
    """

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self.client: Optional[aioredis.Redis] = None
        self._is_connected: bool = False
        self._warned_offline: bool = False
        
        # In-memory fallbacks when Redis is offline
        self._memory_cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expire_timestamp)
        self._memory_locks: Dict[str, asyncio.Lock] = {}
        
        # Operational telemetry counters
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._locks_acquired: int = 0
        self._locks_contested: int = 0
        self._lock_timeouts: int = 0
        self._events_published: int = 0

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    async def connect(self):
        """Initializes async Redis client pool with connection ping."""
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
                logger.warning("Redis is offline (%s) - operating with in-memory fallback.", e)
                self._warned_offline = True

    async def ping(self) -> bool:
        """Pings Redis to check health."""
        if not self._is_connected or not self.client:
            return False
        try:
            return bool(await self.client.ping())
        except Exception:
            self._is_connected = False
            return False

    # ----------------------------------------------------
    # Core Key-Value & JSON Operations
    # ----------------------------------------------------

    async def set_json(self, key: str, value: Any, expire_seconds: int = 300) -> bool:
        """Sets a JSON-serializable value with expiration."""
        if self._is_connected and self.client:
            try:
                await self.client.set(key, json.dumps(value), ex=expire_seconds)
                return True
            except Exception as e:
                logger.warning("Redis set_json failed for '%s', falling back to memory: %s", key, e)
                self._is_connected = False
        
        # In-memory fallback
        expire_at = time.time() + expire_seconds if expire_seconds > 0 else float("inf")
        self._memory_cache[key] = (value, expire_at)
        return True

    async def get_json(self, key: str) -> Optional[Any]:
        """Gets and parses JSON value with automatic hit/miss metrics."""
        now = time.time()
        if self._is_connected and self.client:
            try:
                raw = await self.client.get(key)
                if raw is not None:
                    self._cache_hits += 1
                    return json.loads(raw)
                self._cache_misses += 1
                return None
            except Exception as e:
                logger.warning("Redis get_json failed for '%s', falling back to memory: %s", key, e)
                self._is_connected = False

        # In-memory fallback
        if key in self._memory_cache:
            val, expire_at = self._memory_cache[key]
            if now < expire_at:
                self._cache_hits += 1
                return val
            else:
                del self._memory_cache[key]
                
        self._cache_misses += 1
        return None

    async def delete(self, key: str) -> bool:
        """Deletes a key from Redis and memory."""
        self._memory_cache.pop(key, None)
        if self._is_connected and self.client:
            try:
                await self.client.delete(key)
                return True
            except Exception:
                return False
        return True

    # ----------------------------------------------------
    # Domain Caching Helpers (Telemetry, TLE, Mission)
    # ----------------------------------------------------

    async def cache_telemetry(self, satellite_id: str, telemetry: Dict[str, Any], ttl_s: int = 60) -> bool:
        """Caches satellite telemetry frame at telemetry:sat:{satellite_id}."""
        key = f"telemetry:sat:{satellite_id}"
        return await self.set_json(key, telemetry, expire_seconds=ttl_s)

    async def get_cached_telemetry(self, satellite_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached satellite telemetry frame."""
        key = f"telemetry:sat:{satellite_id}"
        return await self.get_json(key)

    async def cache_tle(self, satellite_id: str, tle_data: Dict[str, Any], ttl_s: int = 3600) -> bool:
        """Caches satellite TLE orbital data at tle:satellite:{satellite_id}."""
        key = f"tle:satellite:{satellite_id}"
        return await self.set_json(key, tle_data, expire_seconds=ttl_s)

    async def get_cached_tle(self, satellite_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached satellite TLE orbital data."""
        key = f"tle:satellite:{satellite_id}"
        return await self.get_json(key)

    async def cache_mission_state(self, mission_id: str, mission_data: Dict[str, Any], ttl_s: int = 600) -> bool:
        """Caches mission state at mission:{mission_id}."""
        key = f"mission:{mission_id}"
        return await self.set_json(key, mission_data, expire_seconds=ttl_s)

    async def get_cached_mission_state(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached mission state."""
        key = f"mission:{mission_id}"
        return await self.get_json(key)

    # ----------------------------------------------------
    # Event Idempotency Helpers
    # ----------------------------------------------------

    async def is_event_processed(self, event_id: str) -> bool:
        """Checks if an event has already been processed by event_id."""
        key = f"processed:event:{event_id}"
        val = await self.get_json(key)
        return val is not None

    async def mark_event_processed(self, event_id: str, ttl_s: int = 86400) -> bool:
        """Marks an event as processed for 24 hours to enforce idempotency."""
        key = f"processed:event:{event_id}"
        return await self.set_json(key, {"processed_at": time.time()}, expire_seconds=ttl_s)

    # ----------------------------------------------------
    # Distributed Locking (with spin-retry, auto-release, & memory fallback)
    # ----------------------------------------------------

    @asynccontextmanager
    async def distributed_lock(
        self,
        resource: str,
        timeout_s: float = 5.0,
        lease_s: float = 10.0,
    ) -> AsyncIterator[str]:
        """Asynchronous context manager for distributed locking.
        
        Args:
            resource: Resource identifier to lock (e.g., 'satellite:SAT-004' or 'scheduler:global')
            timeout_s: Maximum seconds to wait to acquire the lock
            lease_s: Auto-expiration TTL in seconds if not explicitly released
            
        Yields:
            lock_token (str): Unique token identifying the lock holder
            
        Raises:
            DistributedLockError: If lock cannot be acquired within timeout_s
        """
        lock_key = f"lock:{resource}"
        lock_token = str(uuid.uuid4())
        deadline = time.time() + timeout_s
        acquired = False

        if self._is_connected and self.client:
            # Redis-based distributed lock
            while time.time() < deadline:
                try:
                    # SET key token NX EX lease_s
                    ok = await self.client.set(lock_key, lock_token, nx=True, ex=int(lease_s))
                    if ok:
                        acquired = True
                        self._locks_acquired += 1
                        break
                    else:
                        self._locks_contested += 1
                except Exception as e:
                    logger.warning("Redis error during lock attempt on '%s': %s", lock_key, e)
                    self._is_connected = False
                    break
                
                # Exponential/jittered backoff (20ms to 60ms)
                await asyncio.sleep(0.02 + random.uniform(0.0, 0.04))

        if not acquired and not self._is_connected:
            # Fallback to local asyncio lock table
            if lock_key not in self._memory_locks:
                self._memory_locks[lock_key] = asyncio.Lock()
            mem_lock = self._memory_locks[lock_key]
            
            try:
                # Wait for local memory lock up to remaining deadline
                wait_time = max(0.01, deadline - time.time())
                await asyncio.wait_for(mem_lock.acquire(), timeout=wait_time)
                acquired = True
                self._locks_acquired += 1
            except (asyncio.TimeoutError, TimeoutError):
                self._lock_timeouts += 1
                raise DistributedLockError(f"Timed out acquiring fallback lock for '{resource}' after {timeout_s:.2f}s")
        elif not acquired:
            self._lock_timeouts += 1
            raise DistributedLockError(f"Timed out acquiring distributed lock for '{resource}' after {timeout_s:.2f}s")

        try:
            yield lock_token
        finally:
            if self._is_connected and self.client:
                try:
                    await self.client.eval(UNLOCK_LUA_SCRIPT, 1, lock_key, lock_token)
                except Exception as e:
                    logger.warning("Error releasing distributed lock '%s': %s", lock_key, e)
            else:
                mem_lock = self._memory_locks.get(lock_key)
                if mem_lock and mem_lock.locked():
                    try:
                        mem_lock.release()
                    except RuntimeError:
                        pass

    # ----------------------------------------------------
    # Pub/Sub Streaming
    # ----------------------------------------------------

    async def publish_event(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publishes an event to a Redis Pub/Sub channel asynchronously."""
        self._events_published += 1
        if not self._is_connected or not self.client:
            return False
        try:
            await self.client.publish(channel, json.dumps(message))
            return True
        except Exception:
            return False

    # ----------------------------------------------------
    # Operational Diagnostics
    # ----------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Returns runtime cache, lock, and connection statistics."""
        total_queries = self._cache_hits + self._cache_misses
        hit_ratio = (self._cache_hits / total_queries * 100.0) if total_queries > 0 else 0.0
        return {
            "is_connected": self._is_connected,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_ratio_pct": round(hit_ratio, 2),
            "locks_acquired": self._locks_acquired,
            "locks_contested": self._locks_contested,
            "lock_timeouts": self._lock_timeouts,
            "events_published": self._events_published,
            "in_memory_keys": len(self._memory_cache),
        }

    async def close(self):
        """Gracefully closes Redis connection pool."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass
            self._is_connected = False


redis_manager = AsyncRedisManager()
