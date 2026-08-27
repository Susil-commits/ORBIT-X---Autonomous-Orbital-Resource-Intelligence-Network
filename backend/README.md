# ORBIT-X Backend Engine

> **The computational backbone of ORBIT-X, providing high-performance APIs, physics simulation, constraint optimization, and governed AI decision services.** It ingests high-velocity telemetry, validates data contracts and lineage, executes neural ranking with physical constraint verification, and exposes tools via standard protocols (FastAPI ASGI & FastMCP).

<div align="center">

[![FastAPI](https://img.shields.io/badge/FastAPI-Async%20ASGI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-Cross--Attention%20Net-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT%20Solver-4285F4?style=flat-square&logo=google&logoColor=white)](https://developers.google.com/optimization)
[![FastMCP](https://img.shields.io/badge/FastMCP-Model%20Context%20Protocol-8A2BE2?style=flat-square)](https://modelcontextprotocol.io)
[![PyTest](https://img.shields.io/badge/PyTest-159%2F159%20PASS%20(100%25)-2ea44f?style=flat-square&logo=pytest&logoColor=white)](https://pytest.org)

</div>

---

## 🏛️ Architecture Overview

The backend is architected around a strict multi-layer separation of concerns:

```
backend/
├── app/
│   ├── api/                   # REST API route controllers (FastAPI)
│   │   ├── routes_context.py          # Data contract, lineage DAG & freshness SLA endpoints
│   │   ├── routes_ai.py               # Neural ranking, Isolation Forest health & SHAP explainability
│   │   ├── routes_missions.py         # Mission lifecycle & CP-SAT scheduling dispatch
│   │   ├── routes_simulation.py       # Keplerian propagator & PINN thermal ODE streams
│   │   ├── routes_benchmarks.py       # Empirical evaluation & 5-paradigm baseline metrics
│   │   └── routes_experiments.py      # Feature ablation & scenario experiment runners
│   ├── context/               # Context Graph engine, schema validators & lineage DAG store
│   ├── intelligence/          # Cross-Attention predictor, RAG catalog & calibrated refusal engine
│   ├── mcp_server/            # FastMCP standardized Model Context Protocol server
│   ├── physics/               # SGP4 / Keplerian astrodynamics propagator & coordinate transforms
│   ├── simulation/            # Stefan-Boltzmann radiative thermal & battery state-of-charge ODE
│   ├── core/                  # Configuration, logging, Redis connection pool & security/RBAC
│   └── main.py                # ASGI application factory & lifespan event coordinator
├── eval/                      # Formal context quality harness, agent probes & deliberate failure suite
├── tests/                     # 159 comprehensive unit, integration & property-invariant tests
└── pyproject.toml             # uv / pip dependency definitions
```

---

## 🚀 Key Subsystems & Capabilities

### 1. Data Governance & Context Engine (`app/context/`)
- **Strict Data Contracts:** Pydantic v2 schemas validating all incoming telemetry and mission requirements.
- **3-State Asset Lifecycle:** Enforces `VERIFIED`, `DRAFT`, and `DEPRECATED` governance states with automated SLA checks.
- **Bidirectional Lineage DAG:** Cryptographic SHA-256 hash tracking linking every autonomous decision to its upstream telemetry frames and model weights.

### 2. Predictive AI & Anomaly Scoring (`app/intelligence/` & `ml/`)
- **Multi-Head Cross-Attention Ranking:** PyTorch neural ranker achieving **84.6% Top-1 accuracy** and **0.372 ms** inference latency.
- **Spacecraft Health AI:** Multivariate Isolation Forest scoring 14 telemetry features with **85.6% fault recall** and **3.7% false positive rate**.
- **Calibrated Decision & Refusal Engine:** Computes Expected Calibration Error ($ECE < 0.038$), conformal prediction intervals ($90\%$ coverage guarantee), and automatically triggers safe refusal when telemetry is stale or unverified.

### 3. Deterministic Constraint Optimization (`optimization/`)
- **Google OR-Tools CP-SAT Solver:** Verifies battery floors ($\text{SoC} \ge 20\%$), thermal operating boundaries ($-5^\circ\text{C} \le T \le 45^\circ\text{C}$), slew rates ($1.8^\circ/\text{s}$), and Keplerian contact visibility.
- **100% Feasibility Guarantee:** **0.0% constraint violations** across benchmark scenarios.

### 4. FastMCP Tool Protocol Server (`app/mcp_server/`)
- Standardized Model Context Protocol server exposing operational tools (`get_satellite_health`, `get_orbital_pass_geometry`, `query_decision_lineage`) with JSON-schema input validation.

---

## 🧪 Testing & Verification Suite

The backend includes a comprehensive, multi-tiered test and evaluation harness:

```bash
# 1. Run all 159 PyTest Unit & Integration Tests (100% PASS)
uv run pytest tests -v

# 2. Run Formal Context Quality & Governance Harness (98.0% Composite Score)
uv run python eval/run_context_eval.py

# 3. Run 5 Deliberate Failure & Safe Degradation Tests (100% Pass Rate)
uv run python eval/run_deliberate_failure_suite.py

# 4. Run 128-Probe Autonomous Agent Benchmark Harness
uv run python eval/run_agent_harness_benchmark.py

# 5. Run 5-Paradigm ML Ranking Baseline Benchmark Suite
uv run python eval/run_baselines.py
```

---

## ⚡ Quick Start

```bash
# Navigate to backend directory
cd backend

# Install dependencies with uv (or standard pip)
uv sync --python 3.12

# Launch the FastAPI ASGI server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive Swagger Documentation:** `http://localhost:8000/docs`
- **Interactive ReDoc Documentation:** `http://localhost:8000/redoc`
- **Health Check Endpoint:** `http://localhost:8000/health`
