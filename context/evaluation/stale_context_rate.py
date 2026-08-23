"""Stale Context Rate Evaluator for ORBIT-X Context Layer.

Evaluates the rate of stale, deprecated, or out-of-SLA context entities
across the system to protect autonomous agents from corrupted decision priors:
Formula: (deprecated_assets + stale_sla_violations) / total_evaluated_entities
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StaleContextRateResult(BaseModel):
    metric_name: str = "stale_context_rate"
    rate: float = Field(..., ge=0.0, le=1.0)
    rate_pct: float = Field(..., ge=0.0, le=100.0)
    total_evaluated_entities: int
    stale_entities_count: int
    stale_entities: List[str] = Field(default_factory=list)


def evaluate_stale_context_rate(
    datasets: Optional[List[Any]] = None,
    lineage_nodes: Optional[List[Any]] = None,
    max_freshness_threshold_s: float = 86400.0,
) -> StaleContextRateResult:
    """Computes the empirical rate of stale or deprecated context assets."""
    if datasets is None:
        from context.metadata.catalog import SemanticMetadataCatalog
        datasets = SemanticMetadataCatalog().list_datasets()

    if lineage_nodes is None:
        from context.lineage.graph import DataLineageGraph
        dag = DataLineageGraph.trace_decision_lineage("DEC-M-204")
        lineage_nodes = dag.get("nodes", [])

    stale_list = []
    total_count = len(datasets) + len(lineage_nodes)

    for ds in datasets:
        name = getattr(ds, "dataset_name", getattr(ds, "name", "dataset"))
        status = getattr(ds, "status", getattr(ds, "asset_status", "VERIFIED"))
        freshness_s = getattr(ds, "freshness_s", getattr(ds, "freshness_seconds", 0.0))

        if status == "DEPRECATED" or (freshness_s is not None and freshness_s > max_freshness_threshold_s):
            stale_list.append(f"Dataset:{name} ({status}, {freshness_s}s)")

    for node in lineage_nodes:
        n_id = node.get("node_id") if isinstance(node, dict) else getattr(node, "node_id", getattr(node, "id", "node"))
        status = node.get("status") if isinstance(node, dict) else getattr(node, "status", getattr(node, "asset_status", "VERIFIED"))
        fresh_raw = node.get("freshness") if isinstance(node, dict) else getattr(node, "freshness", "1.0s")
        
        try:
            fresh_val = float(str(fresh_raw).replace("s", "").strip())
        except Exception:
            fresh_val = 1.0

        if status == "DEPRECATED" or fresh_val > max_freshness_threshold_s:
            stale_list.append(f"Node:{n_id} ({status}, {fresh_val}s)")

    rate = round(len(stale_list) / max(1, total_count), 4)
    return StaleContextRateResult(
        rate=rate,
        rate_pct=round(rate * 100.0, 1),
        total_evaluated_entities=total_count,
        stale_entities_count=len(stale_list),
        stale_entities=stale_list,
    )
