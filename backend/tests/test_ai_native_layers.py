"""Tests for the ORBIT-X Modular Decision Intelligence Architecture Layers.

Validates:
- Data Layer: Pydantic schemas, validation, cleaning, feature engineering
- ML Layer: Cross-Attention neural ranker, XGBoost tabular ranker, TreeSHAP
- Anomaly Detection Layer: Isolation Forest detector & risk penalty scoring
- Context Layer: Semantic metadata catalog, data discovery, lineage DAG
- Agents & MCP Layer: FastMCP tools registry, agent orchestration loop
- Decision Layer: Human governance review, continuous feedback loop
- Simulation Layer: Telemetry generation & physics propagation
"""

import pytest
import numpy as np
import torch

from data.schemas.entities import Telemetry, MissionRequest, Anomaly, Prediction, Decision, Feedback
from data.pipeline import DataProcessingPipeline, get_data_pipeline
from ml.models.cross_attention.ranker import CrossAttentionNeuralRanker
from ml.models.xgboost.ranker import XGBoostRanker
from ml.models.baselines.classical import RandomBaseline, GreedyEDFBaseline, RidgeBaseline
from ml.explainability.shap_xai import TreeSHAPExplainer
from anomaly_detection.models.isolation_forest import IsolationForestAnomalyDetector
from context.metadata.catalog import SemanticMetadataCatalog
from context.discovery.search import DataDiscoveryEngine
from context.lineage.graph import DataLineageGraph
from agents.tools.mcp_tools import AIToolsRegistry, get_ai_tools_registry
from agents.agent_loop.orchestrator import AgentOrchestrator
from decision.human_review.governance import HumanGovernanceEngine, OperatorReviewSubmission
from decision.feedback.loop import FeedbackLoopManager
from simulation.telemetry.generator import TelemetryStreamGenerator


def test_data_pipeline_and_schemas():
    """Validates data validation, cleaning, and feature engineering."""
    pipeline = get_data_pipeline()
    raw = {
        "resource_id": "SAT-01",
        "battery_soc": 0.88,
        "bus_voltage_v": 28.2,
        "battery_temp_c": 22.4,
        "comm_latency_ms": 45.0,
        "link_snr_db": 18.5,
        "memory_util_pct": 35.0,
        "is_sunlit": True,
    }
    telemetry, err = pipeline.validate_telemetry(raw)
    assert err is None
    assert telemetry.resource_id == "SAT-01"
    assert telemetry.battery_soc == 0.88

    cleaned = pipeline.clean_telemetry(telemetry)
    assert cleaned["battery_soc"] == 0.88

    req = MissionRequest(
        request_id="M-204",
        priority=4,
        target_lat=34.05,
        target_lon=-118.25,
        deadline_epoch_s=3600.0,
    )
    features = pipeline.extract_features(cleaned, req, current_time_s=100.0)
    assert len(features) == 13
    assert isinstance(features, np.ndarray)


def test_ml_cross_attention_and_xgboost():
    """Validates neural cross-attention ranker and XGBoost tabular model."""
    ranker = CrossAttentionNeuralRanker(resource_dim=7, request_dim=6, d_model=32, n_heads=2)
    ranker.eval()

    res_feat = torch.randn(2, 5, 7)  # 2 batches, 5 candidate resources, 7 dims
    req_feat = torch.randn(2, 1, 6)  # 2 batches, 1 mission request, 6 dims

    with torch.no_grad():
        out = ranker(res_feat, req_feat, return_attention=True)

    assert "probabilities" in out
    assert out["probabilities"].shape == (2, 5)
    assert torch.allclose(out["probabilities"].sum(dim=-1), torch.ones(2), atol=1e-5)
    assert "attention_weights" in out

    # Test XGBoost Ranker
    xgb = XGBoostRanker(n_estimators=10)
    X = np.random.randn(20, 13)
    y = np.random.uniform(10, 90, 20)
    xgb.fit(X, y)
    preds = xgb.predict(X[:5])
    assert len(preds) == 5
    ranked = xgb.rank_candidates(X[:3], ["SAT-01", "SAT-02", "SAT-03"])
    assert len(ranked) == 3
    assert ranked[0]["rank"] == 1


def test_anomaly_detection_isolation_forest():
    """Validates multivariate Isolation Forest scoring and risk penalty."""
    detector = IsolationForestAnomalyDetector(n_estimators=50)
    nominal_vec = np.array([0.88, 22.0, 28.0, 45.0, 18.0, 35.0, 35.0])
    res_nom = detector.score_telemetry(nominal_vec)
    assert "anomaly_score" in res_nom
    assert not res_nom["is_anomaly"]

    severe_fault = np.array([0.20, 65.0, 21.0, 400.0, 2.0, 98.0, 95.0])
    res_fault = detector.score_telemetry(severe_fault)
    assert res_fault["is_anomaly"]
    assert res_fault["risk_penalty"] > 0.0


def test_context_metadata_and_lineage():
    """Validates semantic metadata catalog, discovery search, and lineage DAG."""
    catalog = SemanticMetadataCatalog()
    telemetry_meta = catalog.get_dataset("satellite_telemetry")
    assert telemetry_meta is not None
    assert telemetry_meta.quality_score >= 0.95

    discovery = DataDiscoveryEngine(catalog)
    results = discovery.find_by_query("battery telemetry")
    assert len(results) > 0

    lineage = DataLineageGraph.trace_decision_lineage("DEC-001")
    assert "nodes" in lineage
    assert "edges" in lineage
    assert len(lineage["nodes"]) >= 5


def test_agents_and_tools_registry():
    """Validates standard FastMCP tools registry and orchestrator loop."""
    tools = get_ai_tools_registry()
    meta = tools.get_dataset_metadata("satellite_telemetry")
    assert "columns" in meta

    anomaly = tools.get_anomaly("SAT-03")
    assert "anomaly_score" in anomaly

    pred = tools.get_prediction("SAT-01")
    assert pred["ranking_score"] > 0

    orchestrator = AgentOrchestrator()
    result = orchestrator.process_query("Why is Mission M-204 at risk and what should we do?")
    assert result["status"] == "VERIFIED_TRUST_ENVELOPE"
    assert result["confidence_score"] >= 0.90
    assert len(result["evidence"]) >= 3


def test_decision_governance_and_feedback():
    """Validates operator review and continuous feedback loop dataset."""
    gov = HumanGovernanceEngine()
    review = gov.submit_review(
        OperatorReviewSubmission(
            decision_id="DEC-001",
            action="APPROVE",
            rationale="Verified zero hard constraint violations.",
        )
    )
    assert review["human_decision"] == "APPROVE"

    feedback_loop = FeedbackLoopManager()
    entry = feedback_loop.record_feedback(
        decision_id="DEC-001",
        human_decision="APPROVE",
        rationale="Nominal execution verified.",
    )
    assert entry["alignment_score"] == 1.0
    stats = feedback_loop.get_dataset_statistics()
    assert stats["total_feedback_records"] == 1
    assert stats["approval_rate"] == 1.0


def test_simulation_telemetry_generator():
    """Validates simulation telemetry generation."""
    gen = TelemetryStreamGenerator(resource_id="SAT-05")
    frame = gen.generate_frame(is_sunlit=True, inject_anomaly=False)
    assert frame["resource_id"] == "SAT-05"
    assert 0.0 <= frame["battery_soc"] <= 1.0
