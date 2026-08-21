"""Comprehensive test suite for Kafka Event Backbone, Idempotency, and DLQ."""

import pytest
import asyncio
import time
from app.core.events import (
    MissionCreatedEvent,
    TelemetryReceivedEvent,
    AnomalyDetectedEvent,
    EmergencyReplanRequestedEvent,
    DeadLetterEvent,
    TOPIC_MISSIONS,
    TOPIC_TELEMETRY,
    TOPIC_ANOMALIES,
    TOPIC_EMERGENCY,
    TOPIC_DLQ,
)
from app.core.kafka_client import AsyncKafkaManager
from app.core.redis_client import AsyncRedisManager


@pytest.mark.asyncio
async def test_event_schemas_and_keys():
    """Validates that event models correctly construct standard metadata and partition keys."""
    evt = MissionCreatedEvent(
        mission_id="M-888",
        satellite_id="SAT-003",
        payload={"target": "Amazon Basin", "priority": 5},
    )
    assert evt.event_type == "MISSION_CREATED"
    assert evt.event_id.startswith("evt-")
    assert evt.to_kafka_key() == "SAT-003"
    assert evt.payload["priority"] == 5


@pytest.mark.asyncio
async def test_kafka_publish_and_consume():
    """Verifies end-to-end publishing and asynchronous consumption of domain events."""
    kafka = AsyncKafkaManager()
    await kafka.start()
    
    received_events = []
    
    async def on_mission_created(event: MissionCreatedEvent):
        received_events.append(event)
        
    kafka.register_handler(TOPIC_MISSIONS, on_mission_created, auto_idempotency=False)
    
    event = MissionCreatedEvent(mission_id="M-TEST-100", payload={"req_id": 100})
    await kafka.publish(TOPIC_MISSIONS, event)
    
    # Allow async loop to process event
    await asyncio.sleep(0.1)
    
    assert len(received_events) == 1
    assert received_events[0].mission_id == "M-TEST-100"
    
    stats = kafka.get_stats()
    assert stats["messages_published"] >= 1
    assert stats["messages_consumed"] >= 1


@pytest.mark.asyncio
async def test_kafka_idempotency_duplicate_suppression():
    """Verifies that re-delivering the exact same event_id is safely suppressed."""
    kafka = AsyncKafkaManager()
    await kafka.start()
    
    call_count = 0
    
    async def idempotency_handler(event: TelemetryReceivedEvent):
        nonlocal call_count
        call_count += 1
        
    kafka.register_handler(TOPIC_TELEMETRY, idempotency_handler, auto_idempotency=True)
    
    event = TelemetryReceivedEvent(
        event_id="evt-fixed-id-12345",
        satellite_id="SAT-009",
        payload={"battery": 88.0},
    )
    
    # Publish 1st time
    await kafka.publish(TOPIC_TELEMETRY, event)
    await asyncio.sleep(0.1)
    assert call_count == 1
    
    # Publish duplicate 2nd time
    await kafka.publish(TOPIC_TELEMETRY, event)
    await asyncio.sleep(0.1)
    assert call_count == 1  # Still 1 because duplicate was suppressed!
    
    stats = kafka.get_stats()
    assert stats["duplicates_skipped"] >= 1


@pytest.mark.asyncio
async def test_kafka_consumer_retry_and_recovery():
    """Verifies that transient errors trigger exponential backoff retries and succeed."""
    kafka = AsyncKafkaManager()
    await kafka.start()
    
    attempts = 0
    
    async def flaky_handler(event: AnomalyDetectedEvent):
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ConnectionError("Temporary glitch")
            
    kafka.register_handler(TOPIC_ANOMALIES, flaky_handler, auto_idempotency=False, max_retries=3)
    
    event = AnomalyDetectedEvent(satellite_id="SAT-FLAKY-01", payload={"anomaly": "THERMAL"})
    await kafka.publish(TOPIC_ANOMALIES, event)
    
    await asyncio.sleep(0.3)
    
    # Attempt 1 failed, Attempt 2 succeeded
    assert attempts == 2
    stats = kafka.get_stats()
    assert stats["retries_attempted"] >= 1
    assert stats["messages_consumed"] >= 1


@pytest.mark.asyncio
async def test_kafka_dlq_routing_on_unrecoverable_failure():
    """Verifies that when all retries fail, the event is automatically routed to orbit.dlq."""
    kafka = AsyncKafkaManager()
    await kafka.start()
    
    dlq_received = []
    
    async def failing_handler(event: EmergencyReplanRequestedEvent):
        raise ValueError("Permanent processing fault")
        
    async def dlq_handler(event: DeadLetterEvent):
        dlq_received.append(event)
        
    kafka.register_handler(TOPIC_EMERGENCY, failing_handler, auto_idempotency=False, max_retries=2)
    kafka.register_handler(TOPIC_DLQ, dlq_handler, auto_idempotency=False)
    
    event = EmergencyReplanRequestedEvent(
        mission_id="M-CRITICAL-ERR",
        payload={"reason": "SOLAR_STORM"},
    )
    await kafka.publish(TOPIC_EMERGENCY, event)
    
    await asyncio.sleep(0.4)
    
    assert len(dlq_received) == 1
    assert dlq_received[0].original_topic == TOPIC_EMERGENCY
    assert dlq_received[0].failed_attempts >= 2
    assert "Permanent processing fault" in dlq_received[0].error_message
    
    stats = kafka.get_stats()
    assert stats["dlq_routed"] >= 1
