"""Tests for Machine Learning Baselines & Feature Ablation."""

import pytest
import numpy as np

from app.intelligence.baselines import get_baseline_suite
from eval.run_ablation import run_ablation_experiment


def test_baseline_suite_execution_and_metrics():
    """Validates that ML models and Decision Systems run and produce valid comparative evaluation metrics."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()

    # 1. Validate Pure ML & Heuristic Evaluation Models
    assert len(report.ml_models) == 6
    ml_names = [m.model_name for m in report.ml_models]
    assert "Random Assignment" in ml_names
    assert "Greedy EDF Heuristic" in ml_names
    assert "Ridge Linear Regression" in ml_names
    assert "Random Forest Regressor (XGBoost Tier)" in ml_names
    assert "Multi-Layer Perceptron (BidValueMLP)" in ml_names
    assert "ConstellationCrossAttentionNet" in ml_names

    for m in report.ml_models:
        assert 0.0 <= m.top1_agreement_pct <= 100.0
        assert m.latency_ms_p50 >= 0.0
        assert m.throughput_inferences_sec > 0.0

    # 2. Validate Decision Systems Evaluation
    assert len(report.decision_systems) == 2
    dec_names = [d.system_name for d in report.decision_systems]
    assert "Cross-Attention Only" in dec_names
    assert "Cross-Attention + CP-SAT" in dec_names

    for d in report.decision_systems:
        assert 0.0 <= d.feasibility_rate_pct <= 100.0
        assert 0.0 <= d.decision_utility_pct <= 100.0
        assert d.end_to_end_latency_ms_p50 > 0.0
        assert len(d.constraint_violations) > 0

    # 3. Ensure Champion metadata is cleanly separated
    assert report.champion_ml_model == "ConstellationCrossAttentionNet"
    assert "CP-SAT" in report.champion_decision_system


def test_feature_ablation_experiment():
    """Validates that feature ablation runs and shows expected degradation when removing key feature clusters."""
    report = run_ablation_experiment()
    assert report.baseline_top1_pct > 50.0
    assert len(report.ablations) >= 4
    assert len(report.key_findings) >= 3

    # Verify battery ablation shows degradation
    batt_ablation = next(a for a in report.ablations if "Battery" in a.ablation_name)
    assert batt_ablation.performance_delta_pct <= 0.0
