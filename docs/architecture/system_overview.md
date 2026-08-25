# ORBIT-X: System Architecture & Design Specification

## 1. High-Level Architecture

ORBIT-X is designed as a modular, production-ready **Context-Aware Decision Intelligence Platform**. It ingests high-velocity operational data, validates quality, discovers context, predicts candidate feasibility with deep learning, guarantees safety with CP-SAT constraint programming, and provides explainable, auditable agent workflows via the Model Context Protocol (FastMCP) through a 7-stage execution chain:

$$\textbf{Context} \longrightarrow \textbf{Retrieval} \longrightarrow \textbf{Tool} \longrightarrow \textbf{Reasoning} \longrightarrow \textbf{Constraint} \longrightarrow \textbf{Decision} \longrightarrow \textbf{Evidence}$$

```
                         ORBIT-X PLATFORM ARCHITECTURE
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                     │
               DATA LAYER                            AI / ML LAYER
                    │                                     │
              PostgreSQL                              ML Models
              Telemetry                           Anomaly Detection
              Metadata                               SHAP / XAI
              Lineage                               Predictions
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       │
                                 CONTEXT LAYER
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                Metadata             Vector              SQL
                 Search              Search             Query
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                                 Context / RAG
                                       │
                                  AGENT LAYER
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                  Tools             Planning          Reasoning
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
                                DECISION LAYER
                                       │
                                  ML + CP-SAT
                                       │
                                Human Approval
                                       │
                                       ▼
                                    ACTION
                                       │
                                Feedback Loop
                                       │
                                       ▼
                            Evaluation / Improvement
                                       │
                                       ▼
                             Prometheus / Grafana
```

## 2. Layer-by-Layer Architectural Breakdown

### 2.1 Data Engineering Layer
- **Ingestion:** High-frequency telemetry streams, mission requests, subsystem health metrics, and historical operator decisions.
- **Validation & Cleaning:** Schema validation via Pydantic, missing value imputation, outlier clipping, and type verification.
- **Storage:** PostgreSQL for ACID-compliant persistence; Redis 7 for high-speed caching and pub/sub message bus.

### 2.2 Machine Learning & Deep Learning Layer
- **Classical Baselines:** Random, Greedy Earliest Deadline First (EDF), Ridge Linear Regression, Random Forest / XGBoost regressor.
- **Deep Neural Ranking:** Multi-Head Cross-Attention Network (`ConstellationCrossAttentionNet`) learning complex cross-modal interactions between resource availability tokens and mission request demand tokens.
- **Unsupervised Anomaly AI:** Multivariate Isolation Forest scoring multi-sensor telemetry for early degradation detection.
- **Explainable AI (XAI):** TreeSHAP attribution and Cross-Attention heatmap visualizations providing transparent local and global feature explanations.

### 2.3 Semantic Context & Metadata Layer
- **Semantic Entities:** 10 core entity types (`Dataset`, `Mission`, `Satellite`, `TelemetryStream`, `Feature`, `Model`, `Prediction`, `Anomaly`, `Decision`, `Tool`).
- **Knowledge Graph:** Directed property graph maintaining relationships (`generates`, `participates_in`, `produces`, `triggers`, `contains`, `used_by`, `influences`, `affects`).
- **Data Discovery:** Natural language discovery querying dataset schemas, quality metrics, and freshness timestamps without hallucination.
- **Bidirectional Lineage:** Full provenance tracking from raw telemetry to final operational outcomes.

### 2.4 Agent & GenAI Layer
- **Context-Aware RAG:** Hybrid retrieval fusing metadata filters, dense vector search, and SQL structured queries.
- **Model Context Protocol (MCP):** Exposes 10 standardized tool schemas over standard JSON-RPC interface.
- **Agent Planning & Trust Layer:** Multi-step intent understanding, planning, tool selection, evidence collection, and hallucination verification.

### 2.5 Decision Intelligence & Optimization Layer
- **Hybrid ML + CP-SAT:** Decouples fast neural candidate ranking from deterministic constraint optimization using Google OR-Tools CP-SAT.
- **Human-in-the-Loop:** Interactive approval, rejection, and investigation workflows with full audit logging.
- **Continuous Feedback Loop:** Operator decisions are collected into feedback datasets to drive fine-tuning and retrieval optimization.

### 2.6 Simulation & Evaluation Testbed
- **Operational Domain:** High-fidelity LEO satellite constellation simulation generating realistic telemetry, SGP4 orbital propagation, battery degradation, thermal cycles, and eclipse constraints.
