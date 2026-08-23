"""Freshness SLA Compliance Evaluator for ORBIT-X Context Layer.

Evaluates adherence of operational telemetry streams, datasets, and context nodes
to their declared latency and freshness SLAs:
Formula: count(assets within max allowed latency SLA) / total_evaluated_entities
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class FreshnessEvaluationResult(BaseModel):
    metric_name: str = "freshness_sla_compliance"
    score: float = Field(..., ge=0.0, le=1.0)
    score_pct: float = Field(..., ge=0.0, le=100.0)
    total_evaluated_entities: int
    compliant_entities_count: int
    violations_count: int
    details: Dict[str, Any] = Field(default_factory=dict)


def evaluate_freshness(
    datasets: Optional[List[Any]] = None,
    lineage_nodes: Optional[List[Any]] = None,
    max_telemetry_sla_s: float = 15.0,
    max_dataset_sla_s: float = 3600.0,
) -> FreshnessEvaluationResult:
    """Computes freshness SLA compliance score across datasets and context graph nodes."""
    if datasets is None:
        from context.metadata.catalog import SemanticMetadataCatalog
        datasets = SemanticMetadataCatalog().list_datasets()

    if lineage_nodes is None:
        from context.lineage.graph import DataLineageGraph
        dag = DataLineageGraph.trace_decision_lineage("DEC-M-204")
        lineage_nodes = dag.get("nodes", [])

    total_evaluated = 0
    compliant_count = 0
    violations = []

    # 1. Evaluate datasets
    for ds in datasets:
        total_evaluated += 1
        name = getattr(ds, "dataset_name", getattr(ds, "name", "dataset"))
        status = getattr(ds, "status", getattr(ds, "asset_status", "VERIFIED"))
        freshness_s = getattr(ds, "freshness_s", getattr(ds, "freshness_seconds", 0.0))
        
        # Telemetry requires < 15s; other datasets < 3600s; deprecated are non-compliant
        sla_limit = max_telemetry_sla_s if "telemetry" in name.lower() else max_dataset_sla_s
        if status != "DEPRECATED" and freshness_s is not None and freshness_s <= sla_limit:
            compliant_count += 1
        else:
            violations.append(f"Dataset:{name} ({freshness_s}s, status:{status})")

    # 2. Evaluate context graph nodes
    for node in lineage_nodes:
        total_evaluated += 1
        n_id = node.get("node_id") if isinstance(node, dict) else getattr(node, "node_id", getattr(node, "id", "node"))
        status = node.get("status") if isinstance(node, dict) else getattr(node, "status", getattr(node, "asset_status", "VERIFIED"))
        fresh_raw = node.get("freshness") if isinstance(node, dict) else getattr(node, "freshness", "1.0s")
        
        try:
            fresh_val = float(str(fresh_raw).replace("s", "").strip())
        except Exception:
            fresh_val = 1.0

        if status != "DEPRECATED" and fresh_val <= max_dataset_sla_s:
            compliant_count += 1
        else:
            violations.append(f"Node:{n_id} ({fresh_val}s, status:{status})")

    score = round(compliant_count / max(1, total_evaluated), 4)
    return FreshnessEvaluationResult(
        score=score,
        score_pct=round(score * 100.0, 1),
        total_evaluated_entities=total_evaluated,
        compliant_entities_count=compliant_count,
        violations_count=len(violations),
        details={"violations": violations},
    )
