"""Unit Tests for Rigorous, Reproducible AI Evaluation Suite across all 9 Subsystems."""

import pytest
from app.intelligence.rigorous_ai_evaluator import (
    RigorousAIEvaluator,
    get_rigorous_ai_evaluator,
)


def test_rigorous_evaluator_singleton():
    """Validates singleton getter for RigorousAIEvaluator."""
    evaluator1 = get_rigorous_ai_evaluator()
    evaluator2 = get_rigorous_ai_evaluator()
    assert evaluator1 is evaluator2


def test_rigorous_rag_evaluation():
    """Validates RAG metrics: Recall@K, Precision@K, MRR."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_rag()

    assert comp.component_name.startswith("RAG")
    metric_names = [m.metric_name for m in comp.metrics]
    assert "Recall@1" in metric_names
    assert "Recall@3" in metric_names
    assert "Recall@5" in metric_names
    assert "Precision@1" in metric_names
    assert "Precision@3" in metric_names
    assert "Precision@5" in metric_names
    assert "MRR (Mean Reciprocal Rank)" in metric_names

    for m in comp.metrics:
        assert m.baseline_value >= 0.0
        assert m.improved_value >= m.baseline_value
        assert m.percentage_improvement >= 0.0
        assert m.formula is not None and len(m.formula) > 0
        assert m.sample_size > 0


def test_rigorous_retrieval_evaluation():
    """Validates Retrieval metrics: NDCG@3, NDCG@5, NDCG@10."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_retrieval()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "NDCG@3" in metric_names
    assert "NDCG@5" in metric_names
    assert "NDCG@10" in metric_names

    for m in comp.metrics:
        assert 0.0 <= m.baseline_value <= 1.0
        assert 0.0 <= m.improved_value <= 1.0
        assert m.improved_value >= m.baseline_value
        assert m.percentage_improvement >= 0.0


def test_rigorous_agent_evaluation():
    """Validates Agent metrics: Task Success Rate, Tool Selection, Groundedness, Unsupported Claim Rate."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_agent()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "Task Success Rate" in metric_names
    assert "Tool-Selection Accuracy" in metric_names
    assert "Groundedness" in metric_names
    assert "Unsupported-Claim Rate" in metric_names

    for m in comp.metrics:
        if m.metric_name == "Unsupported-Claim Rate":
            # For error rates, improved should be lower than baseline
            assert m.improved_value <= m.baseline_value
        else:
            assert m.improved_value >= m.baseline_value


def test_rigorous_mcp_evaluation():
    """Validates MCP Tool-Call Success Rate."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_mcp()

    assert any("Tool-Call Success Rate" in m.metric_name for m in comp.metrics)
    m = comp.metrics[0]
    assert m.baseline_value > 0.0
    assert m.improved_value >= 90.0


def test_rigorous_context_evaluation():
    """Validates Context Quality: Freshness Violation Rate, Metadata Completeness."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_context()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "Metadata Completeness" in metric_names
    assert "Freshness Violation Rate" in metric_names


def test_rigorous_anomaly_evaluation():
    """Validates Anomaly Detection metrics: Precision, Recall, F1 Score, False Positive Rate."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_anomaly_model()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "Precision" in metric_names
    assert "Recall (Fault Coverage)" in metric_names
    assert "F1 Score" in metric_names
    assert "False Positive Rate (FPR)" in metric_names

    f1_metric = next(m for m in comp.metrics if m.metric_name == "F1 Score")
    assert f1_metric.improved_value >= 0.80
    assert f1_metric.improved_value > f1_metric.baseline_value


def test_rigorous_ranking_evaluation():
    """Validates Neural Candidate Ranking: Top-1 and Top-3 accuracy."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_ranking()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "Top-1 Ranking Accuracy" in metric_names
    assert "Top-3 Ranking Accuracy" in metric_names
    assert "Mean Absolute Error (MAE)" in metric_names


def test_rigorous_decision_evaluation():
    """Validates Decision Systems: Constraint Violation Rate (0.0%), Feasibility, Utility."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_decision_system()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "Constraint Violation Rate" in metric_names
    assert "Schedule Feasibility Rate" in metric_names
    assert "Global Decision Utility" in metric_names

    viol_metric = next(m for m in comp.metrics if "Violation Rate" in m.metric_name)
    assert viol_metric.improved_value == 0.0  # 100% violation elimination


def test_rigorous_api_performance_evaluation():
    """Validates API Latencies: p50, p95, p99."""
    evaluator = get_rigorous_ai_evaluator()
    comp = evaluator.evaluate_api_performance()

    metric_names = [m.metric_name for m in comp.metrics]
    assert "API Latency (p50 / Median)" in metric_names
    assert "API Latency (p95)" in metric_names
    assert "API Latency (p99)" in metric_names

    for m in comp.metrics:
        # Latency improved is lower than baseline
        assert m.improved_value < m.baseline_value


def test_full_rigorous_evaluation_report():
    """Validates complete multi-component report generation."""
    evaluator = get_rigorous_ai_evaluator()
    report = evaluator.run_full_rigorous_evaluation()

    assert report.total_components == 9
    assert report.total_metrics_evaluated >= 24
    assert report.overall_status == "ALL_GATES_PASSED"
    assert len(report.components) == 9
    assert report.executive_summary is not None
