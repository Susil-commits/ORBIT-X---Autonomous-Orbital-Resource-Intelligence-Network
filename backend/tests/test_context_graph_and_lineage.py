"""Tests for Context Graph, Semantic Metadata Catalog, and Data Lineage."""

import pytest
from app.intelligence.context_graph import get_context_graph_engine


def test_semantic_metadata_catalog_retrieval():
    """Validates that the semantic metadata catalog loads datasets with valid schemas and owners."""
    engine = get_context_graph_engine()
    catalog = engine.get_catalog()
    assert catalog.total_datasets >= 4
    names = [d.dataset_name for d in catalog.datasets]
    assert "satellite_telemetry" in names
    assert "mission_requests" in names
    assert "decision_history" in names
    assert "model_features" in names

    telemetry_entry = next(d for d in catalog.datasets if d.dataset_name == "satellite_telemetry")
    assert telemetry_entry.quality_score >= 0.95
    assert len(telemetry_entry.columns) >= 6
    assert "SpacecraftHealthAI (Isolation Forest)" in telemetry_entry.downstream_consumers


def test_natural_language_dataset_search():
    """Validates natural language search over dataset catalog."""
    engine = get_context_graph_engine()
    battery_results = engine.search_datasets("battery")
    assert len(battery_results) >= 1
    assert any("battery" in d.dataset_name or any("battery" in c.name for c in d.columns) for d in battery_results)

    ml_results = engine.search_datasets("Cross-Attention")
    assert len(ml_results) >= 1


def test_decision_lineage_graph_traversal():
    """Validates end-to-end lineage path generation from Raw Telemetry to Mission Outcome."""
    engine = get_context_graph_engine()
    lineage = engine.trace_decision_lineage(mission_id="EO-TEST-99", satellite_id="SAT-05")
    assert lineage.target_id == "EO-TEST-99"
    assert len(lineage.nodes) >= 6
    assert len(lineage.edges) >= 5

    node_types = [n.type for n in lineage.nodes]
    assert "SOURCE_TELEMETRY" in node_types
    assert "DATASET" in node_types
    assert "FEATURE_TABLE" in node_types
    assert "ML_MODEL" in node_types
    assert "OPTIMIZER" in node_types
    assert "DECISION" in node_types
    assert "OUTCOME" in node_types

    assert "SAT-05" in lineage.lineage_path_summary


def test_dataset_dependency_impact_analysis():
    """Validates tracing of downstream ML models dependent on a specific dataset."""
    engine = get_context_graph_engine()
    deps = engine.get_dataset_dependencies("satellite_telemetry")
    assert deps["dataset_name"] == "satellite_telemetry"
    assert len(deps["downstream_consumers"]) >= 2
    assert "SpacecraftHealthAI (Isolation Forest)" in deps["downstream_consumers"]


def test_asset_certification_and_trust_states():
    """Validates 6-pillar context governance: VERIFIED, DRAFT, and DEPRECATED certification states."""
    engine = get_context_graph_engine()
    catalog = engine.get_catalog()
    assert catalog.verified_count >= 4
    assert catalog.draft_count >= 1
    assert catalog.deprecated_count >= 1

    # Check verified dataset
    telemetry = engine.get_dataset_metadata("satellite_telemetry")
    assert telemetry is not None
    assert telemetry.status == "VERIFIED"
    assert telemetry.owner == "flight-operations"
    assert telemetry.quality_score >= 0.99
    assert telemetry.freshness_seconds <= 1.0
    assert "VERIFIED" in telemetry.governance_policy

    # Check draft dataset
    solar_draft = engine.get_dataset_metadata("experimental_solar_flux_forecast")
    assert solar_draft is not None
    assert solar_draft.status == "DRAFT"
    assert solar_draft.owner == "research-lab"
    assert "DRAFT" in solar_draft.certification_badge

    # Check deprecated dataset
    legacy = engine.get_dataset_metadata("legacy_v1_telemetry_csv")
    assert legacy is not None
    assert legacy.status == "DEPRECATED"
    assert "Deprecated" in legacy.description


def test_agent_prefers_verified_assets_over_draft():
    """Validates that search_datasets strictly ranks VERIFIED assets above DRAFT and DEPRECATED assets."""
    engine = get_context_graph_engine()
    # Search for broad keyword matching multiple items
    results = engine.search_datasets("telemetry", prefer_verified=True)
    assert len(results) >= 2
    # The first result must be VERIFIED
    assert results[0].status == "VERIFIED"
    # Deprecated assets must appear after verified assets
    verified_indices = [i for i, d in enumerate(results) if d.status == "VERIFIED"]
    deprecated_indices = [i for i, d in enumerate(results) if d.status == "DEPRECATED"]
    if verified_indices and deprecated_indices:
        assert max(verified_indices) < min(deprecated_indices)

    # get_verified_datasets returns only VERIFIED assets
    verified_only = engine.get_verified_datasets()
    assert len(verified_only) >= 4
    assert all(d.status == "VERIFIED" for d in verified_only)


def test_context_quality_metrics_evaluation():
    """Validates programmatic calculation of the 6 measurable Context Quality metrics."""
    engine = get_context_graph_engine()
    metrics = engine.evaluate_context_quality()

    # Verify bounds [0.0, 1.0] and percentage consistency
    assert 0.80 <= metrics.metadata_completeness <= 1.0
    assert metrics.metadata_completeness_pct == round(metrics.metadata_completeness * 100.0, 1)

    assert 0.80 <= metrics.lineage_coverage <= 1.0
    assert metrics.lineage_coverage_pct == round(metrics.lineage_coverage * 100.0, 1)

    assert 0.80 <= metrics.freshness_sla_compliance <= 1.0
    assert metrics.freshness_sla_compliance_pct == round(metrics.freshness_sla_compliance * 100.0, 1)

    assert 0.80 <= metrics.quality_score <= 1.0
    assert metrics.quality_score_pct == round(metrics.quality_score * 100.0, 1)

    assert 0.50 <= metrics.verified_asset_ratio <= 1.0
    assert metrics.verified_asset_ratio_pct == round(metrics.verified_asset_ratio * 100.0, 1)

    assert 0.80 <= metrics.retrieval_groundedness <= 1.0
    assert metrics.retrieval_groundedness_pct == round(metrics.retrieval_groundedness * 100.0, 1)

    assert metrics.total_assets >= 6
    assert metrics.verified_assets >= 4
    assert metrics.draft_assets >= 1
    assert metrics.deprecated_assets >= 1
    assert metrics.evaluated_at_iso is not None


def test_governed_context_step_execution_order():
    """Validates the 6-step governed agent reasoning pipeline ('Agent asks context, not database')."""
    from app.intelligence.trust_layer import get_trust_layer_engine
    trust_engine = get_trust_layer_engine()
    res = trust_engine.ask_orbitx("Why is Mission M-204 at risk and what should we do?")

    assert len(res.governed_context_steps) == 6
    step_names = [s.step_name for s in res.governed_context_steps]
    expected_order = [
        "discover_context",
        "identify_authoritative_dataset",
        "check_quality_freshness",
        "inspect_lineage",
        "retrieve_data",
        "reason",
    ]
    assert step_names == expected_order

    # Verify context quality metrics attached to response
    assert res.context_quality is not None
    assert res.context_quality.metadata_completeness_pct >= 90.0
    assert res.context_quality.lineage_coverage_pct >= 90.0
    assert res.context_quality.freshness_sla_compliance_pct >= 95.0
