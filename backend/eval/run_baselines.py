"""Baseline Models Evaluation & Decision Systems Benchmark Runner.

Executes all 6 pure ML/heuristic candidate ranking models and 2 Decision Systems
on held-out test splits, computes precision metrics, feasibility rates, and latencies,
and outputs both structured JSON and cleanly separated benchmark tables.
"""

import sys
import json
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.intelligence.baselines import get_baseline_suite

OUTPUT_REPORT = BACKEND_DIR / "eval" / "baseline_comparison_report.json"


def main():
    print("=" * 96)
    print("           ORBIT-X BENCHMARK EVALUATION HARNESS (ML & DECISION SYSTEMS)           ")
    print("=" * 96)
    print("Empirically evaluating candidate ranking ML models and integrated decision pipelines...\n")

    suite = get_baseline_suite()
    report = suite.run_full_comparison()

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    # ----------------------------------------------------
    # Table 1: Pure ML & Heuristic Evaluation
    # ----------------------------------------------------
    print("-" * 96)
    print(" TABLE 1: MACHINE LEARNING EVALUATION (Pure Predictive & Ranking Models)")
    print("-" * 96)
    ml_header = f"{'Model Architecture':<42} | {'Category':<14} | {'Top-1 %':<8} | {'MAE':<7} | {'F1':<6} | {'p50 (ms)':<9} | {'Throughput (inf/s)':<18}"
    print(ml_header)
    print("-" * len(ml_header))

    for m in report.ml_models:
        print(
            f"{m.model_name:<42} | {m.model_category:<14} | {m.top1_agreement_pct:<8.1f} | {m.mae:<7.2f} | {m.f1_score:<6.3f} | {m.latency_ms_p50:<9.3f} | {m.throughput_inferences_sec:<18.1f}"
        )

    # ----------------------------------------------------
    # Table 2: Decision Systems Evaluation
    # ----------------------------------------------------
    print("\n" + "-" * 96)
    print(" TABLE 2: DECISION SYSTEMS EVALUATION (Constraint Safety & End-to-End Latency)")
    print("-" * 96)
    dec_header = f"{'Decision System':<30} | {'Constraint Violations':<30} | {'Feasibility':<12} | {'Utility':<8} | {'Opt Latency':<12} | {'E2E Latency':<12}"
    print(dec_header)
    print("-" * len(dec_header))

    for d in report.decision_systems:
        opt_lat_str = f"{d.optimization_latency_ms_p50:.2f} ms" if d.optimization_latency_ms_p50 is not None else "N/A (ML only)"
        e2e_lat_str = f"{d.end_to_end_latency_ms_p50:.3f} ms"
        print(
            f"{d.system_name:<30} | {d.constraint_violations:<30} | {d.feasibility_rate_pct:<11.1f}% | {d.decision_utility_pct:<7.1f}% | {opt_lat_str:<12} | {e2e_lat_str:<12}"
        )

    print("\n" + "=" * 96)
    print(f"Champion ML Model:       {report.champion_ml_model}")
    print(f"Champion Decision System: {report.champion_decision_system}")
    print(f"Selection Rationale:     {report.selection_rationale}")
    print(f"Saved benchmark report to: {OUTPUT_REPORT}")
    print("=" * 96)


if __name__ == "__main__":
    main()
