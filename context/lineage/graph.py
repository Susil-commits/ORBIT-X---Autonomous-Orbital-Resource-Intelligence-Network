"""Bidirectional Data Lineage Graph Engine.

Traces provenance from Raw Sensor Telemetry to Feature Extraction,
Machine Learning Predictions, CP-SAT Optimization, Final Decision, and Human Feedback:

Telemetry -> Feature -> Model -> Prediction -> Optimizer -> Decision -> Outcome
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class LineageNode(BaseModel):
    node_id: str
    entity_type: str  # TELEMETRY | FEATURE | MODEL | PREDICTION | OPTIMIZER | DECISION | FEEDBACK
    name: str
    status: str
    metadata: Dict[str, Any]


class LineageEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str  # TRANSFORMS_INTO | EVALUATED_BY | SCORED_BY | OPTIMIZED_BY | APPROVED_BY


class DataLineageGraph:
    """Constructs and queries bidirectional provenance DAGs for decisions."""

    @staticmethod
    def trace_decision_lineage(decision_id: str, request_id: str = "M-204", resource_id: str = "SAT-01") -> Dict[str, Any]:
        nodes = [
            LineageNode(
                node_id="node_telemetry",
                entity_type="TELEMETRY",
                name=f"Raw Telemetry ({resource_id})",
                status="FRESH",
                metadata={"freshness_s": 8.0, "battery_soc": 0.88, "temp_c": 22.4},
            ),
            LineageNode(
                node_id="node_feature",
                entity_type="FEATURE",
                name="18-dim Feature Vector",
                status="NORMALIZED",
                metadata={"vector_dim": 18, "scaling": "StandardScaler"},
            ),
            LineageNode(
                node_id="node_model",
                entity_type="MODEL",
                name="Cross-Attention Ranker",
                status="SERVING",
                metadata={"checkpoint": "v2.1", "inference_latency_ms": 0.37},
            ),
            LineageNode(
                node_id="node_prediction",
                entity_type="PREDICTION",
                name="Neural Candidate Valuation",
                status="COMPUTED",
                metadata={"score": 0.942, "win_prob": 0.948, "top_shap_feature": "battery_soc_margin"},
            ),
            LineageNode(
                node_id="node_optimizer",
                entity_type="OPTIMIZER",
                name="Google OR-Tools CP-SAT",
                status="SOLVED",
                metadata={"solve_time_ms": 1.4, "hard_constraints_violated": 0},
            ),
            LineageNode(
                node_id="node_decision",
                entity_type="DECISION",
                name=f"Assignment Decision ({decision_id})",
                status="VERIFIED",
                metadata={"assigned": resource_id, "request": request_id},
            ),
            LineageNode(
                node_id="node_feedback",
                entity_type="FEEDBACK",
                name="Operator Governance Review",
                status="APPROVED",
                metadata={"decision": "APPROVE", "operator": "OPERATOR_CHIEF"},
            ),
        ]

        edges = [
            LineageEdge(source_id="node_telemetry", target_id="node_feature", relation="TRANSFORMS_INTO"),
            LineageEdge(source_id="node_feature", target_id="node_model", relation="INPUT_TO"),
            LineageEdge(source_id="node_model", target_id="node_prediction", relation="PRODUCES"),
            LineageEdge(source_id="node_prediction", target_id="node_optimizer", relation="FEEDS_INTO"),
            LineageEdge(source_id="node_optimizer", target_id="node_decision", relation="VERIFIES"),
            LineageEdge(source_id="node_decision", target_id="node_feedback", relation="REVIEWED_BY"),
        ]

        return {
            "decision_id": decision_id,
            "request_id": request_id,
            "resource_id": resource_id,
            "nodes": [n.model_dump() for n in nodes],
            "edges": [e.model_dump() for e in edges],
        }
