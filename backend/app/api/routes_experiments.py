"""FastAPI Router for ML Baseline Benchmarks, Model Evaluation, Feature Ablation & Model Registry."""

import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional

from app.core.schemas import BaselineComparisonReport, FeatureAblationReport
from app.intelligence.baselines import get_baseline_suite
from eval.run_ablation import run_ablation_experiment
from ml.registry import get_model_registry
from ml.evaluation.ranking_benchmarks import get_ranking_baseline_suite

router = APIRouter(prefix="/api/experiments", tags=["ML Experiments & Evaluation"])

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
BASELINE_REPORT_PATH = BACKEND_DIR / "eval" / "baseline_comparison_report.json"
ABLATION_REPORT_PATH = BACKEND_DIR / "eval" / "feature_ablation_report.json"
RANKING_BASELINE_REPORT_PATH = BACKEND_DIR / "eval" / "ranking_baseline_comparison_report.json"


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
    """Runs a fresh comparative evaluation across all baseline models against CP-SAT ground truth."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()
    with open(BASELINE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)
    return report


@router.get("/ranking-baselines")
async def get_ranking_baseline_report():
    """Returns the authoritative 5-paradigm ranking baseline comparison table."""
    if RANKING_BASELINE_REPORT_PATH.exists():
        with open(RANKING_BASELINE_REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    suite = get_ranking_baseline_suite()
    report = suite.run_benchmark()
    return report


@router.post("/ranking-baselines/run")
async def trigger_ranking_baseline_comparison():
    """Executes a fresh 5-paradigm ranking baseline benchmark run (Greedy, Random, XGBoost, Neural, Cross-Attention)."""
    suite = get_ranking_baseline_suite()
    report = suite.run_benchmark()
    RANKING_BASELINE_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RANKING_BASELINE_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


@router.get("/model-registry")
async def list_registered_models(
    task_type: Optional[str] = Query(None, description="Filter by task domain: ranking, anomaly, forecasting"),
    status: Optional[str] = Query(None, description="Filter by status: CHAMPION, PRODUCTION, STAGING, SHADOW, BASELINE, EXPERIMENTAL"),
):
    """Lists all models registered in the ORBIT-X enterprise Model Registry."""
    registry = get_model_registry()
    cards = registry.list_models(task_type=task_type, status=status)
    return {
        "total_models": len(cards),
        "models": [c.model_dump() for c in cards],
    }


@router.get("/model-registry/champions")
async def get_champion_models():
    """Retrieves the active champion models for ranking, anomaly detection, and forecasting."""
    registry = get_model_registry()
    ranking_champ = registry.get_champion("ranking")
    anomaly_champ = registry.get_champion("anomaly")
    forecasting_champ = registry.get_champion("forecasting")
    return {
        "ranking": ranking_champ.model_dump() if ranking_champ else None,
        "anomaly": anomaly_champ.model_dump() if anomaly_champ else None,
        "forecasting": forecasting_champ.model_dump() if forecasting_champ else None,
    }


@router.get("/model-registry/{model_id}")
async def get_model_details(model_id: str):
    """Retrieves full ModelCard governance metadata for a specific model_id."""
    registry = get_model_registry()
    card = registry.get_model(model_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found in registry.")
    return card.model_dump()


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
