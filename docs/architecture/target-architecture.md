# ORBIT-X Target Architecture: AI-Native Decision Intelligence Platform

## 1. Executive Summary & Identity

**ORBIT-X** is an end-to-end **AI-Native Decision Intelligence Platform** designed to transform high-velocity operational data into grounded, explainable, and constraint-satisfying decisions. 

A high-fidelity orbital mechanics simulator serves as the ground-truth **evaluation environment and telemetry generator**, providing realistic operational constraints, communication mesh dynamics, and fault scenarios to evaluate the platform without coupling its core abstractions to aerospace physics.

```
Operational Data & Telemetry (Simulator / Ingestion)
      │
      ▼
Schema Validation & Cleaning (Pydantic / Quality Agent)
      │
      ▼
Machine Learning & Anomaly Detection (Cross-Attention / Isolation Forest / TreeSHAP)
      │
      ▼
Context, Semantic Metadata & Lineage (Context Graph / Provenance DAG)
      │
      ▼
RAG, Agents & Tool Orchestration (Hybrid Dense+BM25 / MCP Server / Trust Layer)
      │
      ▼
Constraint-Aware Decision Intelligence (ML Ranking ──► Google CP-SAT Optimizer)
      │
      ▼
Human-in-the-Loop Review & Approval (Approve / Reject / Investigate / Execute)
      │
      ▼
Persistent Audit & Continuous Evaluation (PostgreSQL Ledger / Redis Hot Cache / Prometheus Metrics)
```

---

## 2. Core Architectural Subsystems

### 2.1 Data Engineering & Semantic Metadata Layer
- **Pydantic v2 Type Safety**: Strict schemas for `TelemetryFrame`, `MissionRequest`, `AnomalyReport`, `DecisionCandidate`, and `AuditRecord`.
- **Reusable Feature Extraction**: Modular 7-dimensional feature engineering functions (Battery Margin, Thermal Headroom, Slew Feasibility, ISL Latency, Token Alignment) separated from training routines.
- **Semantic Data Catalog**: Searchable metadata layer tracking dataset freshness SLAs, ownership, schema definitions, and downstream model consumers.
- **Bidirectional Data Lineage**: Complete provenance tracing answering *"What data influenced this decision?"* and *"Which models depend on this dataset?"*.

### 2.2 Machine Learning & Neural Ranking (Cross-Attention Hero)
- **Multi-Head Cross-Attention Network**: Models resource-state tokens against mission-requirement tokens to output valuation scores, win probabilities, and feasibility metrics.
- **Empirical Baseline Suite**: Benchmarked against `RandomBaseline`, `GreedyEDFBaseline`, `RidgeBaseline`, `RandomForestBaseline`, and `BidValueMLPBaseline`.
- **Reproducible Evidence Hierarchy**: Formal held-out evaluation, feature ablation studies (`experiments/feature_ablation`), and error analysis (`experiments/error_analysis`).
- **Model Card Authority**: Comprehensive documentation in `docs/models/cross-attention-model-card.md`.

### 2.3 Multivariate Anomaly Detection & TreeSHAP XAI
- **Isolation Forest Health Engine**: Unsupervised anomaly scoring over multivariate sensor streams (temperatures, discharge rates, angular velocities) with configurable sigma thresholds.
- **TreeSHAP Feature Attribution**: Explains both why a candidate was **chosen** (e.g. high battery headroom) and why candidates were **rejected** (e.g. thermal excursion +3.2σ).
- **Decision Workflow Integration**: Anomalies automatically gate candidates prior to CP-SAT integer optimization.

### 2.4 Hybrid RAG, Autonomous Agents & Model Context Protocol (MCP)
- **Hybrid Dense + BM25 Retrieval**: Combines semantic embeddings with exact keyword BM25 retrieval over mission history, anomaly logs, and system manuals.
- **Model Context Protocol (MCP)**: Exposes standardized JSON-schema tools (`get_constellation_status`, `preview_satellite_bid`, `ask_mission_history`, `trigger_scenario`, `query_decision_lineage`).
- **Trust & Grounding Verification**: Enforces fact consistency, generates source citations, and executes honest refusals upon detecting insufficient context.

### 2.5 Deterministic Decisioning & Human-in-the-Loop (HITL)
- **Google OR-Tools CP-SAT**: Solves multi-objective integer programming to enforce modeled physical constraints (line-of-sight visibility, battery depth of discharge, thermal boundaries) when feasible.
- **Human Approval Gate**: Multi-state decision lifecycle (`proposed`, `approved`, `rejected`, `investigate`, `executed`) with auditable reviewer rationales.
- **Feedback Dataset**: Operator decisions feed a PostgreSQL evaluation repository for continuous validation.

### 2.6 Production Serving & Infrastructure
- **FastAPI Modular Microservices**: Clean domain routers (`/api/ai`, `/api/context`, `/api/experiments`, `/api/simulation`, `/api/missions`).
- **Persistence & Caching**: PostgreSQL for durable decision ledgers and lineage; Redis 7 for hot state and distributed locking.
- **Observability**: Prometheus metrics, structured JSON logging with correlation IDs, and Grafana dashboard integration.

---

## 3. Evaluation Domain: Orbital Mechanics Simulator

The simulator models:
- Keplerian two-body + J2 oblateness orbit propagation.
- CelesTrak TLE ingestion and Starlink-style Walker Delta constellations.
- Dynamic Line-of-Sight (LOS) visibility and eclipse shadow modeling.
- 10 operational resilience failure scenarios (Thermal runaway, solar flare, ISL degradation, GPS loss, thruster blowout, cyber spoofing).

All physics equations and derivations are isolated in `docs/simulation/physics.md`.
