"""Semantic Dataset Registry and Metadata Catalog.

Maintains formal metadata records for operational telemetry, datasets,
features, schemas, freshness SLAs, quality scores, and downstream ML models.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DatasetMetadataRecord(BaseModel):
    """Metadata specification for operational and ML datasets."""
    dataset_name: str
    description: str
    owner: str = "Platform Engineering"
    schema_version: str = "2.1.0"
    freshness_s: float
    quality_score: float = Field(default=0.98, ge=0.0, le=1.0)
    record_count: int
    columns: List[Dict[str, str]]
    downstream_models: List[str]
    upstream_sources: List[str]


class SemanticMetadataCatalog:
    """In-memory catalog of all system datasets and schemas."""

    def __init__(self):
        self._catalog: Dict[str, DatasetMetadataRecord] = {}
        self._initialize_catalog()

    def _initialize_catalog(self):
        self.register_dataset(
            DatasetMetadataRecord(
                dataset_name="satellite_telemetry",
                description="High-frequency multivariate satellite sensor streams including battery SOC, bus voltage, temperature, and link quality.",
                owner="Telemetry & Ground Ops",
                schema_version="2.1.0",
                freshness_s=8.0,
                quality_score=0.99,
                record_count=145200,
                columns=[
                    {"name": "resource_id", "type": "string", "desc": "Satellite identifier"},
                    {"name": "battery_soc", "type": "float", "desc": "State of charge [0.0 - 1.0]"},
                    {"name": "battery_temp_c", "type": "float", "desc": "Battery cell temperature"},
                    {"name": "bus_voltage_v", "type": "float", "desc": "Primary bus voltage"},
                    {"name": "comm_latency_ms", "type": "float", "desc": "Uplink latency"},
                    {"name": "link_snr_db", "type": "float", "desc": "Signal to noise ratio"},
                ],
                downstream_models=["IsolationForestAnomalyDetector", "CrossAttentionRanker", "BidValueMLP"],
                upstream_sources=["SGP4_Simulator", "OBC_Sensors"],
            )
        )
        self.register_dataset(
            DatasetMetadataRecord(
                dataset_name="mission_requests",
                description="Priority Earth Observation and disaster response task requirements, geo-coordinates, and execution deadlines.",
                owner="Mission Planning",
                schema_version="2.0.0",
                freshness_s=45.0,
                quality_score=0.98,
                record_count=1820,
                columns=[
                    {"name": "request_id", "type": "string", "desc": "Task identifier"},
                    {"name": "priority", "type": "integer", "desc": "Priority tier (1 to 5)"},
                    {"name": "target_lat", "type": "float", "desc": "Target Latitude"},
                    {"name": "target_lon", "type": "float", "desc": "Target Longitude"},
                    {"name": "deadline_epoch_s", "type": "float", "desc": "Execution deadline"},
                ],
                downstream_models=["CrossAttentionRanker", "CP_SAT_Optimizer"],
                upstream_sources=["Customer_Portal", "Disaster_Relief_API"],
            )
        )
        self.register_dataset(
            DatasetMetadataRecord(
                dataset_name="decision_audit_log",
                description="Immutable log of all CP-SAT allocation decisions, candidate scores, SHAP explanations, and human approvals.",
                owner="Governance & Compliance",
                schema_version="1.4.0",
                freshness_s=2.0,
                quality_score=1.0,
                record_count=8940,
                columns=[
                    {"name": "decision_id", "type": "string", "desc": "Unique decision trace ID"},
                    {"name": "assigned_resource_id", "type": "string", "desc": "Assigned satellite"},
                    {"name": "solver_time_ms", "type": "float", "desc": "CP-SAT execution time"},
                    {"name": "hard_constraints_satisfied", "type": "boolean", "desc": "Safety verification"},
                ],
                downstream_models=["FeedbackLoopEvaluator", "TrustLayerEngine"],
                upstream_sources=["CP_SAT_Solver", "HumanOperatorConsole"],
            )
        )

    def register_dataset(self, record: DatasetMetadataRecord):
        self._catalog[record.dataset_name] = record

    def get_dataset(self, name: str) -> Optional[DatasetMetadataRecord]:
        return self._catalog.get(name)

    def list_datasets(self) -> List[DatasetMetadataRecord]:
        return list(self._catalog.values())
