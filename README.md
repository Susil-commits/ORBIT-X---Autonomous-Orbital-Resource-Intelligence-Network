# ORBIT-X: Autonomous Satellite Mission Decision System

> **A reliable AI decision system combining predictive ML, anomaly detection, constraint optimization, and tool-augmented reasoning.**

<div align="center">

[![Python 3.12](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async%20ASGI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-Cross--Attention%20Net-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT%20Solver-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![FastMCP](https://img.shields.io/badge/FastMCP-Model%20Context%20Protocol-8A2BE2?style=flat-square)](https://modelcontextprotocol.io)
[![Tests](https://img.shields.io/badge/PyTest-100%25%20PASS-2ea44f?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)

</div>

---

## 1. Problem

Autonomous space operations require real-time mission decisions across constellations of satellites under extreme operational challenges:
- **Asynchronous Telemetry:** High-velocity sensor feeds with packet dropouts and sensor drift.
- **Strict Physical Invariants:** Hard operational limits on battery depth-of-discharge, thermal envelopes, reaction wheel slew rates, and orbital line-of-sight.
- **The AI Reliability Gap:** Raw ML models and LLMs cannot guarantee physical constraints, hallucinate under uncertainty, and lack verifiable data lineage. Pure heuristic systems are rigid and fail to adapt.

---

## 2. What It Does

ORBIT-X is an autonomous mission decision engine that transforms raw satellite telemetry and mission requests into **conflict-free, constraint-satisfying, and explainable operational schedules in $<50\text{ ms}$**.

```
Mission Request
      ↓
ORBIT-X
      ↓
Find relevant context
      ↓
ML prediction
      ↓
Anomaly / health check
      ↓
Constraint optimization
      ↓
Decision
      ↓
"Why this satellite?"
      ↓
Evidence + explanation
```

---

## 3. Architecture

ORBIT-X decouples statistical machine learning from deterministic constraint satisfaction to guarantee system safety:

```
Telemetry ──────┐
                ↓
          Data Processing (Validation & Feature Store)
                ↓
       ┌────────┴────────┐
       ↓                 ↓
   ML Ranking       Anomaly Detection
 (Cross-Attention)  (Isolation Forest)
       ↓                 ↓
       └────────┬────────┘
                ↓
       Constraint Solver (Google OR-Tools CP-SAT)
                ↓
          Final Decision (Conflict-Free Action)
                ↓
       Explanation / Evidence (TreeSHAP & Lineage)
                ↑
        Agent + Context (FastMCP & Hybrid RAG)
```

---

## 4. AI/ML Components

Rather than relying on ungrounded black-box models, ORBIT-X focuses on three core AI components:

### A. Prediction: Multi-Head Cross-Attention Neural Ranking
- **Role:** Evaluates spacecraft state vectors against mission requirements to predict optimal matching suitability.
- **Impact:** **84.6% Top-1 Ranking Accuracy** (+35.4% over Greedy EDF) with **38.20 MAE** (-59.1% error reduction).
- **Details:** [`docs/ml.md`](docs/ml.md)

### B. Anomaly Detection: Multivariate Isolation Forest
- **Role:** Continuously scores 14 physical sensor streams (voltages, temperatures, reaction wheel currents) to detect degradation before threshold alarms trigger.
- **Impact:** **85.6% Fault Recall** and **0.820 F1-Score** (vs. 62.5% recall for static $3\sigma$ rules) with **3.7% False Positive Rate**.
- **Details:** [`docs/ml.md`](docs/ml.md)

### C. Decision Intelligence: Google OR-Tools CP-SAT Solver
- **Role:** Enforces hard mathematical constraints (energy balance, thermal limits, angular slew rates, orbital contact windows).
- **Impact:** **0.0% Constraint Violations** and **100.0% Feasibility** across all scheduled missions.
- **Details:** [`docs/optimization.md`](docs/optimization.md)

---

## 5. Results & Empirical Benchmarks

All metrics are measured against live tests and held-out test splits:

| AI Subsystem | Metric | Baseline System | ORBIT-X System | Improvement |
| :--- | :--- | :--- | :--- | :--- |
| **Reasoning Agent** | **Task Success Rate** | 72.0% (Naive ReAct) | **100.0% (Governed Agent)** | **+38.9%** |
| **Reasoning Agent** | **Unsupported Claims** | 24.5% (Hallucinations) | **0.0% (Anti-Hallucination Gate)** | **-100.0%** |
| **Retrieval (RAG)** | **NDCG@10** | 0.793 (BM25 Only) | **0.965 (Dense + BM25 RRF)** | **+21.6%** |
| **MCP Tooling** | **Tool-Call Success** | 74.2% (Unchecked API) | **100.0% (FastMCP Schema Envelopes)**| **+34.8%** |
| **Anomaly Detection** | **Fault Recall** | 62.5% ($3\sigma$ Thresholds) | **85.6% (Isolation Forest)** | **+37.0%** |
| **Neural Ranking** | **Top-1 Accuracy** | 62.5% (Greedy EDF) | **84.6% (Cross-Attention Net)** | **+35.4%** |
| **Constraint Solver** | **Constraint Violations** | 3.4% (Pure Neural) | **0.0% (Google OR-Tools CP-SAT)** | **-100.0%** |
| **API Serving** | **p95 Latency** | 48.5 ms (Sync Disk) | **3.2 ms (Async In-Memory)** | **-93.4%** |

*Full 30-metric reproducible evaluation table:* [`docs/evaluation.md`](docs/evaluation.md)

---

## 6. End-to-End Demo & Failure Handling

### Practical Agent: "Ask ORBIT-X"

```
Query: "Which satellite is best for Mission 42 and why?"

Response:
Recommended: SAT-03
Confidence: 94.2%

Reasons:
  • Subsystem Health: 98.4% (No telemetry anomalies detected)
  • Fuel / Battery: High (Battery DoD 38% vs 65% limit)
  • Mission Visibility: 96.8% (Elevation window 72°, Slew angle 12°)
  • Predicted Success: 94.2/100 (Top-1 neural ranking)

Constraints Checked: 8/8 Verified
  [x] Battery Thermal Envelope: 18.4°C (Limit: [-5°C, 45°C])
  [x] Reaction Wheel Slew Rate: 1.1°/s (Limit: 1.8°/s)
  [x] Ground Station ISL Window: 320s contact window verified

Evidence & Lineage:
  Telemetry Stream → Feature Store → CrossAttentionNet → CP-SAT Solver → Verified Action
```

### Safe Failure Handling: Refusal Over Hallucination

ORBIT-X is deliberately tested against 4 operational failure modes to verify it **safely refuses unsafe decisions**:

1. **Stale Telemetry ($>30\text{m}$ old):** Refuses automated scheduling and alerts operators of expired telemetry.
2. **Missing Lineage / Unverified Data:** Blocks execution when data provenance cannot be established.
3. **Tool / API 503 Outage:** Executes exponential retry and safely falls back to conservative heuristic envelopes.
4. **Invalid / Nonexistent Mission Query:** Immediately returns catalog validation error without fabricating spacecraft state.

---

## 7. Tech Stack

- **AI / ML & Optimization:** PyTorch (Cross-Attention), scikit-learn (Isolation Forest), Google OR-Tools (CP-SAT), SHAP (TreeExplainer).
- **Agent & Context Layer:** FastMCP (Model Context Protocol), SentenceTransformers (Embeddings), BM25 (Lexical Search).
- **Backend & Serving:** Python 3.12, FastAPI (Async ASGI), Redis 7 (Cache & PubSub), PostgreSQL 16.
- **Frontend:** React 19, TypeScript 5, Vite, TailwindCSS.
- **Testing & Tooling:** PyTest, Docker, Docker Compose.

---

## 8. Quick Start

### 1. Clone & Setup Backend
```bash
git clone https://github.com/Susil-commits/ORBIT-X---Autonomous-Orbital-Resource-Intelligence-Network.git
cd ORBITX/backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Evaluation & Benchmark Suite
```bash
python -m pytest tests/test_rigorous_ai_evaluation.py tests/test_deliberate_failure_testing.py tests/test_agent_evaluation_harness.py -v
```

### 3. Start Backend & Interactive UI
```bash
# Terminal 1: Backend API
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd ../frontend
npm install
npm run dev
```

---

## 9. Deep-Dive Engineering Documentation

For in-depth mathematical formulations, architecture diagrams, and experiments:

- 📐 [**System Architecture & Data Flows**](docs/architecture.md)
- 🧠 [**Machine Learning, Neural Networks & Anomaly Detection**](docs/ml.md)
- 🤖 [**Autonomous Agents & FastMCP Protocol**](docs/agents.md)
- 📊 [**Empirical Evaluation Suite & 128 Benchmark Probes**](docs/evaluation.md)
- ⚙️ [**Constraint Optimization & CP-SAT Solver**](docs/optimization.md)
- 🔬 [**Ablation Studies & Temporal Split Experiments**](docs/experiments.md)
