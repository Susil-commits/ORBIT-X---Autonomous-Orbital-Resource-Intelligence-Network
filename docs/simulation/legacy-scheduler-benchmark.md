# Legacy 6-Scheduler Comparison & Historical Benchmark

This document archives the historical 6-scheduler evaluation metrics in the simulation domain for reference.

## 1. 6-Scheduler Empirical Comparison Table

| Scheduler Architecture | Paradigm | Reward Yield | Completion Rate (%) | High-Priority Rate (%) | Latency (p50) | Invariant Violations (%) |
|---|---|---|---|---|---|---|
| **Random Baseline** | Heuristic | 2,192.4 | 58.3% | 25.0% | 0.07 ms | 0.0% |
| **Greedy EDF** | Heuristic | 2,458.4 | 75.0% | 50.0% | 0.04 ms | 0.0% |
| **Multi-Agent Auction** | Market / Game Theory | 2,458.4 | 75.0% | 50.0% | 2.87 ms | 0.0% |
| **Neural Surrogate** | Deep Learning (Cross-Attn) | 2,458.4 | 75.0% | 50.0% | 2.42 ms | 3.4% (battery) |
| **Hybrid Neural + CP-SAT** | Hybrid AI / Optimization | **2,572.3** | **83.3%** | **100.0%** | 21.45 ms | **0.0% (Zero)** |
| **Google CP-SAT (Pure)** | Constraint Programming | **2,572.3** | **83.3%** | **100.0%** | 12.12 ms | **0.0% (Zero)** |

## 2. Transition to Decision Intelligence Platform

In the target 7-stage architecture:
- Scheduling algorithms are treated as optimization and simulation testbed features.
- The core platform centers on:
  1. Data Ingestion, Metadata Contracts & Lineage DAG
  2. Semantic Context Catalog & Hybrid Retrieval (FastMCP)
  3. Standardized Tool Interfaces & Sandboxed Execution
  4. Predictive Machine Learning (Cross-Attention Network) & Anomaly Detection (Isolation Forest)
  5. Constraint Optimization (Google CP-SAT)
  6. Calibrated Decision Dispatch & Refusal State Machine
  7. TreeSHAP Attribution & Cryptographic Provenance Audit Trail
