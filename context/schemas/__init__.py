"""ORBIT-X Context Schemas & Governance Asset Specifications.

Defines formal Pydantic v2 schemas for the 10 canonical context graph entities:
1. Dataset
2. Mission
3. Satellite
4. TelemetryStream
5. Feature
6. Model
7. Prediction
8. Anomaly
9. Decision
10. Tool

Every context entity enforces uniform asset-level trust & governance metadata:
- status: VERIFIED | DRAFT | DEPRECATED
- owner: str
- last_reviewed: str (ISO-8601 timestamp)
- freshness: str | float (e.g. "0.1s" or 0.1)
- quality_score: float [0.0, 1.0]
- schema_version: str (e.g. "2.2.0")
- bidirectional provenance links (upstream_sources, downstream_consumers)
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class AssetStatus(str, Enum):
    """Authoritative asset certification lifecycle status."""
    VERIFIED = "VERIFIED"
    DRAFT = "DRAFT"
    DEPRECATED = "DEPRECATED"


class GovernedAsset(BaseModel):
    """Base schema for all context-layer assets with trust and governance metadata."""
    entity_id: str
    name: str
    description: str
    status: AssetStatus = AssetStatus.VERIFIED
    owner: str = Field(default="flight-operations", description="Owning team or system")
    last_reviewed: str = Field(default="2026-08-23T12:00:00Z", description="ISO-8601 review timestamp")
    freshness: Union[str, float] = Field(default="1.0s", description="Freshness SLA latency string or seconds")
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Quality/confidence score [0.0, 1.0]")
    schema_version: str = Field(default="2.2.0", description="Semantic contract version")
    is_trusted: bool = Field(default=True, description="Evaluated trust compliance state")
    governance_policy: Optional[str] = Field(
        default="Production agent decisions require VERIFIED assets only.",
        description="Applied governance policy rule"
    )
    upstream_sources: List[str] = Field(default_factory=list, description="Bidirectional lineage upstream node IDs")
    downstream_consumers: List[str] = Field(default_factory=list, description="Bidirectional lineage downstream node IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific metadata payload")


# Backward compatibility alias
ContextEntity = GovernedAsset


# -------------------------------------------------------------
# 1. Dataset Asset Schema
# -------------------------------------------------------------
class DatasetAsset(GovernedAsset):
    """Canonical Dataset context entity."""
    entity_type: str = "DATASET"
    storage_format: str = "TimescaleDB / Parquet"
    record_count: int = 0
    columns: List[Dict[str, str]] = Field(default_factory=list)


# -------------------------------------------------------------
# 2. Mission Asset Schema
# -------------------------------------------------------------
class MissionAsset(GovernedAsset):
    """Canonical Mission context entity."""
    entity_type: str = "MISSION"
    priority: int = Field(default=3, ge=1, le=5)
    target_lat: float = 0.0
    target_lon: float = 0.0
    deadline_epoch_s: float = 0.0
    required_sensor: str = "OPTICAL_RGB"


# -------------------------------------------------------------
# 3. Satellite Asset Schema
# -------------------------------------------------------------
class SatelliteAsset(GovernedAsset):
    """Canonical Satellite context entity."""
    entity_type: str = "SATELLITE"
    norad_id: Optional[int] = None
    orbit_plane: int = 1
    battery_capacity_wh: float = 800.0
    bus_voltage_v: float = 28.0
    mass_kg: float = 48.5


# -------------------------------------------------------------
# 4. TelemetryStream Asset Schema
# -------------------------------------------------------------
class TelemetryStreamAsset(GovernedAsset):
    """Canonical Telemetry Stream context entity."""
    entity_type: str = "TELEMETRY_STREAM"
    sampling_rate_hz: float = 10.0
    channel_count: int = 6
    stream_topic: str = "orbitx.telemetry.primary"


# -------------------------------------------------------------
# 5. Feature Asset Schema
# -------------------------------------------------------------
class FeatureAsset(GovernedAsset):
    """Canonical Feature Table / Feature Vector context entity."""
    entity_type: str = "FEATURE"
    vector_dimension: int = 18
    scaling_method: str = "StandardScaler"
    feature_names: List[str] = Field(default_factory=list)


# -------------------------------------------------------------
# 6. Model Asset Schema
# -------------------------------------------------------------
class ModelAsset(GovernedAsset):
    """Canonical Machine Learning Model context entity."""
    entity_type: str = "MODEL"
    architecture: str = "MultiHeadCrossAttention"
    checkpoint_version: str = "v2.2"
    f1_score: float = 0.94
    inference_latency_ms: float = 0.78


# -------------------------------------------------------------
# 7. Prediction Asset Schema
# -------------------------------------------------------------
class PredictionAsset(GovernedAsset):
    """Canonical Model Prediction context entity."""
    entity_type: str = "PREDICTION"
    win_probability: float = 0.942
    bid_valuation_score: float = 27.4
    shap_primary_attribution: str = "battery_soc_margin"


# -------------------------------------------------------------
# 8. Anomaly Asset Schema
# -------------------------------------------------------------
class AnomalyAsset(GovernedAsset):
    """Canonical Anomaly Detection context entity."""
    entity_type: str = "ANOMALY"
    anomaly_score: float = 0.042
    detector_type: str = "IsolationForest"
    is_fault: bool = False
    gating_action: str = "ALLOW_DISPATCH"


# -------------------------------------------------------------
# 9. Decision Asset Schema
# -------------------------------------------------------------
class DecisionAsset(GovernedAsset):
    """Canonical Decision Record context entity."""
    entity_type: str = "DECISION"
    assigned_satellite_id: str = "SAT-03"
    mission_id: str = "M-204"
    solver_status: str = "OPTIMAL"
    hard_constraints_satisfied: bool = True
    approval_state: str = "APPROVED"


# -------------------------------------------------------------
# 10. Tool Asset Schema
# -------------------------------------------------------------
class ToolAsset(GovernedAsset):
    """Canonical Tool / Solver / MCP Agent Tool context entity."""
    entity_type: str = "TOOL"
    tool_name: str = "Google_OR_Tools_CP_SAT"
    mcp_protocol_version: str = "2024-11-05"
    deterministic_guarantee: bool = True
    execution_timeout_ms: float = 100.0


# Direct exports for all 10 context entity types
Dataset = DatasetAsset
Mission = MissionAsset
Satellite = SatelliteAsset
TelemetryStream = TelemetryStreamAsset
Feature = FeatureAsset
Model = ModelAsset
Prediction = PredictionAsset
Anomaly = AnomalyAsset
Decision = DecisionAsset
Tool = ToolAsset

__all__ = [
    "AssetStatus",
    "GovernedAsset",
    "ContextEntity",
    "DatasetAsset",
    "MissionAsset",
    "SatelliteAsset",
    "TelemetryStreamAsset",
    "FeatureAsset",
    "ModelAsset",
    "PredictionAsset",
    "AnomalyAsset",
    "DecisionAsset",
    "ToolAsset",
    # 10 Canonical Short Names
    "Dataset",
    "Mission",
    "Satellite",
    "TelemetryStream",
    "Feature",
    "Model",
    "Prediction",
    "Anomaly",
    "Decision",
    "Tool",
]
