# ML Experiment: Model Evaluation & Statistical Harness

## 1. Objective
Establish statistical confidence intervals, loss convergence curves, and comprehensive evaluation metrics for all trained models in the ORBIT-X decision suite.

## 2. Evaluation Suite Architecture
The evaluation framework (`backend/eval/run_eval.py`) runs automated test harnesses evaluating:
- **Regression Accuracy:** Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), R² Score.
- **Classification / Ranking Concordance:** Top-1 Agreement (%), Top-3 Accuracy (%), Normalized Discounted Cumulative Gain (NDCG@K), Kendall's Tau rank correlation.
- **Serving Performance:** p50, p90, p95, p99 Latency percentiles, Batching Throughput, Memory footprint.

## 3. Statistical Performance Summary

```
                      EVALUATION HARNESS METRIC CONCORDANCE
┌────────────────────────────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Metric                     │ Cross-Attn  │ RandomForest│ BidValueMLP │ CP-SAT      │
├────────────────────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ Top-1 Agreement            │ 84.6%       │ 81.3%       │ 68.8%       │ 100.0%      │
│ Top-3 Accuracy             │ 96.2%       │ 92.4%       │ 84.1%       │ 100.0%      │
│ NDCG@5                     │ 0.912       │ 0.884       │ 0.796       │ 1.000       │
│ Kendall's Tau              │ 0.784       │ 0.732       │ 0.618       │ 1.000       │
│ MAE                        │ 28.40       │ 21.07       │ 42.03       │ 0.00        │
│ Inference Latency (p50)    │ 0.372 ms    │ 0.132 ms    │ 0.185 ms    │ 18.4 ms     │
│ Inference Latency (p95)    │ 0.557 ms    │ 0.211 ms    │ 0.259 ms    │ 24.2 ms     │
│ Hard Constraint Violations │ 3.4%        │ 5.8%        │ 9.1%        │ 0.0%        │
└────────────────────────────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

## 4. Error Analysis & Edge Case Diagnostic
- **Low-Telemetry Conditions:** When telemetry freshness exceeds 15 minutes, ranking accuracy drops by ~8.2%. The system automatically triggers fallback to greedy deterministic allocation.
- **High-Contention Scenarios:** When >10 simultaneous priority-1 tasks compete for a single orbital plane, Cross-Attention neural ranking provides 4.2x faster CP-SAT convergence by eliminating sub-optimal candidates before solver initialization.
