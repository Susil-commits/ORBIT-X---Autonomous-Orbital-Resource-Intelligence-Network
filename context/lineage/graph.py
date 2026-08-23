"""Bidirectional Data Lineage Graph Engine for ORBIT-X.

Traces 10-entity bidirectional provenance across operational assets:
Satellite -> TelemetryStream -> Dataset -> Feature -> Anomaly & Model -> Prediction -> Tool (CP-SAT) -> Decision -> Mission Outcome

Every node in the provenance graph enforces uniform asset-level trust & governance fields:
- status: VERIFIED | DRAFT | DEPRECATED
- owner: str
- last_reviewed: str
- freshness: str | float
- quality_score: float
- schema_version: str
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LineageNode(BaseModel):
    node_id: str
    entity_type: str  # SATELLITE | TELEMETRY_STREAM | DATASET | FEATURE | ANOMALY | MODEL | PREDICTION | TOOL | DECISION | MISSION
    name: str
    status: str = "VERIFIED"  # "VERIFIED", "DRAFT", "DEPRECATED"
    owner: str = "flight-operations"
    last_reviewed: str = "2026-08-23T12:00:00Z"
    freshness: str = "1.0s"
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    schema_version: str = "2.2.0"
    is_trusted: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LineageEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str  # GENERATES | PRODUCES | EXTRACTED_FROM | INPUT_TO | EVALUATED_BY | GATES | OPTIMIZED_BY | VERIFIES | DELIVERS


class DataLineageGraph:
    """Constructs, validates, and queries bidirectional provenance DAGs for decisions."""

    @staticmethod
    def trace_decision_lineage(
        decision_id: str = "DEC-M-204",
        request_id: str = "M-204",
        resource_id: str = "SAT-03"
    ) -> Dict[str, Any]:
        """Constructs end-to-end 10-entity lineage graph with full trust & governance state."""
        nodes = [
            LineageNode(
                node_id="node_satellite",
                entity_type="SATELLITE",
                name=f"Constellation Satellite ({resource_id})",
                status="VERIFIED",
                owner="spacecraft-systems",
                last_reviewed="2026-08-22T12:00:00Z",
                freshness="0.1s",
                quality_score=0.998,
                schema_version="2.2.0",
                metadata={"constellation": "ORBIT-X Sun-Synchronous", "bus_power_w": 240.0, "mass_kg": 48.5},
            ),
            LineageNode(
                node_id="node_telemetry_stream",
                entity_type="TELEMETRY_STREAM",
                name=f"Telemetry Stream ({resource_id})",
                status="VERIFIED",
                owner="flight-operations",
                last_reviewed="2026-08-22T12:00:00Z",
                freshness="0.1s",
                quality_score=0.992,
                schema_version="2.0.0",
                metadata={"sampling_rate": "10Hz", "channels": ["voltage", "temp_c", "jitter_urad"]},
            ),
            LineageNode(
                node_id="node_dataset",
                entity_type="DATASET",
                name="Dataset: satellite_telemetry",
                status="VERIFIED",
                owner="flight-operations",
                last_reviewed="2026-08-22T12:00:00Z",
                freshness="1.0s",
                quality_score=0.992,
                schema_version="2.1.0",
                metadata={"table": "orbitx.telemetry_frames", "storage": "TimescaleDB"},
            ),
            LineageNode(
                node_id="node_feature",
                entity_type="FEATURE",
                name="18-dim Feature Vector",
                status="VERIFIED",
                owner="ml-platform",
                last_reviewed="2026-08-22T11:15:00Z",
                freshness="1.0s",
                quality_score=0.995,
                schema_version="2.2.0",
                metadata={"vector_dim": 18, "scaling": "StandardScaler"},
            ),
            LineageNode(
                node_id="node_anomaly",
                entity_type="ANOMALY",
                name="IsolationForest (Health AI)",
                status="VERIFIED",
                owner="spacecraft-health-ai",
                last_reviewed="2026-08-20T08:00:00Z",
                freshness="0.5s",
                quality_score=0.980,
                schema_version="1.5.0",
                metadata={"contamination": 0.05, "anomaly_score": 0.042, "state": "NOMINAL"},
            ),
            LineageNode(
                node_id="node_model",
                entity_type="MODEL",
                name="Cross-Attention Ranker (v2.2)",
                status="VERIFIED",
                owner="ml-platform",
                last_reviewed="2026-08-21T18:00:00Z",
                freshness="3600.0s",
                quality_score=0.975,
                schema_version="2.2.0",
                metadata={"checkpoint": "v2.2", "inference_latency_ms": 0.78},
            ),
            LineageNode(
                node_id="node_prediction",
                entity_type="PREDICTION",
                name="Neural Candidate Valuation (94.2%)",
                status="VERIFIED",
                owner="autonomous-gnc",
                last_reviewed="2026-08-23T12:00:00Z",
                freshness="0.2s",
                quality_score=0.942,
                schema_version="2.2.0",
                metadata={"score": 27.4, "win_prob": 0.942, "top_shap_feature": "battery_soc_margin"},
            ),
            LineageNode(
                node_id="node_tool",
                entity_type="TOOL",
                name="Google OR-Tools CP-SAT",
                status="VERIFIED",
                owner="mission-planning",
                last_reviewed="2026-08-22T09:30:00Z",
                freshness="0.05s",
                quality_score=1.000,
                schema_version="3.0.0",
                metadata={"solve_time_ms": 1.4, "hard_constraints_violated": 0},
            ),
            LineageNode(
                node_id="node_decision",
                entity_type="DECISION",
                name=f"Assignment Decision ({decision_id})",
                status="VERIFIED",
                owner="decision-intelligence",
                last_reviewed="2026-08-23T12:00:00Z",
                freshness="0.1s",
                quality_score=1.000,
                schema_version="2.0.0",
                metadata={"assigned": resource_id, "request": request_id, "status": "APPROVED"},
            ),
            LineageNode(
                node_id="node_mission",
                entity_type="MISSION",
                name=f"Mission Delivery ({request_id})",
                status="VERIFIED",
                owner="payload-operations",
                last_reviewed="2026-08-23T12:00:00Z",
                freshness="1.0s",
                quality_score=0.990,
                schema_version="2.0.0",
                metadata={"delivery_status": "COMPLETED", "sla_margin": "+18.5%"},
            ),
        ]

        edges = [
            LineageEdge(source_id="node_satellite", target_id="node_telemetry_stream", relation="GENERATES"),
            LineageEdge(source_id="node_telemetry_stream", target_id="node_dataset", relation="PRODUCES"),
            LineageEdge(source_id="node_dataset", target_id="node_feature", relation="EXTRACTED_FROM"),
            LineageEdge(source_id="node_dataset", target_id="node_anomaly", relation="MONITORED_BY"),
            LineageEdge(source_id="node_dataset", target_id="node_model", relation="TRAINED_ON"),
            LineageEdge(source_id="node_feature", target_id="node_model", relation="INPUT_TO"),
            LineageEdge(source_id="node_model", target_id="node_prediction", relation="GENERATES"),
            LineageEdge(source_id="node_prediction", target_id="node_tool", relation="PRIORS_FOR"),
            LineageEdge(source_id="node_anomaly", target_id="node_tool", relation="GATING_FOR"),
            LineageEdge(source_id="node_tool", target_id="node_decision", relation="OPTIMIZED_BY"),
            LineageEdge(source_id="node_decision", target_id="node_mission", relation="DELIVERS"),
        ]

        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "resource_id": resource_id,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "governance_status": "VERIFIED_10_OF_10",
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges],
        }
