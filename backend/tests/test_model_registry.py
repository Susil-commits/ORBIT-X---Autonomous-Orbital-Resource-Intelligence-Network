"""Unit & Governance Tests for ORBIT-X Model Registry.

Tests:
1. Model card validation & required governance fields.
2. Registration of models and retrieval by ID / version.
3. Champion model resolution across tasks (ranking, anomaly, forecasting).
4. Lifecycle status transitions & promotion with validation.
5. SHA256 integrity checksum verification.
6. Side-by-side comparative metric diffing.
"""

import pytest
from pathlib import Path
from ml.registry import (
    ModelRegistry,
    ModelCard,
    ModelStatus,
    TaskType,
    FeatureSchema,
    FeatureSpec,
    LatencyProfile,
    get_model_registry,
)


def test_model_registry_load_and_default_cards():
    registry = get_model_registry()
    assert len(registry.models) >= 7

    # Check champion ranking model
    rank_champ = registry.get_champion(TaskType.RANKING)
    assert rank_champ is not None
    assert rank_champ.model_id == "orbitx-ranking-cross-attention-v1"
    assert rank_champ.status == ModelStatus.CHAMPION
    assert rank_champ.metrics["top1_ranking_accuracy_pct"] == 84.6
    assert rank_champ.latency.p50_ms < 1.0

    # Check champion anomaly model
    anom_champ = registry.get_champion(TaskType.ANOMALY)
    assert anom_champ is not None
    assert anom_champ.model_id == "orbitx-anomaly-isolation-forest-v1"
    assert anom_champ.metrics["fault_recall_pct"] == 85.6

    # Check champion forecasting model
    fc_champ = registry.get_champion(TaskType.FORECASTING)
    assert fc_champ is not None
    assert fc_champ.model_id == "orbitx-forecasting-pinn-battery-v1"


def test_all_models_have_mandatory_governance_fields():
    registry = get_model_registry()
    for key, card in registry.models.items():
        assert card.model_id is not None and len(card.model_id) > 0
        assert card.version is not None and len(card.version) > 0
        assert card.training_dataset is not None and len(card.training_dataset) > 0
        assert card.feature_schema is not None
        assert isinstance(card.metrics, dict) and len(card.metrics) > 0
        assert card.latency is not None and card.latency.p50_ms > 0
        assert card.owner is not None and len(card.owner) > 0
        assert card.status in list(ModelStatus)
        assert card.data_freshness is not None and len(card.data_freshness) > 0
        assert len(card.sha256) == 64
        assert card.governance_gates.get("sha256_verified", False) is True


def test_model_registration_and_retrieval(tmp_path):
    custom_reg_path = tmp_path / "test_model_card.json"
    registry = ModelRegistry(registry_file=custom_reg_path)

    new_card = ModelCard(
        model_id="orbitx-ranking-test-model",
        version="1.0.0",
        task_type=TaskType.RANKING,
        name="Test Ranker",
        description="Temporary test ranking network",
        training_dataset="test_corpus_v1",
        feature_schema=FeatureSchema(
            input_features=[FeatureSpec(name="f1", description="feature 1")],
            output_features=[FeatureSpec(name="out", description="output score")],
            total_input_dim=1,
        ),
        metrics={"top1_ranking_accuracy_pct": 82.0, "mae": 40.0},
        latency=LatencyProfile(p50_ms=0.35, p95_ms=0.50, p99_ms=0.65, throughput_req_per_sec=2850.0),
        owner="MLOps Test Suite",
        status=ModelStatus.EXPERIMENTAL,
        data_freshness="2026-08-25T00:00:00Z",
        sha256="a" * 64,
    )

    registry.register_model(new_card)

    fetched = registry.get_model("orbitx-ranking-test-model", "1.0.0")
    assert fetched is not None
    assert fetched.name == "Test Ranker"
    assert fetched.governance_gates["sha256_verified"] is True
    assert fetched.governance_gates["latency_sla_passed"] is True


def test_model_promotion_and_status_transition():
    registry = get_model_registry()
    xgb_card = registry.get_model("orbitx-ranking-xgboost-v1")
    assert xgb_card is not None

    promoted = registry.promote_model("orbitx-ranking-xgboost-v1", ModelStatus.PRODUCTION)
    assert promoted.status == ModelStatus.PRODUCTION


def test_model_comparison_diffing():
    registry = get_model_registry()
    comparison = registry.compare_models([
        "orbitx-ranking-cross-attention-v1",
        "orbitx-ranking-xgboost-v1",
        "orbitx-ranking-greedy-edf-v1",
    ])
    assert comparison["models_compared"] == 3
    assert comparison["winner_model_id"] == "orbitx-ranking-cross-attention-v1"
    assert len(comparison["table"]) == 3
