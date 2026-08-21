"""Integration and resilience test suite for AsyncRedisManager and Distributed Locks."""

import pytest
import asyncio
import time
from app.core.redis_client import AsyncRedisManager, DistributedLockError

@pytest.mark.asyncio
async def test_redis_in_memory_caching_and_ttl():
    """Verifies that Redis manager works seamlessly in in-memory fallback mode."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host-for-testing:9999/0")
    await mgr.connect()
    
    assert mgr.is_connected is False
    
    # Test JSON set and get
    data = {"satellite_id": "SAT-001", "battery_soc": 0.88, "status": "NOMINAL"}
    ok = await mgr.set_json("telemetry:sat:SAT-001", data, expire_seconds=2)
    assert ok is True
    
    retrieved = await mgr.get_json("telemetry:sat:SAT-001")
    assert retrieved is not None
    assert retrieved["satellite_id"] == "SAT-001"
    assert retrieved["battery_soc"] == 0.88
    
    # Test stats
    stats = mgr.get_stats()
    assert stats["cache_hits"] >= 1
    assert stats["cache_misses"] == 0
    assert stats["is_connected"] is False

@pytest.mark.asyncio
async def test_domain_caching_helpers():
    """Tests domain-specific caching helpers (Telemetry, TLE, Mission)."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host:9999/0")
    
    # Telemetry Cache
    tel = {"battery": 92.5, "temp_c": 24.1, "sunlit": True}
    assert await mgr.cache_telemetry("SAT-005", tel, ttl_s=60) is True
    cached_tel = await mgr.get_cached_telemetry("SAT-005")
    assert cached_tel["battery"] == 92.5
    
    # TLE Cache
    tle = {"line1": "1 25544U ...", "line2": "2 25544 ...", "epoch": 1787312400}
    assert await mgr.cache_tle("SAT-005", tle, ttl_s=3600) is True
    cached_tle = await mgr.get_cached_tle("SAT-005")
    assert cached_tle["line1"] == "1 25544U ..."
    
    # Mission Cache
    mission = {"mission_id": "M-101", "priority": 5, "status": "SCHEDULED"}
    assert await mgr.cache_mission_state("M-101", mission, ttl_s=300) is True
    cached_m = await mgr.get_cached_mission_state("M-101")
    assert cached_m["status"] == "SCHEDULED"

@pytest.mark.asyncio
async def test_event_idempotency():
    """Tests idempotency check and marking for Kafka/event processing."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host:9999/0")
    
    event_id = "evt-unit-test-999"
    assert await mgr.is_event_processed(event_id) is False
    
    # Mark processed
    await mgr.mark_event_processed(event_id, ttl_s=3600)
    assert await mgr.is_event_processed(event_id) is True

@pytest.mark.asyncio
async def test_distributed_locking_single_worker():
    """Verifies acquiring and releasing a distributed lock."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host:9999/0")
    
    resource = "satellite:SAT-007"
    async with mgr.distributed_lock(resource, timeout_s=1.0, lease_s=5.0) as token:
        assert token is not None
        assert isinstance(token, str)
        # Check stats
        stats = mgr.get_stats()
        assert stats["locks_acquired"] >= 1

@pytest.mark.asyncio
async def test_distributed_locking_contention_and_timeout():
    """Verifies that a second worker waiting for an active lock raises DistributedLockError upon timeout."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host:9999/0")
    resource = "satellite:SAT-CONTENDED-01"
    
    lock_holder_running = asyncio.Event()
    worker2_finished = asyncio.Event()
    worker2_failed = False
    
    async def worker_1():
        async with mgr.distributed_lock(resource, timeout_s=1.0, lease_s=10.0):
            lock_holder_running.set()
            # Hold lock for 0.4 seconds
            await asyncio.sleep(0.4)
            
    async def worker_2():
        nonlocal worker2_failed
        await lock_holder_running.wait()
        try:
            # Worker 2 only waits 0.1 seconds, which is less than 0.4s hold time
            async with mgr.distributed_lock(resource, timeout_s=0.1, lease_s=5.0):
                pass
        except DistributedLockError:
            worker2_failed = True
        finally:
            worker2_finished.set()
            
    await asyncio.gather(worker_1(), worker_2())
    await worker2_finished.wait()
    
    assert worker2_failed is True
    stats = mgr.get_stats()
    assert stats["lock_timeouts"] >= 1

@pytest.mark.asyncio
async def test_distributed_locking_sequential_reacquisition():
    """Verifies that once worker 1 releases the lock, worker 2 acquires it without error."""
    mgr = AsyncRedisManager(redis_url="redis://invalid-host:9999/0")
    resource = "satellite:SAT-SEQUENTIAL-02"
    
    acquired_order = []
    
    async def worker(worker_id: int, hold_s: float):
        async with mgr.distributed_lock(resource, timeout_s=2.0, lease_s=5.0):
            acquired_order.append(f"start-{worker_id}")
            await asyncio.sleep(hold_s)
            acquired_order.append(f"end-{worker_id}")
            
    await worker(1, 0.05)
    await worker(2, 0.05)
    
    assert acquired_order == ["start-1", "end-1", "start-2", "end-2"]
