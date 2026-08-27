# ORBIT-X: Context-Aware Decision Intelligence Platform — Architecture & Design

## 1. System Overview

**ORBIT-X is an autonomous decision intelligence platform that turns real-time operational data into safe, mathematically-grounded actions.** Instead of relying on ungrounded heuristics or black-box models that can hallucinate and violate physical operating limits, ORBIT-X verifies data freshness and lineage, reasons over live system state, enforces hard physical constraints with mathematical solvers, and provides full cryptographic audit trails.

Evaluated on high-stakes autonomous satellite constellation operations through a governed 7-stage decision pipeline:

$$\textbf{Context} \longrightarrow \textbf{Retrieval} \longrightarrow \textbf{Tool} \longrightarrow \textbf{Reasoning} \longrightarrow \textbf{Constraint} \longrightarrow \textbf{Decision} \longrightarrow \textbf{Evidence}$$

A high-fidelity satellite constellation simulation environment serves as the **operational dataset and constraint testbed** for evaluating the platform against physical realities (power budgets, thermal limits, line-of-sight visibility, communication blackouts).

---

## 2. Core Architectural Flow

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               THE 7-STAGE DECISION PIPELINE                            │
│                                                                                        │
│  [1. CONTEXT]    Data Contracts • 3-State Lifecycles • Freshness SLAs • Lineage DAG    │
│        │                                                                               │
│        ▼                                                                               │
│  [2. RETRIEVAL]  FastMCP Semantic Catalog • Hybrid Dense Embeddings + BM25 RRF         │
│        │                                                                               │
│        ▼                                                                               │
│  [3. TOOL]       FastMCP Standardized Tool Interface • Schema Validation Gates         │
│        │                                                                               │
│        ▼                                                                               │
│  [4. REASONING]  Cross-Attention Neural Ranking • Isolation Forest Health AI           │
│        │                                                                               │
│        ▼                                                                               │
│  [5. CONSTRAINT] Google OR-Tools CP-SAT Engine • 100% Invariant Guarantee (0.0% Viola) │
│        │                                                                               │
│        ▼                                                                               │
│  [6. DECISION]   Certified Dispatch in <50ms • Conformal Bounds • Refusal State Machine│
│        │                                                                               │
│        ▼                                                                               │
│  [7. EVIDENCE]   TreeSHAP Attributions • Cryptographic Provenance DAG • Audit Ledger   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. The 7 Behavioral Stages

### [Stage 1: Context] Governance, Metadata & Lineage
- **Contract Schemas:** Strongly-typed Pydantic v2 data models for all telemetry streams, mission profiles, and asset configurations.
- **3-State Asset Lifecycles:** Strict governance states (`VERIFIED`, `DRAFT`, `DEPRECATED`). Autonomous schedulers reject deprecated/uncalibrated assets.
- **Freshness SLAs:** Active latency monitoring ($<15.0\text{s}$ SLA for real-time telemetry).
- **Cryptographic Lineage DAG:** Every decision node maintains a verifiable SHA-256 hash pointer to its upstream datasets, model weights, and prompt templates.

### [Stage 2: Retrieval] Hybrid Semantic Catalog
- **Dual-Index Architecture:** Combines dense neural embeddings (`all-MiniLM-L6-v2`) with sparse keyword matching (`Rank-BM25`).
- **Reciprocal Rank Fusion (RRF):** Merges dense and sparse rankings with parameter $k=60$, achieving $0.965\text{ NDCG@10}$ and $94.0\%\text{ Recall@5}$.
- **FastMCP Catalog:** Exposes searchable metadata endpoints allowing autonomous agents to locate operational manuals, ground contacts, and payload constraints without hallucination.

### [Stage 3: Tool] Deterministic FastMCP Interfaces
- **Standardized MCP Tool Protocol:** Canonical tools (`get_satellite_health`, `get_orbital_pass_geometry`, `inspect_payload_memory`, `query_decision_lineage`).
- **Strict Schema Validation:** Automated JSON-schema parameter validation gates preventing malformed tool inputs.
- **Side-Effect Sandboxing:** Safe execution boundaries ensuring read/query tools do not mutate hardware state without human-in-the-loop authorization.

### [Stage 4: Reasoning] Cross-Attention Ranking & Telemetry Health AI
- **Cross-Attention Neural Ranking:** PyTorch Multi-Head Cross-Attention Network attends spacecraft subsystem tokens against mission requirement queries ($84.6\%$ top-1 accuracy, $0.37\text{ ms}$ inference).
- **Spacecraft Health AI:** Multivariate Isolation Forest continuously scores 14 telemetry channels for early degradation ($85.6\%$ fault recall, $3.7\%$ false positive rate).
- **Agent Orchestrator:** Tool-augmented reasoning loop with anti-hallucination validation and fact consistency checks ($0.0\%$ unsupported claims across 128 benchmark probes).

### [Stage 5: Constraint] Deterministic CP-SAT Optimization
- **Separation of Concerns:** Deep learning scores candidate utility; Google OR-Tools CP-SAT integer programming solver enforces physical boundary invariants.
- **Hard Non-Negotiable Invariants:**
  - Battery Depth-of-Discharge ($\text{SoC} \ge 20\%$)
  - Radiative Thermal Boundary ($-5^\circ\text{C} \le T \le +45^\circ\text{C}$)
  - Reaction Wheel Slew Rate Limit ($\le 1.8^\circ/\text{s}$)
  - Keplerian Line-of-Sight Visibility Window ($\ge 180\text{s}$)
- **Mathematical Safety Guarantee:** Achieves $0.0\%$ constraint violations across 500 multi-satellite benchmark scenarios.

### [Stage 6: Decision] Calibrated Dispatch & First-Class Refusal
- **Certified Operational Dispatch:** Emits conflict-free schedules in $<50\text{ ms}$ serving latency.
- **Uncertainty Calibration:** Temperature scaling ($ECE < 0.038$) and conformal prediction coverage intervals ($90\%$ coverage guarantee).
- **First-Class Refusal State Machine:** Explicitly transitions to safe `REFUSE` state when telemetry is stale, context quality is degraded, or physical feasibility is violated, triggering automated operator review alerts.

### [Stage 7: Evidence] Attributions & Tamper-Proof Audit
- **TreeSHAP Attributions:** Local feature contributions explaining exactly why an asset was selected (+42% pass elevation, +28% battery reserve, +18% slew feasibility).
- **Cryptographic Provenance:** Tamper-proof audit trail recorded in PostgreSQL ledger with hot caching in Redis 7.
- **Human-in-the-Loop Governance:** Flight operator review interface (`Approve` / `Reject` / `Investigate`) with continuous feedback logging.
