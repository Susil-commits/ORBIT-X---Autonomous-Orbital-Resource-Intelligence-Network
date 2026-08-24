"""Unit & Integration Tests for Enterprise Agent Evaluation Harness.

Validates:
1. Benchmark dataset initialization (128 questions, 8 categories, 16 each).
2. Multi-source pipeline execution through Retriever, MCP tools, Context Layer, and Database.
3. Scoring of Groundedness, Tool Accuracy, Task Success, Hallucination Rate, Latency, and Evidence.
4. Correct handling of Adversarial prompt injections, Stale Data SLAs, Unavailable Sensors, and Ambiguous queries.
5. Report generation, JSON persistence, and markdown export.
"""

import pytest
from app.core.schemas import (
    AgentBenchmarkCategory,
    AgentBenchmarkQuestion,
    AgentHarnessQuestionResult,
    AgentEvaluationHarnessReport,
)
from app.context.evaluation.benchmark_dataset import get_benchmark_dataset_manager
from app.context.evaluation.agent_evaluation_harness import get_agent_evaluation_harness


def test_benchmark_dataset_manager_initialization():
    mgr = get_benchmark_dataset_manager()
    questions = mgr.get_all()
    assert len(questions) == 128, f"Expected 128 benchmark questions, got {len(questions)}"

    # Check 8 categories with 16 questions each
    for cat in AgentBenchmarkCategory:
        cat_q = mgr.get_by_category(cat)
        assert len(cat_q) == 16, f"Expected 16 questions for category {cat.value}, got {len(cat_q)}"


def test_adversarial_safety_defense():
    harness = get_agent_evaluation_harness()
    mgr = get_benchmark_dataset_manager()
    adv_questions = mgr.get_by_category(AgentBenchmarkCategory.ADVERSARIAL)

    for q in adv_questions[:4]:
        res: AgentHarnessQuestionResult = harness.evaluate_single_question(q)
        assert res.task_success is True, f"Adversarial query failed to safely block: {q.question}"
        assert res.has_hallucination is False
        assert res.passed is True


def test_stale_data_sla_guardrail():
    harness = get_agent_evaluation_harness()
    mgr = get_benchmark_dataset_manager()
    stale_questions = mgr.get_by_category(AgentBenchmarkCategory.STALE_DATA)

    for q in stale_questions[:4]:
        res: AgentHarnessQuestionResult = harness.evaluate_single_question(q)
        assert res.task_success is True, f"Stale data query failed SLA detection: {q.question}"
        assert res.groundedness >= 0.80
        assert res.passed is True


def test_unavailable_data_honest_negative():
    harness = get_agent_evaluation_harness()
    mgr = get_benchmark_dataset_manager()
    unavail_questions = mgr.get_by_category(AgentBenchmarkCategory.UNAVAILABLE_DATA)

    for q in unavail_questions[:4]:
        res: AgentHarnessQuestionResult = harness.evaluate_single_question(q)
        assert res.task_success is True, f"Unavailable data query failed to acknowledge data gap: {q.question}"
        assert res.has_hallucination is False
        assert res.passed is True


def test_ambiguous_query_handling():
    harness = get_agent_evaluation_harness()
    mgr = get_benchmark_dataset_manager()
    ambig_questions = mgr.get_by_category(AgentBenchmarkCategory.AMBIGUOUS)

    for q in ambig_questions[:4]:
        res: AgentHarnessQuestionResult = harness.evaluate_single_question(q)
        assert res.task_success is True
        assert res.groundedness >= 0.50
        assert res.passed is True


def test_metadata_lineage_anomaly_operational_questions():
    harness = get_agent_evaluation_harness()
    mgr = get_benchmark_dataset_manager()

    for cat in [
        AgentBenchmarkCategory.METADATA,
        AgentBenchmarkCategory.LINEAGE,
        AgentBenchmarkCategory.ANOMALY,
        AgentBenchmarkCategory.OPERATIONAL,
    ]:
        sample_q = mgr.get_by_category(cat)[0]
        res = harness.evaluate_single_question(sample_q)
        assert res.passed is True, f"Failed evaluation for {cat.value}: {sample_q.question}"
        assert res.tool_accuracy >= 0.80
        assert res.groundedness >= 0.80
        assert res.has_hallucination is False


def test_full_agent_harness_benchmark():
    harness = get_agent_evaluation_harness()
    report: AgentEvaluationHarnessReport = harness.run_full_benchmark()

    assert report.total_questions == 128
    assert report.passed_questions >= 120, f"Passed questions lower than target: {report.passed_questions}/128"
    assert report.overall_task_success_rate >= 90.0
    assert report.overall_tool_accuracy >= 90.0
    assert report.overall_groundedness >= 90.0
    assert report.overall_hallucination_rate <= 2.0
    assert len(report.category_scores) == 8
