"""Unit & Comparative Tests for Candidate Ranking Models & Baselines.

Tests:
1. Greedy EDF heuristic evaluation and score ranking.
2. Random candidate selector bounds and distribution.
3. XGBoost candidate score fitting and batch prediction.
4. Neural Ranking MLP (BidValueMLP) inference and forward pass.
5. Multi-Head Cross-Attention neural ranker forward pass, logits, and candidate scoring.
6. Full ranking baseline benchmark suite comparative execution and ASCII/Markdown output.
"""

import pytest
import numpy as np
import torch

from ml.models.ranking.greedy_edf import GreedyEDFRanker
from ml.models.ranking.random_ranker import RandomRanker
from ml.models.ranking.xgboost_ranker import XGBoostRanker
from ml.models.ranking.neural_ranker import NeuralRankingMLP, BidValueMLPBaseline
from ml.models.ranking.cross_attention import CrossAttentionRanker
from ml.evaluation.ranking_benchmarks import get_ranking_baseline_suite


def test_greedy_edf_ranker():
    ranker = GreedyEDFRanker()
    # 3 candidates: (high soc, high elev, high prio, low slack)
    X = np.array([
        [0.9, 0.5, 0.8, 0.5, 0.5, 0.5, 0.5, 5.0, 0.5, 0.5, 0.1],  # High priority, high soc
        [0.3, 0.5, 0.2, 0.5, 0.5, 0.5, 0.5, 1.0, 0.5, 0.5, 0.9],  # Low priority, low soc
        [0.7, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 3.0, 0.5, 0.5, 0.4],  # Medium
    ], dtype=np.float32)

    scores = ranker.predict(X)
    assert len(scores) == 3
    assert scores[0] > scores[2] > scores[1]

    ranked = ranker.rank_candidates(X, ["SAT-01", "SAT-02", "SAT-03"])
    assert ranked[0]["candidate_id"] == "SAT-01"


def test_random_ranker():
    ranker = RandomRanker(random_state=42)
    X = np.ones((5, 13), dtype=np.float32)
    scores = ranker.predict(X)
    assert len(scores) == 5
    assert np.all(scores >= 0.0) and np.all(scores <= 100.0)


def test_xgboost_ranker():
    ranker = XGBoostRanker(n_estimators=10, max_depth=3, random_state=42)
    X = np.random.randn(20, 13).astype(np.float32)
    y = np.sum(X[:, :3], axis=1) * 10.0 + 50.0

    ranker.fit(X, y)
    assert ranker.is_fitted

    preds = ranker.predict(X)
    assert len(preds) == 20

    ranked = ranker.rank_candidates(X[:4], ["SAT-A", "SAT-B", "SAT-C", "SAT-D"])
    assert len(ranked) == 4
    assert ranked[0]["rank"] == 1


def test_neural_ranking_mlp():
    net = NeuralRankingMLP(input_dim=13)
    X = np.random.randn(8, 13).astype(np.float32)
    preds = net.predict(X)
    assert len(preds) == 8


def test_cross_attention_ranker():
    model = CrossAttentionRanker(resource_dim=7, request_dim=6, d_model=32, n_heads=2)
    
    # 4 candidate satellites, 1 mission request
    sat_features = np.random.uniform(0.1, 1.0, (4, 7)).astype(np.float32)
    req_features = np.random.uniform(0.1, 1.0, (1, 6)).astype(np.float32)

    scores = model.score_candidates(sat_features, req_features)
    assert len(scores) == 4
    assert np.all(scores >= 0.0) and np.all(scores <= 100.0)

    # Test forward tensor pass
    res_t = torch.from_numpy(sat_features).unsqueeze(0)
    req_t = torch.from_numpy(req_features).unsqueeze(0)
    out = model(res_t, req_t, return_attention=True)
    assert "logits" in out
    assert "probabilities" in out
    assert "attention_weights" in out
    assert out["logits"].shape == (1, 4)


def test_ranking_baseline_benchmark_suite():
    suite = get_ranking_baseline_suite()
    report = suite.run_benchmark()

    assert "models" in report
    assert len(report["models"]) == 5

    model_names = [m["model_name"] for m in report["models"]]
    assert "Greedy EDF" in model_names
    assert "Random" in model_names
    assert "XGBoost" in model_names
    assert "Neural Ranking" in model_names
    assert "Cross-Attention" in model_names

    # Verify table outputs
    assert "ascii_table" in report and len(report["ascii_table"]) > 0
    assert "markdown_table" in report and len(report["markdown_table"]) > 0
    assert report["champion_model"] == "Cross-Attention"

    # Cross-Attention must be superior in top-1 accuracy
    ca_model = next(m for m in report["models"] if m["model_name"] == "Cross-Attention")
    greedy_model = next(m for m in report["models"] if m["model_name"] == "Greedy EDF")
    assert ca_model["top1_accuracy_pct"] > greedy_model["top1_accuracy_pct"]
    assert ca_model["latency_p50_ms"] < 1.0
