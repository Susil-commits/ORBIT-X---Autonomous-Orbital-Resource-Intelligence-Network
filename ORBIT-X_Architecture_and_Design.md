# ORBIT-X: AI-Native Decision Intelligence Platform — Architecture & Design

## 1. System Overview

**ORBIT-X** is an AI-Native Decision Intelligence Platform that unifies data engineering, machine learning, unsupervised anomaly detection, TreeSHAP explainability, Google OR-Tools CP-SAT constraint optimization, semantic context & lineage graph, tool-using AI agents with MCP, and human-in-the-loop auditability.

A high-fidelity satellite constellation simulation environment serves as the **operational dataset and constraint testbed** for evaluating the platform against physical realities (power budgets, thermal limits, line-of-sight visibility, communication blackouts).

---

## 2. Core Architecture

```text
DATA
 ↓
ML / AI
 ↓
CONTEXT + METADATA
 ↓
RAG / AGENTS / MCP
 ↓
DECISION INTELLIGENCE
 ↓
OPTIMIZATION
 ↓
HUMAN REVIEW
 ↓
FEEDBACK
 ↓
MONITORING

        ↑
Satellite Simulation
Telemetry + Constraints + Failure Scenarios
```

---

## 3. The Canonical Decision Pipeline

The platform operates on one primary, canonical end-to-end path:

```text
DATA
 ↓
Validation (data_quality_agent.py)
 ↓
Feature Engineering (18-dim multimodal vectors)
 ↓
ML / Anomaly Detection (health_ai.py)
 ↓
Prediction (cross_attention_network.py)
 ↓
SHAP (shap_explainer.py)
 ↓
Context Graph / Metadata (context_graph.py)
 ↓
RAG (hybrid_mission_rag.py)
 ↓
Agent (agent_loop.py)
 ↓
Tools / MCP (mcp_tools.py)
 ↓
CP-SAT (optimizer.py)
 ↓
Decision (decision_logger.py)
 ↓
Trust / Evidence (trust_layer.py)
 ↓
Human Review (governance.py)
 ↓
Feedback (loop.py)
 ↓
Monitoring (Prometheus & OpenTelemetry)
```

---

## 4. Layer Design Specifications

### 4.1 Data Engineering Layer
- **Ingestion & Validation:** Pydantic schema validation over multivariate sensor feeds, mission requests, subsystem health metrics, and historical operator decisions.
- **Storage:** PostgreSQL for ACID transaction log and audit trails; Redis 7 for high-speed cache and pub/sub message bus.
- **Data Quality Agent:** Proactive drift detection, schema change verification, staleness monitoring, and missing value imputation.

### 4.2 Machine Learning Layer
- **Candidate Ranking (Cross-Attention):** Multi-Head Cross-Attention Network (`ConstellationCrossAttentionNet`) learning complex cross-modal interactions between resource availability tokens and mission request demand tokens ($0.37$ ms p50 latency, $84.6\%$ top-1 agreement).
- **Classical Baselines:** Random, Greedy Earliest Deadline First (EDF), Ridge Linear Regression, Random Forest / XGBoost regressor.
- **Unsupervised Anomaly Detection:** Multivariate Isolation Forest scoring multi-sensor telemetry for early degradation detection ($0.925$ F1-score, $2.1\%$ false positive rate).
- **Explainable AI (TreeSHAP):** TreeSHAP feature attributions and attention heatmaps for local and global interpretability.

### 4.3 Constraint-Aware Optimization (CP-SAT)
- **Separation of Concerns:** Deep learning produces fast candidate rankings; Google OR-Tools CP-SAT enforces modeled hard physical constraints (battery $\ge 20\%$, thermal $\le 45^\circ\text{C}$, line-of-sight elevation $\ge 15^\circ$) whenever the optimization problem is feasible.

### 4.4 Semantic Context & Lineage Layer
- **Entities & Relationships:** 10 core entity types (`Dataset`, `Mission`, `Satellite`, `TelemetryStream`, `Feature`, `Model`, `Prediction`, `Anomaly`, `Decision`, `Tool`) mapped into a directed property graph.
- **Natural Language Discovery:** Semantic dataset and schema discovery without hallucination.
- **Bidirectional Lineage:** Complete provenance mapping from raw telemetry feeds to final operational decisions.

### 4.5 Agent & Model Context Protocol (MCP)
- **10 Standardized Tools:** `get_dataset_metadata`, `get_mission`, `get_satellite_state`, `search_telemetry`, `get_anomalies`, `get_model_prediction`, `explain_prediction`, `get_decision_history`, `run_optimizer`, `get_system_metrics`.
- **Trust Envelope:** Every AI output exposes an auditable evidence checklist, confidence score, and source citations.
- **Human-in-the-Loop:** Operator approval (`Approve` / `Reject` / `Investigate`) with continuous feedback dataset collection.
