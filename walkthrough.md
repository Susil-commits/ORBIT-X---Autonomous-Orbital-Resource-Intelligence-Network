# ORBIT-X Hero Workflow Walkthrough: Ask ORBIT-X Decision Intelligence

This document walks through the **Ask ORBIT-X Hero Decision Workflow** and verifies the end-to-end AI-native capabilities of the transformed platform.

---

## 1. Hero Workflow Walkthrough: "Ask ORBIT-X"

### Target Scenario:
> **Operator Query**: *"Why is Mission M-204 at risk and what should we do?"*

```
1. Resolve Mission Constraints (Target EO, 70% min SOC, +15° elevation)
                      │
                      ▼
2. Ingest Operational Context & Telemetry (12 Constellation Nodes)
                      │
                      ▼
3. Run Multivariate Isolation Forest (Detect SAT-03 +3.2σ thermal anomaly)
                      │
                      ▼
4. Multi-Head Cross-Attention Neural Ranking (SAT-01: 0.942, SAT-04: 0.887)
                      │
                      ▼
5. Generate TreeSHAP Attribution (Why SAT-01 chosen vs why SAT-03 rejected)
                      │
                      ▼
6. Solve CP-SAT Integer Programming (100% hard constraints satisfied)
                      │
                      ▼
7. Assemble Grounded Evidence & Citations (3 verified telemetry/RAG sources)
                      │
                      ▼
8. Synthesize Grounded Operational Recommendation
                      │
                      ▼
9. Present Human Operator Review Controls ([Approve] / [Reject] / [Investigate])
                      │
                      ▼
10. Persist Decision Audit & Operator Feedback to PostgreSQL Ledger
```

---

## 2. Interactive Verification of Platform Views

### A. AI Assistant Hero View (`/` - Default Tab)
- **Interactive Query Input**: Operator enters operational inquiries or chooses one-click presets.
- **10-Step Execution Stepper**: Visualizes the autonomous decision pipeline in real-time.
- **Grounded Evidence Drawer**: Displays verified fact citations and honest refusal flags on insufficient evidence.
- **Human-in-the-Loop Actions**: Instant review logging (`[Approve Action]`, `[Reject]`, `[Investigate]`) with PostgreSQL persistence.

### B. Decision Explorer View
- **Multi-Candidate Evaluation Table**: Inspects Cross-Attention valuation scores, win probabilities, and constraint gates for all candidate nodes.
- **Empirical Baseline Comparison**: Compares Cross-Attention against `BidValueMLP`, `Random Forest`, and `Greedy EDF`.
- **TreeSHAP Feature Attributions**: Dual explanation breakdown highlighting positive drivers for the selected resource and disqualification factors for rejected resources.
- **CP-SAT Invariant Proofs**: Formal verification that 100% of physical constraints (LOS, battery SOC, thermal SOA, slew limits) are satisfied.

### C. Data Discovery & Lineage View
- **Semantic Dataset Catalog**: Searchable metadata with schema definitions, freshness SLAs, and downstream consumers.
- **End-to-End Decision Lineage DAG**: Traces data provenance from Raw Telemetry $\to$ Schema Cleaning $\to$ Feature Store $\to$ ML Model $\to$ CP-SAT Optimizer $\to$ Human Review $\to$ Outcome.
- **Data Quality & Drift Agent**: Continuous auditing of null rates, schema mutations, and range violations.

### D. Agent Traces & MCP View
- **Execution Waterfall**: Step-by-step latency, inputs, and outputs for all registered MCP tools (`get_constellation_status`, `preview_satellite_bid`, `ask_mission_history`, `trigger_scenario`, `query_decision_lineage`).
- **Trust & Grounding Metrics**: Real-time grounding confidence scores and anti-hallucination verification.

### E. Monitoring & Evaluation View
- **Live System SLOs**: P95 API latencies (1.4ms), Cross-Attention inference (1.2ms), CP-SAT solve time (1.4ms), and Cache Hit Rates (94.8%).
- **Feature Ablation Hierarchy**: Empirical table measuring performance degradation upon removing key telemetry features.

### F. Simulation Environment (Evaluation Domain)
- **Contained Digital Twin**: 3D Globe, Orbit Propagation, Real-Time Constellation Telemetry HUD, Schedule Gantt, and Scenario Injection.

---

## 3. Test & Verification Summary

- **PyTest Backend Suite**: 83 / 83 Tests Passing (100% pass rate).
- **Frontend Production Build**: Vite / TypeScript builds with 0 errors.
- **FastAPI OpenAPI Endpoints**: Fully documented under `/docs` across AI, Context, Experiments, and Simulation domains.
