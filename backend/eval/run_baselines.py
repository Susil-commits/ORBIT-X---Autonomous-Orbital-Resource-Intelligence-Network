"""Baseline Models Evaluation & Comparative Experiment Runner.

Executes all 7 baseline models on the held-out test split, computes
Top-1 Agreement, MAE, Accuracy, F1, Latency, and Throughput,
and outputs both structured JSON and a formatted benchmark table.
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
    print("=" * 80)
    print("        ORBIT-X MACHINE LEARNING BASELINE COMPARISON EXPERIMENT         ")
    print("=" * 80)
    print("Evaluating models against Google OR-Tools CP-SAT ground truth on held-out test split...\n")

    suite = get_baseline_suite()
    report = suite.run_full_comparison()

    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    header = f"{'Model Name':<38} | {'Top-1 %':<8} | {'MAE':<7} | {'F1':<6} | {'p50 (ms)':<9} | {'Throughput (inf/s)':<18}"
    print(header)
    print("-" * len(header))

    for m in report.models:
        print(
            f"{m.model_name:<38} | {m.top1_agreement_pct:<8.1f} | {m.mae:<7.2f} | {m.f1_score:<6.3f} | {m.latency_ms_p50:<9.3f} | {m.throughput_inferences_sec:<18.1f}"
        )

    print("\n" + "=" * 80)
    print(f"Champion Model: {report.champion_model}")
    print(f"Selection Rationale: {report.selection_rationale}")
    print(f"Saved benchmark report to: {OUTPUT_REPORT}")
    print("=" * 80)


if __name__ == "__main__":
    main()
