"""Explicit Data Schemas for the ORBIT-X AI-Native Data Platform.

Defines Pydantic v2 data models for Telemetry, MissionRequest, OperationalState,
Anomaly, Prediction, Decision, and Human Feedback records.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class Telemetry(BaseModel):
    """Raw and validated telemetry frame from operational resources."""
    model_config = ConfigDict(extra="ignore")

    resource_id: str = Field(..., description="Unique resource identifier (e.g. SAT-01)")
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    battery_soc: float = Field(..., ge=0.0, le=1.0, description="Battery State of Charge [0.0 - 1.0]")
    bus_voltage_v: float = Field(default=28.0, description="Main bus voltage in Volts")
    battery_temp_c: float = Field(default=22.0, description="Internal battery temperature in Celsius")
    panel_current_a: float = Field(default=12.5, description="Solar array generated current in Amps")
    comm_latency_ms: float = Field(default=45.0, description="Uplink/downlink latency in ms")
    link_snr_db: float = Field(default=18.5, description="Signal to Noise Ratio in dB")
    memory_util_pct: float = Field(default=35.0, ge=0.0, le=100.0, description="On-board memory utilization %")
    is_sunlit: bool = Field(default=True, description="Whether resource is in solar illumination")
    raw_packet_id: Optional[str] = None


class MissionRequest(BaseModel):
    """Operational incoming request / task requirement."""
    model_config = ConfigDict(extra="ignore")

    request_id: str = Field(..., description="Unique task identifier (e.g. M-204)")
    priority: int = Field(..., ge=1, le=5, description="Priority scale: 1 (Routine) to 5 (Critical)")
    target_lat: float = Field(..., ge=-90.0, le=90.0, description="Target Latitude")
    target_lon: float = Field(..., ge=-180.0, le=180.0, description="Target Longitude")
    duration_s: float = Field(default=120.0, gt=0, description="Required payload execution duration in seconds")
    min_elevation_deg: float = Field(default=15.0, ge=0.0, le=90.0, description="Minimum line-of-sight elevation")
    deadline_epoch_s: float = Field(..., description="Strict execution deadline timestamp")
    min_energy_pct: float = Field(default=0.20, description="Minimum reserve energy required")
    created_at: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class OperationalState(BaseModel):
    """Normalized snapshot of operational system state."""
    model_config = ConfigDict(extra="ignore")

    state_id: str
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    active_resource_count: int
    pending_request_count: int
    system_health_score: float = Field(default=1.0, ge=0.0, le=1.0)
    active_anomalies_count: int = 0
    telemetry_freshness_s: float = 0.0


class Anomaly(BaseModel):
    """Detected operational anomaly record."""
    model_config = ConfigDict(extra="ignore")

    anomaly_id: str
    resource_id: str
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
    anomaly_score: float = Field(..., description="Isolation Forest anomaly score (-1.0 to 1.0)")
    is_anomaly: bool = Field(..., description="True if anomaly threshold exceeded")
    severity: str = Field(default="LOW", description="LOW | MEDIUM | HIGH | CRITICAL")
    contributing_sensors: List[str] = Field(default_factory=list)
    mitigation_action: Optional[str] = None


class Prediction(BaseModel):
    """Machine learning candidate valuation and ranking prediction."""
    model_config = ConfigDict(extra="ignore")

    prediction_id: str
    model_name: str = "CrossAttentionRanker"
    model_version: str = "v2.1"
    request_id: str
    resource_id: str
    ranking_score: float = Field(..., description="Neural match valuation [0.0 - 1.0]")
    win_probability: float = Field(..., ge=0.0, le=1.0)
    inference_latency_ms: float
    feature_contributions: Dict[str, float] = Field(default_factory=dict)
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class Decision(BaseModel):
    """Constraint-verified assignment and scheduling decision."""
    model_config = ConfigDict(extra="ignore")

    decision_id: str
    request_id: str
    assigned_resource_id: str
    solver_name: str = "Google_OR_Tools_CP_SAT"
    solve_time_ms: float
    hard_constraints_satisfied: bool = True
    objective_value: float
    reason: str
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())


class Feedback(BaseModel):
    """Human-in-the-loop operator review and evaluation feedback."""
    model_config = ConfigDict(extra="ignore")

    feedback_id: str
    decision_id: str
    human_decision: str = Field(..., description="APPROVE | REJECT | INVESTIGATE")
    operator_id: str = "OPERATOR_CHIEF"
    operator_notes: str
    model_version: str
    agent_version: str = "AgentLoop-v2.0"
    actual_outcome: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: datetime.now(timezone.utc).timestamp())
