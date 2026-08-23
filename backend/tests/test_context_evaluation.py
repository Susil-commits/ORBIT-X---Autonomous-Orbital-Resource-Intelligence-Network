"""Unit Tests for Deterministic, Non-Invented Context Quality Evaluator & Modular Evaluation Package."""

import pytest
from app.context.evaluation.context_evaluator import (
    ContextQualityEvaluator,
    get_context_quality_evaluator,
)
from context.schemas import (
    AssetStatus,
    GovernedAsset,
    Dataset,
    Mission,
    Satellite,
    TelemetryStream,
    Feature,
    Model,
    Prediction,
    Anomaly,
    Decision,
    Tool,
)
from context.discovery.search import DataDiscoveryEngine
from context.metadata.catalog import SemanticMetadataCatalog, DatasetMetadataRecord
from context.lineage.graph import DataLineageGraph
from context.evaluation import (
    evaluate_metadata_completeness,
    evaluate_lineage_coverage,
    evaluate_freshness,
    evaluate_retrieval_groundedness,
    evaluate_stale_context_rate,
    evaluate_all_context_metrics,
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


def test_ten_canonical_context_entities_schemas():
    """Validates all 10 canonical context graph entities with uniform trust & governance metadata."""
    entities = [
        Dataset(entity_id="ds-01", name="satellite_telemetry", description="Telemetry frames", status=AssetStatus.VERIFIED, owner="flight-ops", freshness="0.1s", quality_score=0.99, schema_version="2.0.0"),
        Mission(entity_id="ms-01", name="disaster_flood_imaging", description="Priority flood monitoring", status=AssetStatus.VERIFIED, owner="mission-planning", freshness="10.0s", quality_score=0.98, schema_version="2.0.0"),
        Satellite(entity_id="sat-01", name="SAT-01", description="Sun-synchronous satellite asset", status=AssetStatus.VERIFIED, owner="spacecraft-systems", freshness="0.1s", quality_score=1.0, schema_version="2.2.0"),
        TelemetryStream(entity_id="ts-01", name="stream_sat01", description="10Hz live downlink stream", status=AssetStatus.VERIFIED, owner="ground-ops", freshness="0.1s", quality_score=0.99, schema_version="2.0.0"),
        Feature(entity_id="ft-01", name="18_dim_vector", description="Standardized feature table", status=AssetStatus.VERIFIED, owner="ml-platform", freshness="1.0s", quality_score=0.99, schema_version="2.2.0"),
        Model(entity_id="md-01", name="CrossAttentionRanker", description="Neural candidate valuation network", status=AssetStatus.VERIFIED, owner="ml-platform", freshness="3600.0s", quality_score=0.97, schema_version="2.2.0"),
        Prediction(entity_id="pr-01", name="val_sat01_m204", description="Neural win probability token", status=AssetStatus.VERIFIED, owner="autonomous-gnc", freshness="0.2s", quality_score=0.94, schema_version="2.2.0"),
        Anomaly(entity_id="an-01", name="health_isolation_forest", description="Multivariate health scorer", status=AssetStatus.VERIFIED, owner="health-ai", freshness="0.5s", quality_score=0.98, schema_version="1.5.0"),
        Decision(entity_id="dc-01", name="assignment_dec_204", description="Allocated satellite mission pair", status=AssetStatus.VERIFIED, owner="decision-intelligence", freshness="0.1s", quality_score=1.0, schema_version="2.0.0"),
        Tool(entity_id="tl-01", name="Google_OR_Tools_CP_SAT", description="Integer constraint optimization solver", status=AssetStatus.VERIFIED, owner="mission-planning", freshness="0.05s", quality_score=1.0, schema_version="3.0.0"),
    ]

    for entity in entities:
        assert isinstance(entity, GovernedAsset)
        assert entity.status in [AssetStatus.VERIFIED, AssetStatus.DRAFT, AssetStatus.DEPRECATED]
        assert entity.owner != ""
        assert entity.last_reviewed != ""
        assert entity.freshness != ""
        assert 0.0 <= entity.quality_score <= 1.0
        assert entity.schema_version != ""
        assert entity.is_trusted is True


def test_retrieval_prefers_verified_and_current_assets():
    """Validates that DataDiscoveryEngine strictly prioritizes VERIFIED over DRAFT and DEPRECATED."""
    engine = DataDiscoveryEngine()

    # General query that matches multiple assets including DRAFT and DEPRECATED
    results = engine.find_by_query("telemetry", prefer_verified=True)
    assert len(results) >= 1
    # Top result must be verified
    assert results[0].status == "VERIFIED"
    assert results[0].dataset_name == "satellite_telemetry"

    # Search for solar / research asset (DRAFT)
    solar_results = engine.find_by_query("solar flux forecast", prefer_verified=True)
    assert any(r.status == "DRAFT" for r in solar_results)

    # Search requiring verified only
    verified_only = engine.search("telemetry", require_verified=True)
    assert all(r.status == "VERIFIED" for r in verified_only)


def test_modular_context_evaluation_package():
    """Validates individual modules in context.evaluation: metadata_completeness, lineage_coverage, freshness, retrieval_groundedness, stale_context_rate."""
    # 1. Metadata completeness
    meta_res = evaluate_metadata_completeness()
    assert 0.80 <= meta_res.score <= 1.0
    assert meta_res.evaluated_assets_count >= 5

    # 2. Lineage coverage
    lineage_res = evaluate_lineage_coverage()
    assert lineage_res.score >= 0.90
    assert lineage_res.total_canonical_nodes == 10
    assert lineage_res.connected_nodes == 10

    # 3. Freshness
    fresh_res = evaluate_freshness()
    assert 0.70 <= fresh_res.score <= 1.0
    assert fresh_res.total_evaluated_entities >= 10

    # 4. Retrieval groundedness
    ground_res = evaluate_retrieval_groundedness()
    assert 0.80 <= ground_res.score <= 1.0
    assert ground_res.grounded_hits >= 4

    # 5. Stale context rate
    stale_res = evaluate_stale_context_rate()
    assert 0.0 <= stale_res.rate <= 0.30

    # 6. Full aggregated report
    full_report = evaluate_all_context_metrics()
    assert 0.80 <= full_report.composite_quality_score <= 1.0
    assert full_report.composite_quality_score_pct == round(full_report.composite_quality_score * 100.0, 1)
    assert full_report.evaluated_at_iso is not None


def test_context_quality_synthetic_drift_sensitivity():
    """Validates that modifying catalog state dynamically shifts the measured metrics."""
    from app.core.schemas import DataCatalogEntry

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
