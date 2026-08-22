"""Tests for Machine Learning Baselines & Feature Ablation."""

import pytest
import numpy as np

from app.intelligence.baselines import get_baseline_suite
from eval.run_ablation import run_ablation_experiment


def test_baseline_suite_execution_and_metrics():
    """Validates that all baseline models run and produce valid comparative evaluation metrics."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()

    assert len(report.models) >= 6
    names = [m.model_name for m in report.models]
    assert "Random Assignment" in names
    assert "Greedy EDF Heuristic" in names
    assert "Ridge Linear Regression" in names
    assert "Random Forest Regressor (XGBoost Tier)" in names
    assert "Multi-Layer Perceptron (BidValueMLP)" in names
    assert "ConstellationCrossAttentionNet" in names
    assert "Hybrid Neural + CP-SAT (Champion)" in names

    for m in report.models:
        assert 0.0 <= m.top1_agreement_pct <= 100.0
        assert m.latency_ms_p50 >= 0.0
        assert m.throughput_inferences_sec > 0.0

    # Ensure champion is Hybrid Neural + CP-SAT
    assert "Hybrid" in report.champion_model


def test_feature_ablation_experiment():
    """Validates that feature ablation runs and shows expected degradation when removing key feature clusters."""
    report = run_ablation_experiment()
    assert report.baseline_top1_pct > 50.0
    assert len(report.ablations) >= 4
    assert len(report.key_findings) >= 3

    # Verify battery ablation shows degradation
    batt_ablation = next(a for a in report.ablations if "Battery" in a.ablation_name)
    assert batt_ablation.performance_delta_pct <= 0.0
