"""Unit Tests for Deterministic, Non-Invented Context Quality Evaluator."""

import pytest
from app.context.evaluation.context_evaluator import (
    ContextQualityEvaluator,
    get_context_quality_evaluator,
)


def test_context_quality_evaluator_singleton():
    """Validates singleton getter for ContextQualityEvaluator."""
    evaluator1 = get_context_quality_evaluator()
    evaluator2 = get_context_quality_evaluator()
    assert evaluator1 is evaluator2


def test_context_quality_six_metrics_calculation():
    """Validates that all 6 empirical metrics are calculated mathematically from real context data."""
    evaluator = get_context_quality_evaluator()
    metrics = evaluator.evaluate()

    # 1. Metadata Completeness: [0.0, 1.0]
    assert 0.80 <= metrics.metadata_completeness <= 1.0
    assert metrics.metadata_completeness_pct == round(metrics.metadata_completeness * 100.0, 1)

    # 2. Lineage Coverage: [0.0, 1.0]
    assert 0.80 <= metrics.lineage_coverage <= 1.0
    assert metrics.lineage_coverage_pct == round(metrics.lineage_coverage * 100.0, 1)

    # 3. Freshness SLA Compliance: [0.0, 1.0]
    assert 0.80 <= metrics.freshness_sla_compliance <= 1.0
    assert metrics.freshness_sla_compliance_pct == round(metrics.freshness_sla_compliance * 100.0, 1)

    # 4. Verified Asset Ratio: [0.0, 1.0]
    assert 0.40 <= metrics.verified_asset_ratio <= 1.0
    assert metrics.verified_asset_ratio_pct == round(metrics.verified_asset_ratio * 100.0, 1)

    # 5. Retrieval Groundedness: [0.0, 1.0]
    assert 0.80 <= metrics.retrieval_groundedness <= 1.0
    assert metrics.retrieval_groundedness_pct == round(metrics.retrieval_groundedness * 100.0, 1)

    # 6. Stale Context Rate: [0.0, 1.0] (Should be low, <= 0.20)
    assert 0.0 <= metrics.stale_context_rate <= 0.30
    assert metrics.stale_context_rate_pct == round(metrics.stale_context_rate * 100.0, 1)

    # Check asset counts
    assert metrics.total_assets >= 6
    assert metrics.verified_assets >= 4
    assert metrics.draft_assets >= 1
    assert metrics.deprecated_assets >= 1
    assert metrics.stale_assets_count >= 1

    # Check formula notes documentation
    assert "metadata_completeness" in metrics.measurement_formula_notes
    assert "lineage_coverage" in metrics.measurement_formula_notes
    assert "freshness_sla_compliance" in metrics.measurement_formula_notes
    assert "verified_asset_ratio" in metrics.measurement_formula_notes
    assert "retrieval_groundedness" in metrics.measurement_formula_notes
    assert "stale_context_rate" in metrics.measurement_formula_notes


def test_context_quality_synthetic_drift_sensitivity():
    """Validates that modifying catalog state dynamically shifts the measured metrics."""
    from app.core.schemas import DataCatalogEntry

    # Custom provider with degraded draft datasets
    custom_datasets = [
        DataCatalogEntry(
            dataset_name="custom_clean",
            owner="flight-ops",
            description="Clean verified telemetry",
            schema_version="v2.0",
            storage_format="parquet",
            freshness_seconds=0.5,
            quality_score=0.99,
            sensitivity="INTERNAL",
            status="VERIFIED",
            last_reviewed="2026-08-23",
            certification_badge="VERIFIED",
            governance_policy="POL-1",
            columns=[],
            downstream_consumers=["ML-1"],
        ),
        DataCatalogEntry(
            dataset_name="custom_stale_deprecated",
            owner="legacy-ops",
            description="Stale deprecated CSV",
            schema_version="v1.0",
            storage_format="csv",
            freshness_seconds=999999.0,
            quality_score=0.50,
            sensitivity="PUBLIC",
            status="DEPRECATED",
            last_reviewed="2024-01-01",
            certification_badge="DEPRECATED",
            governance_policy="POL-NONE",
            columns=[],
            downstream_consumers=[],
        ),
    ]

    evaluator = ContextQualityEvaluator(catalog_provider=lambda: type("Catalog", (), {"datasets": custom_datasets})())
    metrics = evaluator.evaluate()

    assert metrics.total_assets == 2
    assert metrics.verified_assets == 1
    assert metrics.deprecated_assets == 1
    assert metrics.verified_asset_ratio == 0.50
    assert metrics.stale_assets_count >= 1
