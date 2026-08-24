# ORBIT-X System Architecture & Technical Specification

> **Engineering Deep-Dive**: Complete architectural design of the ORBIT-X Autonomous Decision Platform.

---

## 1. System Overview

ORBIT-X is designed as a high-throughput, fault-tolerant decision platform operating between streaming operational sensor telemetry and mission execution actions. It bridges the gap between predictive statistical models and strict operational safety by combining:

1. **High-Velocity Telemetry Processing & Feature Pipelines**
2. **Predictive Machine Learning & Unsupervised Anomaly Detection**
3. **Deterministic Constraint Programming (Google OR-Tools CP-SAT)**
4. **Governed Context Layer & 10-Entity Bidirectional Lineage**
5. **Tool-Augmented Reasoning via Model Context Protocol (FastMCP)**
6. **Defensive Safe Degradation & Anti-Hallucination Guardrails**

```
                         ┌──────────────────────────────────────────────┐
                         │         ORBIT-X SYSTEM ARCHITECTURE          │
                         └──────────────────────────────────────────────┘

     STREAMING INGEST                                        PERSISTENCE & LINEAGE
   ┌──────────────────┐                                     ┌─────────────────────┐
   │ High-rate Sensor │                                     │ PostgreSQL 16       │
   │ Telemetry Streams│───┐                                 │ (Audit / Entities)  │
   └──────────────────┘   │                                 └──────────┬──────────┘
                          ▼                                            │
               ┌───────────────────────┐                    ┌──────────┴──────────┐
               │    Data Processing    │◄──────────────────►│ Governed Context    │
               │  Validation & Features│                    │ Graph & 10-Node DAG │
               └──────────┬────────────┘                    └─────────────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
 ┌──────────────────────┐    ┌──────────────────────┐
 │  Prediction Pipeline │    │  Anomaly Detection   │
 │ Multi-Head Attention │    │ Isolation Forest     │
 │  Neural Ranking Net  │    │ Multi-Sensor Health  │
 └──────────┬───────────┘    └──────────┬───────────┘
            │                           │
            └─────────────┬─────────────┘
                          ▼
               ┌───────────────────────┐
               │   Constraint Solver   │◄── Hard Physical Constraints:
               │ Google OR-Tools CP-SAT│    Power / Thermal / Slew / Orbit
               └──────────┬────────────┘
                          ▼
               ┌───────────────────────┐
               │    Final Decision     │
               │   Validated Action    │
               └──────────┬────────────┘
                          ▼
               ┌───────────────────────┐
               │ Explanation & Evidence│◄── FastMCP Agent Tools +
               │ 5-Pillar Verification │    Hybrid RAG (Dense + BM25)
               └───────────────────────┘
```

---

## 2. End-to-End Decision Flow

Every mission scheduling and resource allocation decision follows an auditable 6-stage lifecycle:

```
Mission Request
      │
      ▼
Context Retrieval ────────── Query metadata catalog, freshness SLAs, and orbital ephemeris
      │
      ▼
ML Prediction ────────────── Cross-Attention network scores candidate satellite suitability
      │
      ▼
Anomaly / Health Check ───── Isolation Forest flags anomalous subsystems and power sags
      │
      ▼
Constraint Optimization ──── Google OR-Tools CP-SAT solves global invariant feasibility
      │
      ▼
Final Decision ───────────── Conflict-free assignment generated in <10ms
      │
      ▼
Why this satellite? ──────── 5-Pillar evidence generation with TreeSHAP & verifiable citations
```

---

## 3. Subsystem Breakdown

### 3.1 Data Ingestion & Context Layer
- **Telemetry Processing**: Ingests multi-sensor time-series frames (battery voltage, cell temperature, reaction wheel speed, solar flux).
- **Metadata Catalog**: Maintains data schemas, access controls, freshness thresholds, and asset status (`ACTIVE`, `DEPRECATED`, `STALE`).
- **Bidirectional Lineage**: 10-node Directed Acyclic Graph (DAG) mapping `Telemetry` $\to$ `Feature` $\to$ `Model` $\to$ `Prediction` $\to$ `Decision` $\to$ `Operator Action`.
- **Freshness SLA Guard**: Enforces max allowable latency (e.g., 30 minutes for flight telemetry). Stale assets automatically trigger safe refusal.

### 3.2 Machine Learning & Neural Ranking
- **Multi-Head Cross-Attention Network**: Computes dense cross-attention between spacecraft resource state embeddings ($D=64$) and mission target embeddings ($D=64$), predicting optimal match scores.
- **Huber Loss Regression**: Robust against outlier operational costs and sudden orbital geometry changes.
- **Multivariate Isolation Forest**: Unsupervised anomaly detection trained on normal orbital operating regimes to detect degradation before threshold alarms trip.

### 3.3 Constraint Optimization Engine
- **Solver**: Google OR-Tools CP-SAT (Constraint Programming with Satisfiability).
- **Hard Invariants Enforced**:
  1. *Battery Depth of Discharge*: $DoD(t) \le 65\%$ throughout eclipse pass.
  2. *Thermal Envelope*: $T_{battery} \in [-5^\circ\text{C}, +45^\circ\text{C}]$.
  3. *Reaction Wheel Slew Rates*: Max slew rate $\le 1.8^\circ/\text{s}$ with jitter stabilization window.
  4. *Line-of-Sight & Elevation*: Minimum ground station elevation angle $\ge 15^\circ$.
  5. *Inter-Satellite Link (ISL) Bandwidth*: Channel capacity limits on laser cross-links.

### 3.4 Agent Reasoning & FastMCP Layer
- **Model Context Protocol (FastMCP)**: Standardized tool interface exposing operational APIs (`get_satellite_telemetry`, `run_anomaly_diagnostic`, `solve_mission_schedule`, `get_lineage_trace`, `explain_decision_shap`).
- **Hybrid RAG**: Multi-stage retrieval combining SentenceTransformers dense embeddings with BM25 sparse lexical search and Reciprocal Rank Fusion ($k=60$).
- **Anti-Hallucination Trust Layer**: Every generated assertion must be backed by a verified telemetry citation; refuses requests with unverified provenance or stale telemetry.

---

## 4. Production Serving & Latency Budget

| Component | Target SLA | Measured p50 | Measured p95 | Measured p99 |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry Ingestion** | $< 5\text{ ms}$ | $0.8\text{ ms}$ | $1.9\text{ ms}$ | $3.5\text{ ms}$ |
| **Anomaly Scoring** | $< 10\text{ ms}$ | $1.2\text{ ms}$ | $2.6\text{ ms}$ | $4.8\text{ ms}$ |
| **Neural Candidate Ranking** | $< 25\text{ ms}$ | $3.5\text{ ms}$ | $6.2\text{ ms}$ | $9.8\text{ ms}$ |
| **CP-SAT Constraint Solver** | $< 50\text{ ms}$ | $4.8\text{ ms}$ | $11.4\text{ ms}$ | $18.2\text{ ms}$ |
| **Agent Reasoning & RAG** | $< 100\text{ ms}$ | $12.4\text{ ms}$ | $24.8\text{ ms}$ | $42.0\text{ ms}$ |
| **End-to-End Decision Loop** | $< 150\text{ ms}$ | **$22.7\text{ ms}$** | **$46.9\text{ ms}$** | **$78.3\text{ ms}$** |

---

## 5. Failure Recovery & Defensive Modes

| Failure Mode | Detection Mechanism | System Action | Operator Impact |
| :--- | :--- | :--- | :--- |
| **Stale Telemetry ($>30\text{m}$)** | Timestamp audit against SLA | Safe refusal of automatic execution | Operator alerted to acquire fresh TLE/telemetry pass |
| **Missing Provenance** | Lineage graph traversal | Rejection of unverified context | Prevents hallucinated data ingestion |
| **Tool / API 503 Outage** | Exponential backoff retry | Fallback to cached deterministic heuristics | Safe degraded operation without downtime |
| **Nonexistent Asset Query** | Catalog entity validation | Explicit refusal (`SAT-99 does not exist`) | Zero hallucinated responses |
