"""ML Baseline Comparison & Decision Systems Benchmark Harness.

Empirically benchmarks:

Stage 1: Pure ML & Heuristic Evaluation
1. Random Assignment Heuristic
2. Greedy Earliest-Deadline-First (EDF)
3. Ridge Linear Regression
4. Random Forest / Gradient Boosting Regressor
5. Multi-Layer Perceptron (BidValueMLP)
6. Multi-Head Cross-Attention Neural Ranker (ConstellationCrossAttentionNet)

Stage 2: Decision Systems Evaluation
1. Cross-Attention Only (Unconstrained neural candidate ranker)
2. Cross-Attention + Google OR-Tools CP-SAT (Hybrid decision system)

Evaluates precision, ranking concordance, MAE, inference latency, throughput,
constraint violations, feasibility rate, decision utility, and solver latency.
"""

from typing import List, Dict, Any
from backend.app.intelligence.baselines import get_baseline_suite


def run_full_ml_benchmark() -> Dict[str, Any]:
    """Executes held-out evaluation across ML models and integrated decision pipelines."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()
    return report.model_dump()


if __name__ == "__main__":
    import json
    results = run_full_ml_benchmark()
    print(json.dumps(results, indent=2))
