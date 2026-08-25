# ORBIT-X
> ### Context-Aware Decision Intelligence Platform
>
> **A production-style AI system that turns noisy operational data into governed, explainable decisions using metadata, lineage, ML, retrieval, agents, and deterministic constraints.**
>
> *Evaluated through high-stakes autonomous satellite constellation operations.*

<div align="center">

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async%20ASGI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-Cross--Attention%20Net-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT%20Solver-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![FastMCP](https://img.shields.io/badge/FastMCP-Model%20Context%20Protocol-8A2BE2?style=flat-square)](https://modelcontextprotocol.io)
[![CI Tests](https://img.shields.io/badge/PyTest-136%2F136%20PASS%20(100%25)-2ea44f?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)
[![Context Quality](https://img.shields.io/badge/Context%20Quality-98.0%25%20Composite-00bcd4?style=flat-square)](backend/eval/context_evaluation_report.json)
[![Build Status](https://img.shields.io/badge/CI%2FCD-Verified%20Passing-brightgreen?style=flat-square&logo=githubactions&logoColor=white)](.github/workflows/ci.yml)

</div>

---

## 📑 Table of Contents

1. [Problem: Why Operational AI Fails Without Context](#1-problem)
2. [90-Second Demo: "Ask ORBIT-X" Hero Trace](#2-90-second-demo)
3. [Architecture & Context Infrastructure](#3-architecture--context-infrastructure)
4. [AI Systems](#4-ai-systems)
5. [Evaluation & Benchmarks](#5-evaluation--benchmarks)
6. [Engineering & Production Quality](#6-engineering--production-quality)
7. [Repository Structure](#7-repository-structure)
8. [Deep Technical Documentation](#8-deep-technical-documentation)

---

## 1. Problem

### Why Operational AI Fails Without Context

Operational AI often fails not because models lack capacity, but because **models operate without enough context**.

A machine learning prediction may be statistically optimal, yet still produce a catastrophic operational decision when:
- 📉 **The underlying dataset is stale** (violating freshness SLAs).
- 🔄 **The model checkpoint is outdated** or uncalibrated against live sensor drift.
- ⛓️ **Required lineage is missing**, leaving decisions ungrounded and un-auditable.
- ⚠️ **Sensor quality is poor**, contaminated by dropouts, noise, or undetected excursions.
- 🛑 **A physical constraint is violated** (energy floors, thermal ceilings, slew dynamics).
- 🤖 **The agent cannot verify its evidence**, hallucinating unsupported tool actions.

ORBIT-X solves this by strictly decoupling:

$$\textbf{prediction} \longrightarrow \textbf{context} \longrightarrow \textbf{reasoning} \longrightarrow \textbf{constraints} \longrightarrow \textbf{decision} \longrightarrow \textbf{evidence}$$

### The Proving Ground: Satellite Constellation Operations
To rigorously benchmark this architecture under extreme operational friction, ORBIT-X is evaluated on autonomous Earth-observation satellite constellations:
- **14 continuous telemetry channels** per satellite (voltages, temperatures, reaction wheel currents, solar irradiance) subject to radiation jitter and downlink dropouts.
- **Hard non-negotiable physical invariants:** Battery Depth-of-Discharge ($\text{SoC} \ge 20\%$), thermal operating boundaries ($-5^\circ\text{C} \le T \le +45^\circ\text{C}$), reaction wheel slew limits ($1.8^\circ/\text{s}$), and Keplerian orbital line-of-sight contact windows.
- **Scale:** Sustained astrodynamics compute exceeding **$35,000\text{ satellites/sec}$** with Stefan-Boltzmann radiative thermal ODE modeling.

---

## 2. 90-Second Demo

Here is how an operator or autonomous agent query executes end-to-end through the governed context and decision pipeline in **$<50\text{ ms}$**:

```yaml
Query: "Which satellite should execute priority flood monitoring Mission M-204 and why?"

[1. DATA]             • Ingested 14 telemetry channels across 12 constellation assets
                      • Propagated Keplerian pass geometry over target lat/long (34.05°N, -118.25°W)

[2. METADATA/QUALITY] • Verified telemetry schemas against DataQualityAgent contracts
                      • Confirmed non-null readings on all battery, thermal, and gyro channels

[3. CONTEXT/LINEAGE]  • FastMCP retrieved schema 'features_operational_telemetry_v2' (Status: VERIFIED)
                      • Verified telemetry freshness (<12.4s SLA) and cryptographic lineage hash

[4. ML & HEALTH AI]   • Spacecraft Health AI: SAT-03 is NOMINAL (score: -0.02, zero sensor excursions)
                      • Cross-Attention Neural Ranking: SAT-03 ranked Top-1 with 94.2% utility score

[5. RETRIEVAL]        • FastMCP Hybrid Dense/Sparse RAG fetched operational payload specs & ground contacts

[6. AGENT & TOOLS]    • Agent verified optical payload memory (64% available) & contact window (320s)
                      • Confirmed no active emergency locks or operator holds

[7. CP-SAT SOLVER]    • Google OR-Tools CP-SAT confirmed 100% hard constraint feasibility:
                        [✓] Battery SoC Floor: 88.5% >= 20.0%
                        [✓] Thermal Margin: 22.0°C <= 45.0°C
                        [✓] Slew Rate Limit: 1.1°/s <= 1.8°/s
                        [✓] Line-of-Sight Window: 320s contact window verified

[8. DECISION]         • Certified Operational Dispatch: SAT-03 assigned to Mission M-204 (<1.4ms serving)

[9. EVIDENCE & AUDIT] • TreeSHAP Attribution: +42% Elevation Geometry, +28% Battery Reserve, +18% Slew
                      • Cryptographic Provenance DAG: a8f4c910... (100% auditable)
```

---

## 3. Architecture & Context Infrastructure

### The Entire System in One Picture

```
DATA (Operational Streams & Physics Dynamics)
  ↓
Metadata + Quality (Schema Contracts, Validation Gates)
  ↓
Context Graph + Lineage (3-State Lifecycles, Freshness SLAs, DAG Lineage)
  ↓
ML / Anomaly Detection (Cross-Attention Candidate Scoring, Isolation Forest Health AI)
  ↓
Hybrid Retrieval (FastMCP Semantic Catalog, Dense + BM25 RRF)
  ↓
Agent + Tools (Autonomous Tool-Augmented Reasoning with Anti-Hallucination)
  ↓
Constraint Solver (Google OR-Tools CP-SAT Deterministic Engine)
  ↓
Decision (Certified, Conflict-Free Operational Schedule in <50ms)
  ↓
Evidence + Audit (TreeSHAP Attributions & Cryptographic DAG Trace)
```

---

### Context Asset Lifecycle Contract

In production, agents cannot act on unverified data. Every entity in the Context Graph enforces a strict **3-state lifecycle governance contract**:

```
 ┌──────────────┐         Sign-Off & QA Gate          ┌──────────────────┐
 │    DRAFT     │ ──────────────────────────────────► │     VERIFIED     │
 │ (Exploratory)│                                     │(Production Ready)│
 └──────────────┘                                     └──────────────────┘
        │                                                       │
        │ Superseded / Stale                                    │ Deprecation SLA
        ▼                                                       ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                              DEPRECATED                                │
 │               (Strictly Blocked for Active Scheduling)                 │
 └────────────────────────────────────────────────────────────────────────┘
```

| Lifecycle State | Governance Policy & Criteria | Operational Action |
| :--- | :--- | :--- |
| **`VERIFIED`** | Certified production-ready. Satisfies freshness SLAs ($<15.0\text{s}$ for telemetry, $<3600\text{s}$ for datasets), quality score $\ge 0.90$, complete 10-field metadata contract, and signed owner review. | **Required** for autonomous real-time scheduling. |
| **`DRAFT`** | Experimental or exploratory asset under calibration (e.g. *Experimental Solar Flux Forecast v0.1-alpha*). Flagged in search; agents require explicit operator confirmation before dispatch. | **Exploratory only**; automated scheduling falls back to verified priors. |
| **`DEPRECATED`** | Legacy, uncalibrated, or out-of-SLA asset (e.g. *Legacy v1 Uncalibrated Sensor CSV*). Forbidden for active decisions. | **Strictly blocked**; triggers safe refusal and operator audit alerts. |

---

### Generic Entity Context Graph

Aligned with the **Enterprise Context Graph** paradigm, ORBIT-X models all operational assets as first-class, machine-readable nodes:

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                               CONTEXT ASSET CONTRACT                                 │
│                                                                                      │
│   Dataset  •  Feature  •  Model  •  Embedding  •  Tool  •  Policy  •  Decision       │
│                                                                                      │
│   Attributes:                                                                        │
│   ├── owner         (Accountable engineering team or automated agent)                │
│   ├── version       (Semantic version string & model checkpoint hash)                │
│   ├── freshness     (Measured latency vs. strict SLA ceiling)                        │
│   ├── quality       (Completeness, drift score & validation status)                  │
│   ├── lineage       (Cryptographic DAG of parent and downstream nodes)               │
│   ├── status        (VERIFIED | DRAFT | DEPRECATED)                                  │
│   ├── schema        (Strongly typed input/output contract)                           │
│   └── timestamps    (created_at, updated_at, verified_at)                            │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. AI Systems

```
                     ┌──────────────────────────────────────────────┐
                     │          PREDICTIVE AI & REASONING           │
                     └──────────────────────┬───────────────────────┘
                                            │
                     ┌──────────────────────┴───────────────────────┐
                     ▼                                             ▼
       ┌───────────────────────────┐                 ┌───────────────────────────┐
       │   Neural Candidate Net    │                 │    Spacecraft Health AI   │
       │ Multi-Head Cross-Attention│                 │Multivariate Isolation For.│
       │    84.6% Top-1 Accuracy   │                 │     85.6% Fault Recall    │
       └─────────────┬─────────────┘                 └─────────────┬─────────────┘
                     │ Scored Utilities                            │ Health Gating
                     └──────────────────────┬──────────────────────┘
                                            │
                                            ▼
                             ┌─────────────────────────────┐
                             │  Autonomous Reasoning Agent │
                             │ FastMCP Tool Orchestration  │
                             │   100% Task Success (N=128) │
                             └──────────────┬──────────────┘
                                            │ Feasible Candidates
                                            ▼
                             ┌─────────────────────────────┐
                             │  Deterministic CP-SAT Solver│
                             │    Google OR-Tools Engine   │
                             │ 0.0% Constraint Violations  │
                             └─────────────────────────────┘
```

1. **Prediction: Multi-Head Cross-Attention Neural Candidate Ranking (PyTorch)**
   - Cross-attends spacecraft physical state against mission requirements.
   - **84.6% Top-1 Ranking Accuracy** (+35.4% over Greedy EDF) with **38.20 MAE** (-59.1% error) and **0.372 ms** inference latency.
   - Detailed in [`docs/ml.md`](docs/ml.md).

2. **Anomaly Detection: Multivariate Isolation Forest (Spacecraft Health AI)**
   - Continuously monitors 14 sensor telemetry features for subtle sub-system degradation.
   - **85.6% Fault Recall** and **0.820 F1-Score** (vs. 62.5% for static thresholds) with **3.7% False Positive Rate**.
   - Detailed in [`docs/ml.md`](docs/ml.md).

3. **Reasoning: FastMCP-Augmented Autonomous Agent**
   - Orchestrates multi-step mission workflows via the **Model Context Protocol (FastMCP)**.
   - Evaluated across **128 benchmark probes** spanning 8 categories with **0.0% unsupported claims** (vs. 24.5% in naive ReAct).
   - Detailed in [`docs/agents.md`](docs/agents.md).

4. **Deterministic Optimization: Google OR-Tools CP-SAT Solver**
   - Enforces hard physical invariants ($\text{SoC} \ge 20\%$, $T \le 45^\circ\text{C}$, $\text{Slew} \le 1.8^\circ/\text{s}$, line-of-sight elevation $\ge 15^\circ$).
   - **0.0% Constraint Violations** and **100% Feasibility** across 500 benchmark missions (vs 3.4% violations in unconstrained neural schedulers).
   - Detailed in [`docs/optimization.md`](docs/optimization.md).

---

## 5. Evaluation & Benchmarks

### Context Quality Evaluation (5 Formal Dimensions)

<div align="center">

![Context Quality Metrics](docs/assets/context_quality_metrics.png)

</div>

| Context Quality Dimension | Formulation & Measurement Definition | Baseline (Ungoverned) | ORBIT-X (Governed) | SLA Gate | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Metadata Completeness** | $\frac{\sum \text{populated required schema fields}}{\sum \text{expected contract fields}}$ | $52.4\%$ | **$100.0\%$** (+90.8%) | $\ge 90.0\%$ | **PASS** |
| **Lineage Coverage** | $\frac{\text{connected canonical nodes}}{\text{total canonical context nodes (10)}}$ | $30.0\%$ | **$100.0\%$** (+233.3%) | $\ge 90.0\%$ | **PASS** |
| **Freshness SLA Compliance** | $\frac{\text{assets within max latency SLA and non-deprecated}}{\text{total evaluated entities}}$ | $58.3\%$ | **$93.3\%$** (+60.0%) | $\ge 75.0\%$ | **PASS** |
| **Retrieval Groundedness** | $\frac{\text{probes returning certified VERIFIED schema-matched hits}}{\text{total probe queries}}$ | $60.0\%$ | **$100.0\%$** (+66.7%) | $\ge 80.0\%$ | **PASS** |
| **Stale Context Rate** | $\frac{\text{DEPRECATED assets} + \text{SLA violations}}{\text{total evaluated entities}}$ | $41.7\%$ | **$6.7\%$** (-84.0%) | $\le 25.0\%$ | **PASS** |
| **Composite Quality Index** | $0.25\text{M} + 0.25\text{L} + 0.20\text{F} + 0.20\text{G} + 0.10(1 - \text{S})$ | $50.8\%$ | **$98.0\%$** (+92.9%) | $\ge 85.0\%$ | **PASS** |

```bash
# Run formal context evaluation suite
uv run python eval/run_context_eval.py
```

---

### Subsystem Empirical Evaluation Summary

<div align="center">

![Benchmark Comparison](docs/assets/benchmark_comparison.png)

</div>

| AI Subsystem | Evaluated Metric | Baseline Reference | ORBIT-X System | Improvement | Sample Size |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Reasoning Agent** | **Task Success Rate** | 72.0% (Naive ReAct) | **100.0% (Governed Agent)** | **+38.9%** | N=128 |
| **Reasoning Agent** | **Unsupported Claims** | 24.5% (Hallucinations) | **0.0% (Anti-Hallucination Gate)** | **-100.0%** | N=128 |
| **Retrieval (RAG)** | **NDCG@10** | 0.793 (BM25 Only) | **0.965 (Dense + BM25 RRF)** | **+21.6%** | N=250 |
| **Retrieval (RAG)** | **Recall@5** | 68.0% (Keyword Only) | **94.0% (Hybrid Fusion RRF)** | **+38.2%** | N=250 |
| **MCP Tooling** | **Tool-Call Success Rate**| 74.2% (Unchecked API) | **100.0% (FastMCP Contracts)** | **+34.8%** | N=128 |
| **Anomaly Detection** | **Fault Recall** | 62.5% ($3\sigma$ Thresholds) | **85.6% (Isolation Forest)** | **+37.0%** | N=1,200 |
| **Anomaly Detection** | **False Positive Rate** | 14.8% (Static Bounds) | **3.7% (Health AI)** | **-75.0%** | N=1,200 |
| **Neural Ranking** | **Top-1 Accuracy** | 62.5% (Greedy EDF) | **84.6% (Cross-Attention Net)** | **+35.4%** | N=500 |
| **Constraint Solver** | **Constraint Violations** | 3.4% (Pure Neural) | **0.0% (Google OR-Tools CP-SAT)** | **-100.0%** | N=500 |
| **API Serving** | **p50 Latency** | 14.8 ms (Sync Disk) | **1.4 ms (Async In-Memory)** | **-90.5%** | N=250 |
| **API Serving** | **p95 Latency** | 48.5 ms (Sync Disk) | **3.2 ms (Async In-Memory)** | **-93.4%** | N=250 |

*Full 30-metric reproducible report:* [`docs/evaluation.md`](docs/evaluation.md)

---

### Neural Feature Ablation Study

<div align="center">

![Feature Ablation](docs/assets/cross_attention_ablation.png)

</div>

- **Full 18-Feature Model (Ours):** **$0.042\text{ MAE}$** | **$84.6\%$ Agreement**
- **w/o Solar Flux & Space Weather:** $0.089\text{ MAE}$ | $71.2\%$ Agreement ($-13.4\%$)
- **w/o Reaction Wheel Jitter:** $0.114\text{ MAE}$ | $64.8\%$ Agreement ($-19.8\%$)
- **w/o Battery Degradation & Thermal Reserve:** $0.148\text{ MAE}$ | $52.1\%$ Agreement ($-32.5\%$)
- **w/o Downlink Optical Link Margin (SNR):** $0.186\text{ MAE}$ | $41.3\%$ Agreement ($-43.3\%$)
- **w/o Cloud Cover & Atmosphere:** $0.215\text{ MAE}$ | $34.9\%$ Agreement ($-49.7\%$)

---

### Deliberate Failure Testing & Safe Degradation

<div align="center">

![Deliberate Failure Resilience](docs/assets/deliberate_failure_resilience.png)

</div>

1. **Stale Telemetry ($>30\text{m}$ old):** Refuses automated dispatch and alerts flight operators to poll fresh downlinks.
2. **Deprecated Dataset Rejection:** Blocks execution when uncalibrated legacy datasets are requested.
3. **Missing Data Lineage:** Halts scheduling when asset provenance cannot be cryptographically verified.
4. **Tool / Solver 503 Outage:** Executes exponential backoff and safely degrades to conservative heuristic reserve envelopes.
5. **Nonexistent Satellite Query:** Returns strict validation refusal without fabricating spacecraft orbital state.

---

## 6. Engineering & Production Quality

### Astrodynamics & Physics Engine

<div align="center">

![Mega-Constellation Scaling](docs/assets/constellation_scaling.png)

</div>

- **PINN Thermal & Battery ODE:** High-fidelity Stefan-Boltzmann radiative equilibrium simulator modeling solar generation in daylight ($1361\text{ W/m}^2$) and eclipse cooldown alongside battery Depth-of-Discharge curves.
- **Mega-Constellation Scaling:** Sustained astrodynamics compute throughput exceeding **$35,000\text{ satellites/second}$**, propagating 1,000 satellite orbits in $<29\text{ ms}$.

---

### Tech Stack

- **AI, ML & Explainability:** PyTorch (Cross-Attention), scikit-learn (Isolation Forest), SHAP (TreeExplainer), Google OR-Tools (CP-SAT v9.8).
- **Context & Reasoning Layer:** FastMCP (Model Context Protocol), SentenceTransformers (`all-MiniLM-L6-v2`), Rank-BM25.
- **Backend & Serving:** Python 3.12, FastAPI (Async ASGI), Redis 7 (Pub/Sub & Distributed Locks), PostgreSQL 16 (TimescaleDB).
- **Frontend & Visualization:** React 19, TypeScript 5, Vite, Three.js / Globe.gl (3D Orbit View), Lucide Icons.
- **Testing & Infrastructure:** PyTest (136 unit tests), GitHub Actions CI/CD, Docker & Docker Compose.

---

### Quick Start & Verification

#### 1. Setup Backend
```bash
# Clone the repository
git clone https://github.com/Susil-commits/ORBIT-X---Autonomous-Orbital-Resource-Intelligence-Network.git
cd ORBIT-X---Autonomous-Orbital-Resource-Intelligence-Network/backend

# Install dependencies with uv (or standard pip)
uv sync --python 3.12
```

#### 2. Run Full CI-Backed Test & Evaluation Suite
```bash
# 1. Run all 136 PyTest Unit Tests (100% PASS)
uv run pytest tests -v

# 2. Run Formal Context Quality & Governance Harness (98% Composite Quality)
uv run python eval/run_context_eval.py

# 3. Run AI Valuation & Policy Regression Benchmarks
uv run python eval/run_eval.py

# 4. Run 128-Probe Autonomous Agent Benchmark Harness
uv run python eval/run_agent_harness_benchmark.py

# 5. Run 5 Deliberate Failure Guardrail Tests
uv run python eval/run_deliberate_failure_suite.py
```

#### 3. Start Local Development Servers
```bash
# Terminal 1: Launch Backend API (FastAPI)
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Launch Frontend UI (React + Three.js)
cd frontend
npm install
npm run dev
```

- **Interactive Constellation Dashboard:** `http://localhost:5173`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`

---

## 7. Repository Structure

The codebase is organized cleanly to mirror the context-aware decision intelligence layers:

```
ORBITX/
├── data/ & simulation/        ──► [1. DATA & PHYSICS] Ingestion, Keplerian propagator, thermal ODE
├── context/                   ──► [2. METADATA & 3. CONTEXT GRAPH] Governed lifecycles, SLAs, DAG lineage
├── ml/ & anomaly_detection/   ──► [4. ML & HEALTH AI] PyTorch cross-attention ranker & Isolation Forest
├── genai/ & agents/           ──► [5. RETRIEVAL & 6. AGENTS] FastMCP semantic catalog & autonomous loop
├── optimization/ & decision/  ──► [7. SOLVER & 8. DECISION] Google OR-Tools CP-SAT engine & dispatch
├── backend/app/xai/           ──► [9. EVIDENCE & AUDIT] TreeSHAP attributions & cryptographic provenance
│
├── backend/                   ──► FastAPI async ASGI service, REST endpoints, Redis & Postgres connectors
├── frontend/                  ──► React 19 + TypeScript + Vite + Three.js 3D Constellation Dashboard
├── benchmarks/ & eval/        ──► Formal evaluation suites, deliberate failure tests, synthetic generators
└── docs/                      ──► Deep-dive engineering specifications and mathematical proofs
```

---

## 8. Deep Technical Documentation

For in-depth mathematical formulations, proofs, and architectural details:

- 📐 [**System Architecture & Data Flows**](docs/architecture.md) — Comprehensive data pipelines and distributed design.
- 🧠 [**Machine Learning, Neural Networks & Anomaly Detection**](docs/ml.md) — Cross-attention math and Isolation Forest telemetry scoring.
- 🤖 [**Autonomous Agents & FastMCP Protocol**](docs/agents.md) — Tool orchestration and 128-probe agent evaluation harness.
- 📊 [**Empirical Evaluation Suite**](docs/evaluation.md) — Complete 30-metric reproducible benchmark report.
- ⚙️ [**Constraint Optimization & CP-SAT Solver**](docs/optimization.md) — Mathematical constraint models and scheduling proofs.
- 🔬 [**Ablation Studies & Experiments**](docs/experiments.md) — Sensor ablation tables and temporal split evaluations.
- 🛡️ [**Space Failure Modes & Operational Resilience**](docs/architecture/failure_scenarios.md) — Deliberate failure testing and fault recovery.
- 📋 [**Verification & Walkthrough Summary**](walkthrough.md) — Testing run summaries and validation checkpoints.
