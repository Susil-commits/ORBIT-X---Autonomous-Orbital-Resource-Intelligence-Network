"""ML Baseline Comparison Benchmark Harness.

Empirically compares:
1. Random Assignment Heuristic
2. Greedy Earliest-Deadline-First (EDF)
3. Ridge Linear Regression
4. Random Forest / Gradient Boosting
5. Multi-Layer Perceptron (MLP)
6. Multi-Head Cross-Attention Neural Ranker
7. Hybrid Neural + CP-SAT Optimizer

Records Precision, Recall, F1, MAE/RMSE, inference latency, throughput, and decision quality.
"""

from typing import List, Dict, Any
from backend.app.intelligence.baselines import get_baseline_suite


def run_full_ml_benchmark() -> Dict[str, Any]:
    """Executes held-out evaluation across all 7 model architectures."""
    suite = get_baseline_suite()
    report = suite.run_full_comparison()
    return report.model_dump()


if __name__ == "__main__":
    import json
    results = run_full_ml_benchmark()
    print(json.dumps(results, indent=2))
