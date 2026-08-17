"""Automated Evaluation & Regression Scoring Harness for ORBIT-X.

Runs standard benchmark scenarios, evaluates CP-SAT solver performance, checks
the Neural Network's top-1 agreement rate and MAE, verifies TreeSHAP model drift,
and enforces physical orbital period consistency against stored baseline scores.
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add backend directory to sys.path if not present
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.schemas import EvalMetric, EvalRunSummary
from app.simulation.benchmark import run_benchmark_comparison
from app.intelligence.bid_value_network import get_bid_value_predictor
from app.intelligence.shap_explainer import get_shap_explainer
from app.physics.orbit_propagator import compute_orbital_period_minutes, create_initial_constellation
from training.train_bid_network import evaluate_model
from training.collect_cpsat_labels import DATASET_FILE

EVAL_DIR = Path(__file__).resolve().parent
BASELINE_FILE = EVAL_DIR / "baseline_scores.json"
REPORT_FILE = EVAL_DIR / "latest_eval_report.json"


def evaluate_orbital_physics() -> float:
    """Computes measured orbital period of standard constellation satellites."""
    sats = create_initial_constellation(source="synthetic")
    sat = sats[0]
    period_min = compute_orbital_period_minutes(sat.keplerian.semi_major_axis_km)
    return round(period_min, 3)


def run_full_evaluation() -> Tuple[EvalRunSummary, bool]:
    """
    Runs all benchmark and ML evaluations and compares against stored baselines.
    Returns: (EvalRunSummary, has_regressions: bool)
    """
    if not BASELINE_FILE.exists():
        raise FileNotFoundError(f"Baseline configuration '{BASELINE_FILE}' not found.")
        
    with open(BASELINE_FILE, "r", encoding="utf-8") as f:
        baseline_cfg = json.load(f)["baselines"]
        
    metrics_list: List[EvalMetric] = []
    regressions: List[str] = []
    
    print("=" * 65)
    print("      ORBIT-X AUTOMATED EVALUATION & REGRESSION HARNESS       ")
    print("=" * 65)
    
    # ----------------------------------------------------
    # 1. CP-SAT Benchmark Evaluation
    # ----------------------------------------------------
    print("\n[1/4] Running CP-SAT Constellation Scheduler Benchmark...")
    bench_results = run_benchmark_comparison(seed=42, num_missions=24)
    cpsat_bench = next((b for b in bench_results if "CP-SAT" in b.scheduler_name), bench_results[-1])
    
    comp_rate = cpsat_bench.completion_rate_pct
    comp_base = baseline_cfg["cpsat_completion_rate_pct"]
    comp_status = "PASS" if comp_rate >= comp_base["min_allowable"] else "FAIL"
    if comp_status == "FAIL":
        regressions.append(f"CP-SAT Completion Rate ({comp_rate:.1f}%) < Minimum ({comp_base['min_allowable']}%)")
    metrics_list.append(
        EvalMetric(
            metric_name="cpsat_completion_rate_pct",
            baseline_value=comp_base["target"],
            current_value=comp_rate,
            delta=round(comp_rate - comp_base["target"], 2),
            status=comp_status,
            threshold=comp_base["min_allowable"],
        )
    )
    
    reward_yield = cpsat_bench.total_reward_yield
    reward_base = baseline_cfg["cpsat_reward_yield"]
    reward_status = "PASS" if reward_yield >= reward_base["min_allowable"] else "FAIL"
    if reward_status == "FAIL":
        regressions.append(f"CP-SAT Reward Yield ({reward_yield:.1f}) < Minimum ({reward_base['min_allowable']})")
    metrics_list.append(
        EvalMetric(
            metric_name="cpsat_reward_yield",
            baseline_value=reward_base["target"],
            current_value=reward_yield,
            delta=round(reward_yield - reward_base["target"], 2),
            status=reward_status,
            threshold=reward_base["min_allowable"],
        )
    )
    print(f"  -> Completion Rate: {comp_rate:.1f}% ({comp_status}) | Reward Yield: {reward_yield:.1f} ({reward_status})")
    
    # ----------------------------------------------------
    # 2. Neural Network Evaluation
    # ----------------------------------------------------
    print("\n[2/4] Evaluating Neural Network (BidValueMLP) against CP-SAT...")
    predictor = get_bid_value_predictor()
    
    test_samples = []
    if DATASET_FILE.exists():
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            all_samples = json.load(f).get("samples", [])
            test_samples = all_samples[int(0.8 * len(all_samples)):]
            
    nn_results = evaluate_model(predictor.model, test_samples)
    
    agreement_rate = nn_results["top1_agreement_pct"]
    agreement_base = baseline_cfg["nn_top1_agreement_rate_pct"]
    ag_status = "PASS" if agreement_rate >= agreement_base["min_allowable"] else "FAIL"
    if ag_status == "FAIL":
        regressions.append(f"NN Top-1 Agreement Rate ({agreement_rate:.1f}%) < Minimum ({agreement_base['min_allowable']}%)")
    metrics_list.append(
        EvalMetric(
            metric_name="nn_top1_agreement_rate_pct",
            baseline_value=agreement_base["target"],
            current_value=agreement_rate,
            delta=round(agreement_rate - agreement_base["target"], 2),
            status=ag_status,
            threshold=agreement_base["min_allowable"],
        )
    )
    
    mae_score = nn_results["mae"]
    mae_base = baseline_cfg["nn_mae_score"]
    mae_status = "PASS" if mae_score <= mae_base["max_allowable"] else "FAIL"
    if mae_status == "FAIL":
        regressions.append(f"NN MAE Score ({mae_score:.2f}) > Maximum Allowable ({mae_base['max_allowable']})")
    metrics_list.append(
        EvalMetric(
            metric_name="nn_mae_score",
            baseline_value=mae_base["target"],
            current_value=mae_score,
            delta=round(mae_score - mae_base["target"], 2),
            status=mae_status,
            threshold=mae_base["max_allowable"],
        )
    )
    print(f"  -> Top-1 Agreement: {agreement_rate:.1f}% ({ag_status}) | Test MAE: {mae_score:.2f} ({mae_status})")
    
    # ----------------------------------------------------
    # 3. TreeSHAP Surrogate Drift Check
    # ----------------------------------------------------
    print("\n[3/4] Checking TreeSHAP Surrogate Model Alignment & Drift...")
    explainer = get_shap_explainer()
    drift_detected = explainer.check_drift()
    drift_status = "PASS" if not drift_detected else "FAIL"
    if drift_status == "FAIL":
        regressions.append("TreeSHAP Surrogate Checkpoint Drift Detected (Surrogate trained on different NN weights)")
    metrics_list.append(
        EvalMetric(
            metric_name="shap_drift_flag",
            baseline_value=0.0,
            current_value=1.0 if drift_detected else 0.0,
            delta=0.0 if not drift_detected else 1.0,
            status=drift_status,
            threshold=0.0,
        )
    )
    print(f"  -> Drift Status: {drift_status} (Drift Detected: {drift_detected})")
    
    # ----------------------------------------------------
    # 4. Orbital Physics Integrity
    # ----------------------------------------------------
    print("\n[4/4] Verifying Keplerian Orbital Period Physics...")
    measured_period = evaluate_orbital_physics()
    # Baseline for 550km orbit: ~95.6 min; ISS: ~92.9 min
    period_status = "PASS" if 90.0 <= measured_period <= 98.0 else "FAIL"
    if period_status == "FAIL":
        regressions.append(f"Orbital Period Physics ({measured_period:.2f} min) out of nominal LEO range (90-98 min)")
    metrics_list.append(
        EvalMetric(
            metric_name="leo_orbital_period_minutes",
            baseline_value=95.6,
            current_value=measured_period,
            delta=round(measured_period - 95.6, 2),
            status=period_status,
            threshold=90.0,
        )
    )
    print(f"  -> Measured Orbital Period: {measured_period:.2f} min ({period_status})")
    
    # ----------------------------------------------------
    # Summary Report
    # ----------------------------------------------------
    overall_status = "PASS" if not regressions else "REGRESSION_DETECTED"
    run_id = f"EVAL-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    
    summary = EvalRunSummary(
        run_id=run_id,
        timestamp_iso=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        overall_status=overall_status,
        metrics=metrics_list,
        regressions=regressions,
    )
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(summary.model_dump(), f, indent=2)
        
    print("\n" + "=" * 65)
    print(f"EVALUATION HARNESS RESULT: {overall_status}")
    if regressions:
        print("Regressions Detected:")
        for r in regressions:
            print(f"  [X] {r}")
    else:
        print("ALL 6 BENCHMARK & POLICY GATES PASSED CLEANLY.")
    print(f"Report saved to: {REPORT_FILE}")
    print("=" * 65 + "\n")
    
    return summary, len(regressions) > 0


if __name__ == "__main__":
    _, has_regressions = run_full_evaluation()
    if has_regressions:
        sys.exit(1)
    sys.exit(0)
