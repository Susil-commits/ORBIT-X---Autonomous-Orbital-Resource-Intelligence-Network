# ORBIT-X

> **An AI-native decision intelligence platform evaluated through a satellite simulation environment.**

ORBIT-X is an end-to-end AI decision platform that combines operational data pipelines, machine learning, anomaly detection, explainable AI, context-aware retrieval, tool-using agents, Model Context Protocol (MCP), and constraint-aware optimization to transform high-velocity operational telemetry into auditable, verifiable decisions.

A high-fidelity satellite simulation environment provides realistic telemetry streams, operational physics constraints, and failure scenarios strictly as the evaluation domain and telemetry generator for the AI system.

<div align="center">

![ORBIT-X AI Native](https://img.shields.io/badge/ORBIT--X-AI--Native%20Decision%20Intelligence-00f0ff?style=for-the-badge&logo=probot&logoColor=black)
<br/>

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async%20ASGI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-Cross--Attention%20Net-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT%20Solver-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-Baselines%20%26%20Isolation%20Forest-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-TreeExplainer%20XAI-green?style=flat-square)](https://shap.readthedocs.io)
[![Redis](https://img.shields.io/badge/Redis%207-Cache%20%26%20PubSub-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Persistence%20%26%20Audit-336791?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![MCP Protocol](https://img.shields.io/badge/MCP-Official%20Server-8A2BE2?style=flat-square)](https://modelcontextprotocol.io)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-Build%20Tool-646CFF?style=flat-square&logo=vite&logoColor=white)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Manifests-326CE5?style=flat-square&logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Observability](https://img.shields.io/badge/Observability-Prometheus%20%7C%20Grafana-F46800?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io)
[![PyTest](https://img.shields.io/badge/Tests-90%2F90%20PASS%20(100%25)-2ea44f?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)

</div>

---

## Table of Contents
1. [What is ORBIT-X?](#1-what-is-orbit-x)
2. [Why I Built It](#2-why-i-built-it)
3. [What Makes It AI-Native?](#3-what-makes-it-ai-native)
4. [Architecture & Core Capabilities](#4-architecture--core-capabilities)
5. [The Canonical Decision Pipeline](#5-the-canonical-decision-pipeline)
6. [ML Pipeline & Neural Architecture](#6-ml-pipeline--neural-architecture)
7. [Top-Level AI & Decision Intelligence Benchmarks](#7-top-level-ai--decision-intelligence-benchmarks)
8. [Anomaly Detection & Predictive Health](#8-anomaly-detection--predictive-health)
9. [Explainable AI (TreeSHAP & Attention XAI)](#9-explainable-ai-treeshap--attention-xai)
10. [Context & Semantic Lineage Backbone](#10-context--semantic-lineage-backbone)
11. [Hybrid RAG, Agents & MCP](#11-hybrid-rag-agents--mcp)
12. [Hero Feature — Ask ORBIT-X Execution](#12-hero-feature--ask-orbit-x-execution)
13. [Constraint-Aware Optimization (CP-SAT)](#13-constraint-aware-optimization-cp-sat)
14. [Human-in-the-Loop Review & Feedback Analytics](#14-human-in-the-loop-review--feedback-analytics)
15. [Production Observability & SLOs](#15-production-observability--slos)
16. [Simulation Environment as Physical Evaluation Testbed](#16-simulation-environment-as-physical-evaluation-testbed)
17. [Quick Start, Testing & Execution Guide](#17-quick-start-testing--execution-guide)

---

## 1. What is ORBIT-X?

**ORBIT-X** is an end-to-end **AI-Native Decision Intelligence Platform** designed to solve the challenge of turning complex, high-velocity operational telemetry and mission constraints into verified, explainable, and constraint-satisfying decisions.

The platform unifies:
- **Data Engineering & Quality:** Semantic metadata cataloging, data quality auditing (`data_quality_agent.py`), and bidirectional data lineage (`context_graph.py`).
- **Machine Learning & Valuation:** Classical baselines, deep neural ranking via Multi-Head Cross-Attention (`cross_attention_network.py`), and Huber value regression.
- **Unsupervised Anomaly Detection:** Multivariate Isolation Forest telemetry health scoring and predictive maintenance (`health_ai.py`).
- **Explainable AI (XAI):** TreeSHAP feature attributions and attention heatmaps for transparent human reasoning (`shap_explainer.py`).
- **Constraint Optimization:** Google OR-Tools CP-SAT enforcing modeled physical constraints when feasible (`optimizer.py`).
- **Autonomous Agents & MCP:** Hybrid RAG (`hybrid_mission_rag.py`), Model Context Protocol tool execution (`agent_loop.py`), and auditable trust verification (`trust_layer.py`).
- **Audit & Governance:** Immutable decision audit logging (`decision_logger.py`), human review feedback, and production Prometheus/Grafana observability.

---

## 2. Why I Built It

Most AI systems can generate text or isolated predictions. 

ORBIT-X explores a deeper engineering challenge:

**How can an AI system understand the context of operational data, retrieve the right evidence, use tools, reason over ML outputs, produce an explainable decision, and allow a human operator to verify and approve it?**

The platform therefore integrates:
- Semantic data and metadata
- Machine learning models and baselines
- Unsupervised anomaly detection
- Explainable AI (TreeSHAP)
- Context-aware RAG
- Tool-using autonomous agents
- Standardized Model Context Protocol (MCP)
- Deterministic constraint optimization
- Human-in-the-loop review
- Production observability & MLOps

---

## 3. What Makes It AI-Native?

The AI layer is not an isolated chatbot. It is deeply embedded into the operational backbone:

1. **Operational data:** Streaming / near-real-time multi-sensor telemetry processing.
2. **Metadata:** Semantic schemas, freshness SLAs, and data quality scores.
3. **Lineage:** Bidirectional provenance graphs from raw data to decisions.
4. **ML predictions:** Neural candidate rankings and valuation tokens.
5. **Anomaly detection:** Unsupervised health scores and fault classification.
6. **Optimization:** Hard constraint verification engines (Google CP-SAT).
7. **Structured tools:** Model Context Protocol (MCP) JSON-RPC interfaces.
8. **Retrieval:** Hybrid dense vector + keyword BM25 context builder.
9. **Human feedback:** Operator review datasets for continuous learning.
10. **Observability:** Granular agent traces, latencies, and Prometheus metrics.

---

## 4. Architecture & Core Capabilities

The intelligence layer maps directly onto explicit, testable Python components:

| Architectural Component | Core Module | System Function |
|---|---|---|
| **Context & Lineage** | [`context_graph.py`](file:///backend/app/intelligence/context_graph.py) | Semantic metadata catalog, entity relationships, and bidirectional data lineage |
| **Agent Orchestration** | [`agent_loop.py`](file:///backend/app/intelligence/agent_loop.py) | Autonomous multi-step planning, tool selection, and intent decomposition |
| **Data Quality** | [`data_quality_agent.py`](file:///backend/app/intelligence/data_quality_agent.py) | Real-time schema validation, type drift detection, and freshness verification |
| **Trust & Grounding** | [`trust_layer.py`](file:///backend/app/intelligence/trust_layer.py) | Anti-hallucination verification, citation generation, and honest refusal gates |
| **Machine Learning** | [`cross_attention_network.py`](file:///backend/app/intelligence/cross_attention_network.py) | Multi-head cross-attention neural ranking across resources and requests |
| **Anomaly Detection** | [`health_ai.py`](file:///backend/app/intelligence/health_ai.py) | Multivariate Isolation Forest telemetry health scoring and fault alerts |
| **Hybrid RAG** | [`hybrid_mission_rag.py`](file:///backend/app/intelligence/hybrid_mission_rag.py) | Hybrid dense vector + keyword BM25 + structured metadata retrieval |
| **Audit & Logging** | [`decision_logger.py`](file:///backend/app/intelligence/decision_logger.py) | Immutable decision logging, evidence packaging, and provenance tracking |
| **Optimization** | [`optimizer.py`](file:///backend/app/intelligence/optimizer.py) | Google OR-Tools CP-SAT deterministic constraint satisfaction solver |
| **Explainability (XAI)** | [`shap_explainer.py`](file:///backend/app/intelligence/shap_explainer.py) | TreeSHAP local attributions and cross-attention feature interaction heatmaps |

```text
DATA ──► ML / AI ──► CONTEXT + METADATA ──► RAG / AGENTS / MCP ──► DECISION INTELLIGENCE ──► CP-SAT OPTIMIZATION ──► HUMAN REVIEW ──► FEEDBACK ──► MONITORING
                                                           ▲
                                                           │ (Operational Constraints & Sensor Streams)
                                             SATELLITE SIMULATION ENVIRONMENT
```

---

## 5. The Canonical Decision Pipeline

The platform operates on one primary, canonical end-to-end execution path:

```text
DATA (Validation via data_quality_agent.py)
 ↓
Feature Engineering (18-dim multimodal vectors)
 ↓
ML / Anomaly Detection (health_ai.py Isolation Forest)
 ↓
Prediction (cross_attention_network.py)
 ↓
SHAP Attribution (shap_explainer.py TreeSHAP)
 ↓
Context Graph / Lineage (context_graph.py)
 ↓
Hybrid RAG (hybrid_mission_rag.py Dense + BM25)
 ↓
Agent & MCP Tools (agent_loop.py + server.py)
 ↓
Constraint Optimization (optimizer.py CP-SAT)
 ↓
Decision Logging (decision_logger.py)
 ↓
Trust & Evidence Grounding (trust_layer.py)
 ↓
Human Review & Feedback Loop (/api/context/feedback)
 ↓
Monitoring (Prometheus & OpenTelemetry)
```

---

## 6. ML Pipeline & Neural Architecture

```
  Operational Dataset ──► Pydantic v2 Validation ──► StandardScaler ──► 18-dim Feature Store ──► 7-Model Benchmark Evaluation ──► Champion (Hybrid Neural + CP-SAT)
```

- **Candidate Ranking (Cross-Attention):** Multi-Head Cross-Attention Network (`ConstellationCrossAttentionNet`) learning complex cross-modal interactions between resource availability tokens and mission request demand tokens ($0.372$ ms p50 latency, $84.6\%$ top-1 agreement).
- **Baselines Evaluated:** Random, Greedy Earliest Deadline First (EDF), Ridge Linear Regression, Random Forest / XGBoost regressor, Multi-Layer Perceptron (MLP).

---

## 7. Top-Level AI & Decision Intelligence Benchmarks

Empirically measured AI metrics generated by the evaluation harness (`backend/eval/run_baselines.py`):

| Model Architecture | Category | Accuracy (%) | Top-1 Agreement | F1 Score | MAE | Latency (p50) | Latency (p95) | Throughput (inf/sec) |
|---|---|---|---|---|---|---|---|---|
| **Random Assignment** | Heuristic | 30.0% | 37.5% | 0.188 | 91.04 | 0.001 ms | 0.002 ms | 716,332.3 |
| **Greedy EDF Heuristic** | Heuristic | 62.5% | 62.5% | 0.450 | 93.48 | 0.001 ms | 0.001 ms | 1,000,000.0 |
| **Ridge Linear Regression** | Classical ML | 75.0% | 75.0% | 0.570 | 56.84 | 0.004 ms | 0.005 ms | 274,876.3 |
| **Random Forest / XGBoost** | Classical ML | 81.2% | 81.25% | 0.658 | 21.07 | 0.132 ms | 0.211 ms | 7,598.9 |
| **Multi-Layer Perceptron (MLP)** | Deep Learning | 68.8% | 68.75% | 0.571 | 42.03 | 0.185 ms | 0.259 ms | 5,397.5 |
| **ConstellationCrossAttentionNet** | Deep Learning | 84.6% | 84.6% | 0.612 | 28.40 | 0.372 ms | 0.557 ms | 2,690.9 |
| **Hybrid Neural + CP-SAT (Champion)** | Hybrid AI | **100.0%** | **100.0%** | **1.000** | **0.00** | 18.400 ms | 24.200 ms | 54.3 |

### AI Platform Latency & Operational SLOs
- **Neural Token Valuation Latency:** $0.372$ ms ($p50$) / $0.557$ ms ($p95$)
- **TreeSHAP Feature Attribution Latency:** $<1.200$ ms
- **Multivariate Anomaly Detection Latency:** $0.140$ ms ($F_1: 0.925$)
- **Hybrid Dense + BM25 Decision Retrieval:** $<4.500$ ms (Zero Hallucination Grounding)
- **Deterministic CP-SAT Hard Constraint Verification:** $18.400$ ms (Modeled Physical Invariant Safety)

<div align="center">

![Benchmark Comparison](docs/assets/benchmark_comparison.png)

</div>

---

## 8. Anomaly Detection & Predictive Health

- **Algorithm:** Multivariate `IsolationForest(n_estimators=150, contamination=0.08)`
- **Telemetry Features (7-dim):** `battery_soc`, `internal_temp_c`, `power_draw_w`, `comm_latency_ms`, `link_snr_db`, `memory_util_pct`, `task_failure_rate`.
- **Pipeline:** Telemetry $\rightarrow$ Feature Extraction $\rightarrow$ Isolation Forest $\rightarrow$ Anomaly Score $\rightarrow$ Threshold ($-0.095$) $\rightarrow$ Severity Alert $\rightarrow$ Autonomous Replanning.
- **Metrics:** Precision: $0.918$, Recall: $0.932$, F1: $0.925$, False Positive Rate: $2.1\%$, Detection Latency: $0.14$ ms.

<div align="center">

![Health AI Metrics](docs/assets/health_ai_metrics.png)

</div>

---

## 9. Explainable AI (TreeSHAP & Attention XAI)

- **Pipeline:** Neural Prediction $\rightarrow$ TreeSHAP $\rightarrow$ Feature Attribution $\rightarrow$ Human Explanation.
- **Capabilities:**
  - Global feature importance rankings across 18 operational dimensions.
  - Local waterfall attributions for individual decisions.
  - Attention heatmaps showing token interactions between resource availability and mission demands.
  - Comparative explanations: *"Why was Candidate A chosen while Candidate B was rejected?"*

---

## 10. Context & Semantic Lineage Backbone

Bidirectional provenance tracking across 10 core entities (`Dataset`, `Mission`, `Satellite`, `TelemetryStream`, `Feature`, `Model`, `Prediction`, `Anomaly`, `Decision`, `Tool`):

```
  Telemetry Stream ──► Dataset (satellite_telemetry) ──► 18-dim Feature Vector ──► Model & Anomaly ──► Prediction ──► CP-SAT ──► Decision ──► Outcome
```

- **Natural Language Discovery:** Semantic catalog query (`/api/context/catalog/search`).
- **Provenance Querying:** Answers *"What data and features influenced this decision?"* via `/api/context/lineage/provenance/{decision_id}`.

---

## 11. Hybrid RAG, Agents & MCP

- **Query Planner:** Decomposes queries into structured metadata SQL filters, dense vector embeddings (`SentenceTransformers`), and exact BM25 keyword matching.
- **Agent Lifecycle:** Query $\rightarrow$ Intent Understanding $\rightarrow$ Planning $\rightarrow$ Tool Selection $\rightarrow$ Execution $\rightarrow$ Evidence Collection $\rightarrow$ Grounded Response $\rightarrow$ Trust Verification.
- **Model Context Protocol (MCP):** Exposes 10 standardized tool schemas (`get_dataset_metadata`, `search_telemetry`, `get_anomaly`, `get_model_prediction`, `explain_prediction`, `trace_decision_provenance`, `run_optimizer`, `record_human_feedback`).

---

## 12. Hero Feature — Ask ORBIT-X Execution

### User Query:
> *"Why is Mission M-204 at risk and what should we do?"*

### Canonical Decision Synthesis:
```text
┌────────────────────────────────────────────────────────────────────────┐
│                        MISSION M-204 RISK REPORT                       │
├────────────────────────────────────────────────────────────────────────┤
│ Status: HIGH RISK                           Confidence: 94% (GROUNDED) │
│ Target: Disaster Response (Lat 34.05, Lon -118.25)  Deadline: 18 min   │
├────────────────────────────────────────────────────────────────────────┤
│ Primary Causes on SAT-03:                                              │
│ • Battery State of Charge degraded to 24.5% (approaching 20% limit)    │
│ • Internal temperature elevated to 48.2°C (exceeds 45°C limit)         │
│ • Isolation Forest Anomaly Score: -0.142 (CRITICAL_THERMAL)            │
│ • SHAP Negative Attribution: internal_temp_c (-28.4), battery_soc (-22)│
├────────────────────────────────────────────────────────────────────────┤
│ Recommended Action:                                                    │
│ Reassign Mission M-204 from SAT-03 ──► SAT-17                          │
│ (SAT-17 State: Battery 88.5%, Temp 22.0°C, Neural Score: 94.2, PASS)  │
├────────────────────────────────────────────────────────────────────────┤
│ Auditable Constraints Verified (CP-SAT Solver):                        │
│ [✓] Battery Energy Floor (SAT-17 SoC 88.5% >= 20.0% floor)             │
│ [✓] Line-of-Sight Window (Max elevation 78.4°, window 180s)           │
│ [✓] Mission Deadline Slack (Done in 4.2 min vs 18 min deadline)        │
│ [✓] Collision Risk (Zero conjunctions, miss distance > 28.5 km)        │
├────────────────────────────────────────────────────────────────────────┤
│ Provenance Lineage:                                                    │
│ Telemetry: TEL-SAT03-T042 | Prediction: PRED-XATTN-094                 │
│ Anomaly: ANOM-ISO-088    | Decision: DEC-M-204 (Model: CrossAttn v2.2) │
├────────────────────────────────────────────────────────────────────────┤
│ Actions:  [ APPROVE REASSIGNMENT ]   [ REJECT ]   [ INVESTIGATE ]      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Constraint-Aware Optimization (CP-SAT)

- **Architecture:** ML Prediction $\rightarrow$ Candidate Ranking $\rightarrow$ Google OR-Tools CP-SAT $\rightarrow$ Hard Constraint Validation $\rightarrow$ Final Decision.
- **Why Hybrid Decisioning?** Deep learning provides fast candidate rankings in $0.372$ ms, while Google OR-Tools CP-SAT enforces modeled physical invariants (battery $\ge 20\%$, thermal $\le 45^\circ\text{C}$, line-of-sight elevation $\ge 15^\circ$) whenever feasible.

---

## 14. Human-in-the-Loop Review & Feedback Analytics

- **Operator Actions:** `[Approve]`, `[Reject]`, `[Investigate]` recorded to PostgreSQL.
- **Feedback Analytics (`GET /api/context/feedback/analytics`):** Real-time tracking of approval rates, rejection reasons, and operator override distributions for continuous model calibration.

---

## 15. Production Observability & SLOs

- **Metrics:** `fastapi_requests_total`, `http_request_duration_seconds`, `model_inference_seconds`, `cpsat_solve_seconds`, `rag_retrieval_seconds`, `anomaly_score_gauge`.
- **Telemetry Processing:** Streaming / near-real-time sensor processing exposed via OpenTelemetry, Prometheus, and Grafana dashboards.

---

## 16. Simulation Environment as Physical Evaluation Testbed

While the primary benchmarks measure **AI, Machine Learning, and Decision Quality**, the underlying simulation testbed generates realistic operational telemetry and physical constraints at scale:

| Evaluation Testbed Metric | Measured Value | Operational Purpose |
|---|---|---|
| **Orbital Propagation Throughput** | **34,280 satellites/sec** | High-throughput telemetry generation for mega-constellation stress testing |
| **Telemetry Streaming Rate** | **10 Hz Real-Time Sync** | Live sensor push via Async ASGI WebSockets and Redis ring buffers |
| **ISS Ground-Truth Physics Parity** | **99.7% Accuracy (92.9 min)** | Validation against NORAD 25544 real Celestrak TLE ground truth |
| **ISL Optical Mesh Routing** | **<0.85 ms Dijkstra Solve** | Multi-hop inter-satellite laser communication topology verification |
| **Thermal / Battery ODE Step Time** | **0.024 ms / step** | Stefan-Boltzmann radiative balance and electrochemical discharge modeling |

<div align="center">

![Constellation Scaling](docs/assets/constellation_scaling.png)

</div>

---

## 17. Quick Start, Testing & Execution Guide

### Prerequisites
- Python 3.12+ with `uv` package manager
- Node.js 18+ & npm (for frontend)

### 1. Run Live End-to-End Decision Intelligence CLI Demo
```bash
backend\.venv\Scripts\python.exe scripts/demo_decision_platform.py
```

### 2. Start Backend API Server
```bash
cd backend
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```

### 4. Run Full Test Suite (100% Passing)
```bash
cd backend
uv run pytest -v
```

- **Automated Tests:** 90 tests passing with 100% success rate across all ML, context, trust, RAG, and optimizer modules.
- **Chaos Resilience Matrix:** Full 15-scenario failure mode documentation available in [`docs/architecture/failure_scenarios.md`](file:///docs/architecture/failure_scenarios.md).
- **Core Design Decision:** Cross-attention neural candidate valuation accelerates CP-SAT search by $4.2\times$ while CP-SAT guarantees modeled hard constraint safety whenever feasible. All detailed architectural specifications reside in [`docs/`](file:///docs/).

