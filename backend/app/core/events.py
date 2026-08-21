"""Standardized Event Schemas and Topics for ORBIT-X Event-Driven Architecture."""

import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# ----------------------------------------------------
# Kafka Topic Constants
# ----------------------------------------------------
TOPIC_TELEMETRY = "orbit.telemetry"
TOPIC_MISSIONS = "orbit.missions"
TOPIC_HEALTH = "orbit.health"
TOPIC_ANOMALIES = "orbit.anomalies"
TOPIC_EMERGENCY = "orbit.emergency"
TOPIC_SCHEDULER = "orbit.scheduler"
TOPIC_COMPLETED = "orbit.completed"
TOPIC_DLQ = "orbit.dlq"

ALL_TOPICS = [
    TOPIC_TELEMETRY,
    TOPIC_MISSIONS,
    TOPIC_HEALTH,
    TOPIC_ANOMALIES,
    TOPIC_EMERGENCY,
    TOPIC_SCHEDULER,
    TOPIC_COMPLETED,
    TOPIC_DLQ,
]


class BaseOrbitEvent(BaseModel):
    """Canonical event payload conforming to production distributed schema standards."""
    event_id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    event_type: str
    timestamp: float = Field(default_factory=lambda: round(time.time(), 3))
    source: str = "orbitx-core"
    version: int = 1
    satellite_id: Optional[str] = None
    mission_id: Optional[str] = None
    correlation_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)

    def to_kafka_key(self) -> str:
        """Returns partition routing key (satellite_id or mission_id or event_id)."""
        return self.satellite_id or self.mission_id or self.event_id


class MissionCreatedEvent(BaseOrbitEvent):
    """Fired when a new mission request is submitted into the intake pipeline."""
    event_type: str = "MISSION_CREATED"
    source: str = "mission-api"


class TelemetryReceivedEvent(BaseOrbitEvent):
    """Fired when real-time satellite telemetry is ingested."""
    event_type: str = "TELEMETRY_RECEIVED"
    source: str = "telemetry-service"


class AnomalyDetectedEvent(BaseOrbitEvent):
    """Fired when the Health AI model detects a subsystem or orbital anomaly."""
    event_type: str = "ANOMALY_DETECTED"
    source: str = "anomaly-service"


class EmergencyReplanRequestedEvent(BaseOrbitEvent):
    """Fired when an anomaly triggers an immediate dynamic constellation replan."""
    event_type: str = "EMERGENCY_REPLAN_REQUESTED"
    source: str = "emergency-director"


class MissionScheduledEvent(BaseOrbitEvent):
    """Fired when CP-SAT solver completes constellation assignment."""
    event_type: str = "MISSION_SCHEDULED"
    source: str = "scheduler-service"


class MissionCompletedEvent(BaseOrbitEvent):
    """Fired when a satellite completes observation and downlink."""
    event_type: str = "MISSION_COMPLETED"
    source: str = "execution-service"


class DeadLetterEvent(BaseOrbitEvent):
    """Fired when an event fails all retry attempts and is routed to DLQ."""
    event_type: str = "DEAD_LETTER_EVENT"
    source: str = "dlq-router"
    original_topic: Optional[str] = None
    error_message: Optional[str] = None
    failed_attempts: int = 0
