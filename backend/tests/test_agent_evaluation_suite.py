"""Unit Tests for Reproducible Agent Evaluation Suite (7 Canonical Dimensions)."""

import pytest
from app.context.evaluation.agent_evaluator import (
    AgentEvaluationSuite,
    get_agent_evaluation_suite,
)


def test_agent_evaluation_suite_singleton():
    """Validates singleton getter for AgentEvaluationSuite."""
    suite1 = get_agent_evaluation_suite()
    suite2 = get_agent_evaluation_suite()
    assert suite1 is suite2


def test_agent_evaluation_suite_seven_dimensions():
    """Validates that the evaluation suite measures all 7 canonical dimensions on real scenarios."""
    suite = get_agent_evaluation_suite()
    report = suite.run_suite()

    assert report.total_scenarios >= 5
    assert report.passed_scenarios >= 4
    assert report.overall_score_pct >= 85.0

    dim_keys = [d.dimension_key for d in report.dimensions]
    expected_dimensions = [
        "context_relevance",
        "tool_selection_accuracy",
        "evidence_completeness",
        "unsupported_claim_rate",
        "missing_context_detection",
        "tool_failure_recovery",
        "decision_consistency",
    ]
    for exp_dim in expected_dimensions:
        assert exp_dim in dim_keys

    # Check each dimension bounds and structure
    for dim in report.dimensions:
        assert 0.0 <= dim.score <= 1.0
        assert 0.0 <= dim.score_pct <= 100.0
        assert dim.description is not None and len(dim.description) > 0
        assert dim.evaluation_formula is not None and len(dim.evaluation_formula) > 0
        assert dim.tested_cases >= 5
        assert dim.passed_cases >= 4

    # Check scenario details
    for scen in report.scenarios:
        assert scen.scenario_id is not None
        assert scen.context_relevance_score >= 0.70
        assert scen.tool_accuracy_score >= 0.70
        assert scen.evidence_completeness_score >= 0.60
        assert scen.execution_time_ms > 0.0


def test_agent_evaluation_pipeline_stages():
    """Validates that the 13 canonical pipeline stages are benchmarked."""
    suite = get_agent_evaluation_suite()
    report = suite.get_latest_report()

    expected_stages = [
        "DATA", "features", "ML/anomaly", "prediction", "SHAP",
        "context", "RAG", "agent/MCP", "CP-SAT", "decision",
        "trust", "human feedback", "monitoring"
    ]
    assert report.pipeline_stages_evaluated == expected_stages
