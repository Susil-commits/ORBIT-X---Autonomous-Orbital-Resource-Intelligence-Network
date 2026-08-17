"""Unit tests for the Automated Evaluation Harness & Regression Gates."""

import pytest
from eval.run_eval import run_full_evaluation, evaluate_orbital_physics


def test_eval_harness_execution():
    """Validates that evaluation harness executes all 4 benchmarks and returns summary."""
    summary, has_regressions = run_full_evaluation()
    
    assert summary.run_id.startswith("EVAL-")
    assert len(summary.metrics) >= 4
    assert has_regressions is False
    assert summary.overall_status == "PASS"


def test_orbital_physics_within_nominal_envelope():
    """Validates that orbital physics calculation returns realistic LEO orbital periods."""
    period = evaluate_orbital_physics()
    assert 92.0 <= period <= 98.0
