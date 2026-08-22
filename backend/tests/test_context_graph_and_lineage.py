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
