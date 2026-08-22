"""FastAPI Router for ML Baseline Benchmarks, Model Evaluation & Feature Ablation Experiments."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.core.schemas import BaselineComparisonReport, FeatureAblationReport
from app.intelligence.baselines import get_baseline_suite
from eval.run_ablation import run_ablation_experiment

router = APIRouter(prefix="/api/experiments", tags=["ML Experiments & Evaluation"])

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BASELINE_REPORT_PATH = BACKEND_DIR / "eval" / "baseline_comparison_report.json"
ABLATION_REPORT_PATH = BACKEND_DIR / "eval" / "feature_ablation_report.json"


@router.get("/baselines", response_model=BaselineComparisonReport)
async def get_baseline_comparison_report():
    """Returns the latest multi-model baseline comparison report."""
    if BASELINE_REPORT_PATH.exists():
        with open(BASELINE_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return BaselineComparisonReport(**data)
    # Fallback to generating live
    suite = get_baseline_suite()
    return suite.run_full_comparison()


@router.post("/baselines/run", response_model=BaselineComparisonReport)
async def trigger_baseline_comparison():
    """Runs a fresh comparative evaluation across all 7 baseline models against CP-SAT ground truth."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()
    with open(BASELINE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
    return report


@router.get("/ablation", response_model=FeatureAblationReport)
async def get_feature_ablation_report():
    """Returns the latest feature ablation study report."""
    if ABLATION_REPORT_PATH.exists():
        with open(ABLATION_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return FeatureAblationReport(**data)
    return run_ablation_experiment()


@router.post("/ablation/run", response_model=FeatureAblationReport)
async def trigger_feature_ablation():
    """Executes a fresh feature ablation experiment across battery, priority, temporal, and spatial subsets."""
    report = run_ablation_experiment()
    with open(ABLATION_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
    return report
