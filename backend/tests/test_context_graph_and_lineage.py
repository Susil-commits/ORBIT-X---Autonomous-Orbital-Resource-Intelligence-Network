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
    """Validates 10-entity lineage path generation from Constellation Asset to Mission Outcome."""
    engine = get_context_graph_engine()
    lineage = engine.trace_decision_lineage(mission_id="EO-TEST-99", satellite_id="SAT-05")
    assert lineage.target_id == "EO-TEST-99"
    assert len(lineage.nodes) == 10
    assert len(lineage.edges) == 11

    node_types = [n.type for n in lineage.nodes]
    assert "CONSTELLATION_SATELLITE" in node_types
    assert "SOURCE_TELEMETRY" in node_types
    assert "DATASET" in node_types
    assert "FEATURE_TABLE" in node_types
    assert "ANOMALY_DETECTOR" in node_types
    assert "ML_MODEL" in node_types
    assert "MODEL_PREDICTION" in node_types
    assert "OPTIMIZER" in node_types
    assert "DECISION_RECORD" in node_types
    assert "MISSION_OUTCOME" in node_types

    # Validate that all 10 nodes possess complete governance state
    for node in lineage.nodes:
        assert node.asset_status in ["VERIFIED", "DRAFT", "DEPRECATED"]
        assert node.owner is not None and len(node.owner) > 0
        assert node.last_reviewed is not None and len(node.last_reviewed) > 0
        assert node.freshness is not None and len(node.freshness) > 0
        assert 0.0 <= node.quality_score <= 1.0
        assert node.schema_version is not None and len(node.schema_version) > 0
        assert node.is_trusted is True

    assert "SAT-05" in lineage.lineage_path_summary


def test_ten_governed_entities_contract():
    """Validates that get_governed_entities returns 10 distinct entities with full governance contracts."""
    engine = get_context_graph_engine()
    entities = engine.get_governed_entities(satellite_id="SAT-03")
    assert len(entities) == 10
    ids = [e.id for e in entities]
    expected_ids = [
        "satellite_asset",
        "telemetry_stream",
        "dataset_telemetry",
        "feature_vector",
        "anomaly_detector",
        "ml_model",
        "model_prediction",
        "cpsat_optimizer",
        "decision_record",
        "mission_outcome",
    ]
    for exp_id in expected_ids:
        assert exp_id in ids

    # Check that each node has owner, freshness SLA, quality score, schema version
    sat_asset = next(e for e in entities if e.id == "satellite_asset")
    assert sat_asset.owner == "spacecraft-systems"
    assert sat_asset.quality_score >= 0.99
    assert sat_asset.schema_version == "v2.2"


def test_trusted_vs_untrusted_context_filtering():
    """Validates that agent can programmatically distinguish trusted context from draft/deprecated/stale context."""
    from app.core.schemas import DataLineageNode
    engine = get_context_graph_engine()
    
    # Create test nodes with mixed governance states
    mixed_nodes = [
        DataLineageNode(
            id="node_verified",
            label="Verified Live Telemetry",
            type="SOURCE_TELEMETRY",
            asset_status="VERIFIED",
            owner="flight-operations",
            last_reviewed="2026-08-23T12:00:00Z",
            freshness="0.5s",
            quality_score=0.99,
            schema_version="v2.0",
            is_trusted=True,
        ),
        DataLineageNode(
            id="node_draft",
            label="Draft Solar Forecast",
            type="DATASET",
            asset_status="DRAFT",
            owner="research-lab",
            last_reviewed="2026-08-15T09:00:00Z",
            freshness="3600.0s",
            quality_score=0.74,
            schema_version="v0.1-alpha",
            is_trusted=False,
        ),
        DataLineageNode(
            id="node_deprecated",
            label="Legacy CSV Dumps",
            type="DATASET",
            asset_status="DEPRECATED",
            owner="legacy-ops",
            last_reviewed="2026-01-10T00:00:00Z",
            freshness="86400.0s",
            quality_score=0.65,
            schema_version="v1.0-deprecated",
            is_trusted=False,
        ),
    ]

    trusted, untrusted = engine.filter_trusted_context(mixed_nodes)
    assert len(trusted) == 1
    assert trusted[0].id == "node_verified"
    assert len(untrusted) == 2
    untrusted_ids = [n.id for n in untrusted]
    assert "node_draft" in untrusted_ids
    assert "node_deprecated" in untrusted_ids

    # Validate audit report generator
    audit = engine.validate_context_governance(mixed_nodes)
    assert audit.governance_passed is False
    assert "node_verified" in audit.trusted_entities
    assert "node_draft" in audit.untrusted_entities
    assert "node_deprecated" in audit.untrusted_entities


def test_what_data_influenced_decision_governance():
    """Validates that backwards-trace returns complete governance state for all influencing components."""
    engine = get_context_graph_engine()
    trace = engine.what_data_influenced_decision(decision_id="DEC-M-204", satellite_id="SAT-17")
    assert trace["decision_id"] == "DEC-M-204"
    assert trace["context_governance"]["governance_status"] == "PASSED"
    assert trace["context_governance"]["total_entities_governed"] == 10

    lineage = trace["influencing_lineage"]
    # Check satellite
    assert lineage["constellation_satellite"]["asset_status"] == "VERIFIED"
    assert lineage["constellation_satellite"]["owner"] == "spacecraft-systems"
    assert lineage["constellation_satellite"]["schema_version"] == "v2.2"

    # Check telemetry
    assert lineage["source_telemetry"]["asset_status"] == "VERIFIED"
    assert lineage["source_telemetry"]["freshness"] == "0.1s"

    # Check queried datasets
    for ds in lineage["queried_datasets"]:
        assert ds["asset_status"] == "VERIFIED"
        assert ds["owner"] is not None
        assert ds["quality_score"] >= 0.95
        assert ds["schema_version"] is not None

    # Check features & models
    assert lineage["engineered_features"]["asset_status"] == "VERIFIED"
    assert lineage["evaluated_models"][0]["asset_status"] == "VERIFIED"
    assert lineage["evaluated_models"][1]["asset_status"] == "VERIFIED"


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
    assert res.context_quality.freshness_sla_compliance_pct >= 90.0

    # Verify context governance audit in evidence items
    evidence_types = [e.evidence_type for e in res.evidence]
    assert "CONTEXT_GOVERNANCE_AUDIT" in evidence_types
    assert "GOVERNED_CONTEXT" in evidence_types


def test_seven_stage_lineage_pipeline_forward_and_backward():
    """Validates that get_seven_stage_pipeline_trace returns all 7 canonical stages in order with bidirectional traversal."""
    engine = get_context_graph_engine()
    trace = engine.get_seven_stage_pipeline_trace(decision_id="DEC-20260824-M204", mission_id="M-204", satellite_id="SAT-17")

    assert trace["decision_id"] == "DEC-20260824-M204"
    assert trace["mission_id"] == "M-204"
    assert trace["satellite_id"] == "SAT-17"

    stages = trace["pipeline_stages"]
    assert len(stages) == 7

    stage_ids = [s["stage_id"] for s in stages]
    expected_stage_ids = [
        "raw_telemetry",
        "cleaning_validation",
        "feature_table",
        "anomaly_model",
        "prediction",
        "decision",
        "agent_response",
    ]
    assert stage_ids == expected_stage_ids

    # Forward and backward order validation
    assert trace["forward_flow_order"] == expected_stage_ids
    assert trace["backward_trace_order"] == list(reversed(expected_stage_ids))

    # Validate each stage has verified status and operational metrics
    for stage in stages:
        assert stage["asset_status"] == "VERIFIED"
        assert stage["quality_score"] >= 0.95
        assert len(stage["operational_metrics"]) >= 3
        assert len(stage["transformation_description"]) > 10

    # Validate specific values in stages
    raw_stage = next(s for s in stages if s["stage_id"] == "raw_telemetry")
    assert raw_stage["operational_metrics"]["battery_soc"] == "88.5%"
    assert "orbitx.telemetry.sat-17" in raw_stage["asset_name"] or "sat17" in raw_stage["asset_name"].replace("-", "")

    opt_stage = next(s for s in stages if s["stage_id"] == "decision")
    assert opt_stage["operational_metrics"]["solver_status"] == "FEASIBLE_AND_OPTIMAL"
    assert opt_stage["operational_metrics"]["hard_safety_violations"] == "0"



def test_why_was_this_decision_made_root_cause_narrative():
    """Validates that querying 'Why was this decision made?' produces an auditable root-cause explanation."""
    engine = get_context_graph_engine()
    res = engine.query_lineage("Why was this decision made?")

    assert res["query_type"] == "BACKWARD_PROVENANCE_ROOT_CAUSE"
    assert "Why was this decision made?" in res["headline"]
    assert "ROOT-CAUSE PROVENANCE AUDIT" in res["explanation"]
    assert "SAT-17" in res["explanation"]
    assert "Agent Response" in res["explanation"]
    assert "Decision (CP-SAT)" in res["explanation"]
    assert "Prediction" in res["explanation"]
    assert "Anomaly Model" in res["explanation"]
    assert "Feature Table" in res["explanation"]
    assert "Cleaning & Validation" in res["explanation"]
    assert "Raw Telemetry" in res["explanation"]

    assert len(res["active_pipeline"]["pipeline_stages"]) == 7


def test_column_level_lineage_derivation_mapping():
    """Validates Column-Level Lineage (CLL) connecting raw columns to features, models, and decision invariants."""
    engine = get_context_graph_engine()
    cll = engine.get_column_level_lineage()

    assert len(cll) >= 5
    soc_entry = next(c for c in cll if c["source_column"] == "battery_soc")
    assert soc_entry["feature_name"] == "battery_soc_margin"
    assert "ConstellationCrossAttentionNet" in soc_entry["model_consumer"]
    assert "sat_soc >= 0.20" in soc_entry["decision_invariant"]
    assert soc_entry["governance_status"] == "VERIFIED"

    temp_entry = next(c for c in cll if c["source_column"] == "battery_temp_c")
    assert temp_entry["feature_name"] == "thermal_headroom_norm"
    assert "TelemetryIsolationForest" in temp_entry["model_consumer"]
    assert "temp_c <= 45.0°C" in temp_entry["decision_invariant"]

    elev_entry = next(c for c in cll if c["source_column"] == "target_elevation_deg")
    assert elev_entry["feature_name"] == "look_angle_slack_norm"
    assert "max_elevation >= 15.0°" in elev_entry["decision_invariant"]


def test_natural_language_lineage_query_engine():
    """Validates that query_lineage handles different query modalities: why, column, drift."""
    engine = get_context_graph_engine()

    # Query 1: Column trace
    res_col = engine.query_lineage("Trace battery_soc from raw sensor")
    assert res_col["query_type"] == "COLUMN_LEVEL_DERIVATION"
    assert len(res_col["column_lineage"]) >= 5

    # Query 2: Impact / blast radius analysis
    res_drift = engine.query_lineage("What if telemetry drifts?")
    assert res_drift["query_type"] == "FORWARD_IMPACT_BLAST_RADIUS"
    assert "dependencies" in res_drift
    assert "downstream_consumers" in res_drift["dependencies"]

