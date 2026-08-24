"""FastAPI Router for Benchmarking & Policy Evaluation."""

import asyncio
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional

from app.core.limiter import limiter
from app.core.schemas import (
    BenchmarkResult,
    RigorousAIEvaluationReport,
    AgentEvaluationHarnessReport,
    DeliberateFailureSuiteReport,
    DeliberateFailureResult,
    DeliberateFailureCaseId,
)


from app.simulation.benchmark import run_benchmark_comparison, run_multi_seed_benchmark
from app.intelligence.rigorous_ai_evaluator import get_rigorous_ai_evaluator

router = APIRouter(prefix="/api/benchmarks", tags=["Benchmarks"])


class BenchmarkRunRequest(BaseModel):
    seed: int = 42
    num_missions: int = 24
    horizon_s: float = 5400.0


class MultiSeedBenchmarkRequest(BaseModel):
    seeds: List[int] = [42, 101, 777]
    num_missions: int = 24


@router.get("/run", response_model=List[BenchmarkResult])
@limiter.limit("20/minute")
async def run_benchmark_get(request: Request, seed: int = 42, num_missions: int = 24, horizon_s: float = 5400.0):
    """GET handler for benchmark run (called by frontend with no body). Executes comparative evaluation across all 6 authoritative schedulers."""
    results = await asyncio.to_thread(
        run_benchmark_comparison,
        seed=seed,
        num_missions=num_missions,
        horizon_s=horizon_s,
    )
    return results


@router.post("/run", response_model=List[BenchmarkResult])
@limiter.limit("20/minute")
async def run_benchmark(request: Request, req: BenchmarkRunRequest):
    """POST handler for benchmark run with body. Executes comparative evaluation across all 6 authoritative schedulers off the main event loop."""
    results = await asyncio.to_thread(
        run_benchmark_comparison,
        seed=req.seed,
        num_missions=req.num_missions,
        horizon_s=req.horizon_s,
    )
    return results


@router.post("/multi_seed")
@limiter.limit("10/minute")
async def run_multi_seed(request: Request, req: MultiSeedBenchmarkRequest):
    """Runs multi-seed benchmarking returning statistical distributions (mean, std, regret) across 6 schedulers."""
    summary = await asyncio.to_thread(
        run_multi_seed_benchmark,
        seeds=req.seeds,
        num_missions=req.num_missions,
    )
    return summary


# ----------------------------------------------------------------------
# Rigorous Multi-Component AI Evaluation Endpoints
# ----------------------------------------------------------------------

@router.get("/ai-evaluation/latest", response_model=RigorousAIEvaluationReport)
@limiter.limit("30/minute")
async def get_latest_ai_evaluation(request: Request):
    """Returns the latest audited rigorous evaluation report across all 9 AI components."""
    evaluator = get_rigorous_ai_evaluator()
    report = await asyncio.to_thread(evaluator.get_latest_report)
    return report


@router.post("/ai-evaluation/run", response_model=RigorousAIEvaluationReport)
@router.get("/ai-evaluation/run", response_model=RigorousAIEvaluationReport)
@limiter.limit("10/minute")
async def run_rigorous_ai_evaluation(request: Request):
    """Executes a fresh live benchmark run across all 9 AI components and returns the updated report."""
    evaluator = get_rigorous_ai_evaluator()
    report = await asyncio.to_thread(evaluator.run_full_rigorous_evaluation)
    return report


# ----------------------------------------------------------------------
# Enterprise Agent Evaluation Harness Endpoints (128 Questions)
# ----------------------------------------------------------------------

@router.get("/agent-harness/latest", response_model=AgentEvaluationHarnessReport)
@limiter.limit("30/minute")
async def get_latest_agent_harness_evaluation(request: Request):
    """Returns the latest audited evaluation report from the 128-question Agent Evaluation Harness."""
    from app.context.evaluation.agent_evaluation_harness import get_agent_evaluation_harness
    harness = get_agent_evaluation_harness()
    report = await asyncio.to_thread(harness.get_latest_report)
    return report


@router.post("/agent-harness/run", response_model=AgentEvaluationHarnessReport)
@router.get("/agent-harness/run", response_model=AgentEvaluationHarnessReport)
@limiter.limit("10/minute")
async def run_agent_harness_evaluation(
    request: Request,
    category_filter: Optional[str] = None,
    sample_limit: Optional[int] = None,
):
    """
    Executes the full 128-question Agent Evaluation Harness (or filtered category subset)
    across the multi-source pipeline and returns the scorecard.
    """
    from app.context.evaluation.agent_evaluation_harness import get_agent_evaluation_harness
    harness = get_agent_evaluation_harness()
    report = await asyncio.to_thread(
        harness.run_full_benchmark,
        category_filter=category_filter,
        sample_limit=sample_limit,
    )
    return report


@router.get("/agent-harness/questions")
@limiter.limit("30/minute")
async def get_agent_harness_questions(request: Request, category: Optional[str] = None):
    """Returns the catalog of benchmark evaluation questions and metadata."""
    from app.context.evaluation.benchmark_dataset import get_benchmark_dataset_manager
    from app.core.schemas import AgentBenchmarkCategory
    mgr = get_benchmark_dataset_manager()
    questions = mgr.get_all()
    if category:
        target_cat = next((c for c in AgentBenchmarkCategory if c.value == category), None)
        if target_cat:
            questions = [q for q in questions if q.category == target_cat]
    return {
        "total_questions": len(questions),
        "questions": [q.model_dump() for q in questions],
    }


# ----------------------------------------------------------------------
# Deliberate Failure Testing & Safe Degradation Endpoints (5 Scenarios)
# ----------------------------------------------------------------------

@router.get("/deliberate-failure/latest", response_model=DeliberateFailureSuiteReport)
@limiter.limit("30/minute")
async def get_latest_deliberate_failure_report(request: Request):
    """Returns the latest deliberate failure testing audit report."""
    from app.intelligence.deliberate_failure_tester import get_deliberate_failure_tester
    tester = get_deliberate_failure_tester()
    report = await asyncio.to_thread(tester.get_latest_report)
    return report


@router.post("/deliberate-failure/run", response_model=DeliberateFailureSuiteReport)
@router.get("/deliberate-failure/run", response_model=DeliberateFailureSuiteReport)
@limiter.limit("10/minute")
async def run_deliberate_failure_suite(request: Request):
    """Executes all 5 deliberate failure test cases and returns the audit report."""
    from app.intelligence.deliberate_failure_tester import get_deliberate_failure_tester
    tester = get_deliberate_failure_tester()
    report = await asyncio.to_thread(tester.run_all_cases)
    return report


@router.post("/deliberate-failure/case/{case_id}", response_model=DeliberateFailureResult)
@limiter.limit("20/minute")
async def run_single_deliberate_failure_case(request: Request, case_id: DeliberateFailureCaseId):
    """Executes a single deliberate failure scenario on demand."""
    from app.intelligence.deliberate_failure_tester import get_deliberate_failure_tester
    tester = get_deliberate_failure_tester()
    if case_id == DeliberateFailureCaseId.CASE_1_STALE_DATA:
        return await asyncio.to_thread(tester.run_case_1_stale_data)
    elif case_id == DeliberateFailureCaseId.CASE_2_DEPRECATED_DATASET:
        return await asyncio.to_thread(tester.run_case_2_deprecated_dataset)
    elif case_id == DeliberateFailureCaseId.CASE_3_MISSING_LINEAGE:
        return await asyncio.to_thread(tester.run_case_3_missing_lineage)
    elif case_id == DeliberateFailureCaseId.CASE_4_MCP_TOOL_503:
        return await asyncio.to_thread(tester.run_case_4_mcp_tool_503)
    elif case_id == DeliberateFailureCaseId.CASE_5_NONEXISTENT_SATELLITE:
        return await asyncio.to_thread(tester.run_case_5_nonexistent_satellite)
    else:
        return await asyncio.to_thread(tester.run_case_1_stale_data)



