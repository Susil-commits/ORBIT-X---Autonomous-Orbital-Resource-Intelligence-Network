# ML Experiment: Model Evaluation & Statistical Harness

## 1. Objective
Establish statistical confidence intervals, loss convergence curves, and comprehensive evaluation metrics for all trained models in the ORBIT-X decision suite.

## 2. Evaluation Suite Architecture
The evaluation framework (`backend/eval/run_eval.py`) runs automated test harnesses evaluating:
- **Regression Accuracy:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), R² Score.
- **Classification / Ranking Concordance:** Top-1 Agreement (%), Top-3 Accuracy (%), Normalized Discounted Cumulative Gain (NDCG@K), Kendall's Tau rank correlation.
- **Serving Performance:** p50, p90, p95, p99 Latency percentiles, Batching Throughput, Memory footprint.

## 3. Statistical Performance Summary

### Stage 1: Pure Machine Learning Concordance
Evaluates pure ML regression and ranking concordance on held-out test splits:

```
                      EVALUATION HARNESS ML CONCORDANCE
┌────────────────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Metric                     │ Cross-Attn  │ RandomForest│ BidValueMLP │ Ridge Reg   │
├────────────────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Top-1 Agreement            │ 84.6%       │ 81.3%       │ 68.8%       │ 75.0%       │
│ Top-3 Accuracy             │ 96.2%       │ 92.4%       │ 84.1%       │ 87.5%       │
│ NDCG@5                     │ 0.912       │ 0.884       │ 0.796       │ 0.824       │
│ Kendall's Tau              │ 0.784       │ 0.732       │ 0.618       │ 0.655       │
│ MAE                        │ 28.40       │ 21.07       │ 42.03       │ 56.84       │
│ Inference Latency (p50)    │ 0.372 ms    │ 0.132 ms    │ 0.185 ms    │ 0.004 ms    │
│ Inference Latency (p95)    │ 0.557 ms    │ 0.211 ms    │ 0.259 ms    │ 0.005 ms    │
└────────────────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

### Stage 2: Decision Systems Evaluation
Evaluates decision execution, constraint adherence, and end-to-end latency:

| Decision System | Constraint Violations | Feasibility Rate | Decision Utility | Optimization Latency (p50) | End-to-End Latency (p50) |
|---|---|---|---|---|---|
| **Cross-Attention Only** | 3.4% boundary violations | 96.6% | 84.5% | N/A (Neural only) | **0.372 ms** |
| **Cross-Attention + Google OR-Tools CP-SAT** | **0 (Modeled Invariants Enforced)** | **100.0%** | **98.7%** | **18.40 ms** | **18.77 ms** |

## 4. Error Analysis & Edge Case Diagnostic
- **Low-Telemetry Conditions:** When telemetry freshness exceeds 15 minutes, ranking accuracy drops by ~8.2%. The system automatically triggers fallback to greedy deterministic allocation.
- **High-Contention Scenarios:** When >10 simultaneous priority-1 tasks compete for a single orbital plane, Cross-Attention neural ranking provides 4.2x faster CP-SAT convergence by eliminating sub-optimal candidates before solver initialization.
