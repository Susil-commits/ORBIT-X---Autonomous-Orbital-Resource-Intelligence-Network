"""ORBIT-X Context Evaluation Package.

Provides deterministic, empirical measurement across the 5 authoritative Context Quality dimensions:
1. metadata_completeness: Ratio of populated required schema/governance attributes.
2. lineage_coverage: Fraction of tracked context graph entities with active provenance DAG links.
3. freshness: Ratio of assets satisfying real-time latency and freshness SLA compliance.
4. retrieval_groundedness: Proportion of query retrieval items matching verified ground truth schemas.
5. stale_context_rate: Ratio of assets exceeding freshness SLAs or flagged DEPRECATED/stale.
"""

from typing import Dict, Any, Optional
import datetime
from pydantic import BaseModel, Field

from context.evaluation.metadata_completeness import (
    evaluate_metadata_completeness,
    MetadataCompletenessResult,
)
from context.evaluation.lineage_coverage import (
    evaluate_lineage_coverage,
    LineageCoverageResult,
)
from context.evaluation.freshness import (
    evaluate_freshness,
    FreshnessEvaluationResult,
)
from context.evaluation.retrieval_groundedness import (
    evaluate_retrieval_groundedness,
    RetrievalGroundednessResult,
)
from context.evaluation.stale_context_rate import (
    evaluate_stale_context_rate,
    StaleContextRateResult,
)


class ComprehensiveContextEvaluationReport(BaseModel):
    """Aggregated report spanning all 5 context evaluation dimensions."""
    metadata_completeness: MetadataCompletenessResult
    lineage_coverage: LineageCoverageResult
    freshness: FreshnessEvaluationResult
    retrieval_groundedness: RetrievalGroundednessResult
    stale_context_rate: StaleContextRateResult
    composite_quality_score: float = Field(..., ge=0.0, le=1.0)
    composite_quality_score_pct: float = Field(..., ge=0.0, le=100.0)
    evaluated_at_iso: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


def evaluate_all_context_metrics() -> ComprehensiveContextEvaluationReport:
    """Executes full evaluation across all 5 dimensions."""
    meta_res = evaluate_metadata_completeness()
    lineage_res = evaluate_lineage_coverage()
    fresh_res = evaluate_freshness()
    ground_res = evaluate_retrieval_groundedness()
    stale_res = evaluate_stale_context_rate()

    # Weighted composite quality score
    composite = round(
        (meta_res.score * 0.25) +
        (lineage_res.score * 0.25) +
        (fresh_res.score * 0.20) +
        (ground_res.score * 0.20) +
        ((1.0 - stale_res.rate) * 0.10),
        4
    )

    return ComprehensiveContextEvaluationReport(
        metadata_completeness=meta_res,
        lineage_coverage=lineage_res,
        freshness=fresh_res,
        retrieval_groundedness=ground_res,
        stale_context_rate=stale_res,
        composite_quality_score=composite,
        composite_quality_score_pct=round(composite * 100.0, 1),
    )


__all__ = [
    "evaluate_metadata_completeness",
    "MetadataCompletenessResult",
    "evaluate_lineage_coverage",
    "LineageCoverageResult",
    "evaluate_freshness",
    "FreshnessEvaluationResult",
    "evaluate_retrieval_groundedness",
    "RetrievalGroundednessResult",
    "evaluate_stale_context_rate",
    "StaleContextRateResult",
    "ComprehensiveContextEvaluationReport",
    "evaluate_all_context_metrics",
]
