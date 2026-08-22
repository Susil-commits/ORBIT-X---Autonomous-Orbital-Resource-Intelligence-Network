"""Feature Ablation Benchmark.

Measures the empirical performance impact and failure modes when removing feature groups
(Elevation/Slew Geometry, Temporal Deadlines, Battery Energy, Mission Priority).
"""

from typing import Dict, Any
from backend.eval.run_ablation import run_feature_ablation_experiment


def run_ablation_benchmark() -> Dict[str, Any]:
    """Runs systematic feature group ablation studies."""
    return run_feature_ablation_experiment()


if __name__ == "__main__":
    import json
    results = run_ablation_benchmark()
    print(json.dumps(results, indent=2))
