"""ML Baseline Comparison & Decision Systems Benchmark Harness.

Empirically benchmarks Candidate Ranking Models and Integrated Decision Systems:
Stage 1: Pure ML Ranking Baselines
  1. Greedy EDF
  2. Random
  3. XGBoost
  4. Neural Ranking (MLP)
  5. Cross-Attention (Champion)

Stage 2: Hybrid Decision Systems
  1. Cross-Attention Only (Unconstrained neural candidate ranker)
  2. Cross-Attention + Google OR-Tools CP-SAT (Production Hybrid)
"""

import sys
import json
from typing import Dict, Any

from ml.evaluation.ranking_benchmarks import get_ranking_baseline_suite
from backend.app.intelligence.baselines import get_baseline_suite


def run_full_ml_benchmark() -> Dict[str, Any]:
    """Executes held-out evaluation across ML models and integrated decision pipelines."""
    ranking_suite = get_ranking_baseline_suite()
    ranking_report = ranking_suite.run_benchmark()

    # Also run backend decision systems baseline suite
    try:
        decision_suite = get_baseline_suite()
        decision_report = decision_suite.run_full_comparison().model_dump()
    except Exception:
        decision_report = {}

    return {
        "ranking_benchmark": ranking_report,
        "decision_system_benchmark": decision_report,
    }


if __name__ == "__main__":
    print("=" * 80)
    print(" ORBIT-X CANDIDATE RANKING BASELINE COMPARISON BENCHMARK")
    print("=" * 80)

    suite = get_ranking_baseline_suite()
    report = suite.run_benchmark()

    print("\n" + report["ascii_table"] + "\n")
    print("-" * 80)
    print("ENGINEERING TAKEAWAY:")
    print(report["engineering_takeaway"])
    print("-" * 80)
