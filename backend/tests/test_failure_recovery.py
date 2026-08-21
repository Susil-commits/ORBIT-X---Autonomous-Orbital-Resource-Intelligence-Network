"""Chaos Engineering & Failure Recovery Test Suite for ORBIT-X Distributed Architecture."""

import pytest
import asyncio
import time
from app.core.redis_client import AsyncRedisManager, DistributedLockError
from app.core.kafka_client import AsyncKafkaManager
from app.core.events import (
    TelemetryReceivedEvent,
    AnomalyDetectedEvent,
    EmergencyReplanRequestedEvent,
    TOPIC_TELEMETRY,
    TOPIC_ANOMALIES,
    TOPIC_EMERGENCY,
    TOPIC_DLQ,
)
from app.core.schemas import ScenarioType
from app.simulation.simulator import ConstellationSimulator


@pytest.mark.asyncio
async def test_redis_unavailability_circuit_breaker_and_recovery():
    """Simulates Redis server dropping connection mid-operation and verifies transparent fallback."""
    # 1. Start with invalid host simulating offline/crashed Redis
    crashed_redis = AsyncRedisManager(redis_url="redis://crashed-unreachable-redis-host:6379/0")
    await crashed_redis.connect()
    
    assert crashed_redis.is_connected is False

    # 2. Write telemetry under failure condition -> Should succeed via in-memory circuit breaker
    ok = await crashed_redis.cache_telemetry("SAT-001", {"battery": 78.4, "temp_c": 32.1}, ttl_s=60)
    assert ok is True

    # 3. Read back telemetry -> Must return cached value without raising exception
    cached = await crashed_redis.get_cached_telemetry("SAT-001")
    assert cached is not None
    assert cached["battery"] == 78.4

    # 4. Acquire distributed lock under failure condition -> Must use local asyncio lock table
    acquired = False
    async with crashed_redis.distributed_lock("satellite:SAT-001", timeout_s=1.0) as token:
        assert token is not None
        acquired = True
    assert acquired is True


@pytest.mark.asyncio
async def test_kafka_broker_offline_buffer_resilience():
    """Simulates Kafka cluster dropping offline and verifies zero message drop via local event bus."""
    crashed_kafka = AsyncKafkaManager(bootstrap_servers="unreachable-kafka-broker:9092")
    await crashed_kafka.start()
    
    assert crashed_kafka.is_connected is False

    received_telemetry = []

    async def telemetry_consumer(event: TelemetryReceivedEvent):
        received_telemetry.append(event)

    crashed_kafka.register_handler(TOPIC_TELEMETRY, telemetry_consumer, auto_idempotency=False)

    # Dispatch 10 telemetry events during Kafka outage
    for i in range(10):
        evt = TelemetryReceivedEvent(
            satellite_id=f"SAT-{i:03d}",
            payload={"battery_soc": 0.85, "step": i},
        )
        await crashed_kafka.publish(TOPIC_TELEMETRY, evt)

    await asyncio.sleep(0.2)

    # All 10 events must be delivered reliably via in-memory bus buffer
    assert len(received_telemetry) == 10
    stats = crashed_kafka.get_stats()
    assert stats["messages_published"] >= 10
    assert stats["messages_consumed"] >= 10


@pytest.mark.asyncio
async def test_emergency_cascade_recovery():
    """Simulates a space weather solar storm anomaly triggering an automated emergency replan."""
    kafka = AsyncKafkaManager()
    await kafka.start()

    replan_events = []

    async def emergency_replan_consumer(event: EmergencyReplanRequestedEvent):
        replan_events.append(event)

    kafka.register_handler(TOPIC_EMERGENCY, emergency_replan_consumer, auto_idempotency=True)

    sim = ConstellationSimulator()
    # Trigger solar storm scenario
    sim.trigger_scenario(ScenarioType.SOLAR_STORM)
    assert sim.active_scenario.is_active is True
    assert sim.active_scenario.scenario_type == ScenarioType.SOLAR_STORM

    # Publish AnomalyDetected event
    anomaly_event = AnomalyDetectedEvent(
        satellite_id="SAT-001",
        payload={"scenario": "SOLAR_STORM", "severity": "CRITICAL"},
    )
    await kafka.publish(TOPIC_ANOMALIES, anomaly_event)

    # Trigger emergency replan event
    replan_req = EmergencyReplanRequestedEvent(
        mission_id="M-EMERGENCY-CASCADE-01",
        satellite_id="SAT-001",
        payload={"trigger": "SOLAR_STORM", "action": "SAFE_MODE_AVOIDANCE"},
    )
    await kafka.publish(TOPIC_EMERGENCY, replan_req)

    await asyncio.sleep(0.2)

    assert len(replan_events) == 1
    assert replan_events[0].payload["trigger"] == "SOLAR_STORM"
