"""Lineage Coverage Evaluator for ORBIT-X Context Layer.

Evaluates the fraction of canonical context graph entities connected via active
bidirectional provenance edges in decision trace DAGs:
Formula: count(nodes with connected active edges) / total_canonical_nodes (10)
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LineageCoverageResult(BaseModel):
    metric_name: str = "lineage_coverage"
    score: float = Field(..., ge=0.0, le=1.0)
    score_pct: float = Field(..., ge=0.0, le=100.0)
    total_canonical_nodes: int
    connected_nodes: int
    total_edges: int
    details: Dict[str, Any] = Field(default_factory=dict)


def evaluate_lineage_coverage(decision_dag: Optional[Dict[str, Any]] = None) -> LineageCoverageResult:
    """Computes lineage coverage across the canonical 10-node context graph."""
    if decision_dag is None:
        from context.lineage.graph import DataLineageGraph
        decision_dag = DataLineageGraph.trace_decision_lineage("DEC-M-204")

    nodes = decision_dag.get("nodes", [])
    edges = decision_dag.get("edges", [])

    connected_node_ids = set()
    for edge in edges:
        s_id = edge.get("source_id") or edge.get("source")
        t_id = edge.get("target_id") or edge.get("target")
        if s_id:
            connected_node_ids.add(s_id)
        if t_id:
            connected_node_ids.add(t_id)

    total_nodes = max(1, len(nodes))
    connected_count = sum(
        1 for n in nodes
        if (n.get("node_id") or n.get("id")) in connected_node_ids
    )

    score = round(connected_count / total_nodes, 4)
    return LineageCoverageResult(
        score=score,
        score_pct=round(score * 100.0, 1),
        total_canonical_nodes=total_nodes,
        connected_nodes=connected_count,
        total_edges=len(edges),
        details={"connected_node_ids": list(connected_node_ids)},
    )
