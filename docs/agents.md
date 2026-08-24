# ORBIT-X Agent & Tooling Architecture (FastMCP)

> **Engineering Deep-Dive**: Autonomous reasoning agents, FastMCP tool integration, Hybrid RAG, and anti-hallucination verification.

---

## 1. Overview of the Agent Layer

ORBIT-X uses a tool-augmented autonomous reasoning agent built on the **Model Context Protocol (FastMCP)**. Rather than relying on unconstrained LLM text generation, the agent follows a strict **Plan $\to$ Execute $\to$ Verify $\to$ Explain** loop where every action requires certified schema contracts and verifiable telemetry evidence.

```
                           ┌────────────────────────────┐
                           │      USER / OPERATOR       │
                           │   "Ask ORBIT-X" Query      │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │      AGENT CONTROLLER      │
                           │   Multi-Step Intent Parse  │
                           └─────────────┬──────────────┘
                                         │
               ┌─────────────────────────┴─────────────────────────┐
               ▼                                                   ▼
┌─────────────────────────────┐                     ┌─────────────────────────────┐
│       HYBRID RAG CORE       │                     │    FastMCP TOOL REGISTRY    │
│ Dense MiniLM + BM25 Sparse  │                     │  10 Validated JSON-RPC Tools│
│ Reciprocal Rank Fusion      │                     │  Pydantic Contract Envelopes│
└──────────────┬──────────────┘                     └──────────────┬──────────────┘
               │                                                   │
               └─────────────────────────┬─────────────────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │    TRUST & VERIFICATION    │
                           │ 5-Pillar Evidence Gate     │
                           │ Safe Refusal on Anomaly    │
                           └─────────────┬──────────────┘
                                         │
                                         ▼
                           ┌────────────────────────────┐
                           │    STRUCTURED RESPONSE     │
                           │ Recommendation + Evidence  │
                           └────────────────────────────┘
```

---

## 2. FastMCP Tool Registry

The agent interacts with the underlying operational platform through 10 strictly typed FastMCP tools:

| Tool Name | Input Schema | Output Type | Description |
| :--- | :--- | :--- | :--- |
| `get_satellite_telemetry` | `sat_id: str, window_s: int` | `TelemetryFrame` | Fetches live sensor telemetry for a given satellite. |
| `get_subsystem_health` | `sat_id: str` | `HealthReport` | Runs Isolation Forest anomaly detection on telemetry. |
| `get_orbital_passes` | `sat_id: str, target: Coord` | `List[PassWindow]` | SGP4 orbit propagation pass window calculation. |
| `predict_mission_suitability`| `sat_id: str, mission: Mission` | `SuitabilityScore` | Executes Multi-Head Cross-Attention neural ranking. |
| `solve_constellation_schedule`| `missions: List[Mission]` | `SchedulePlan` | Google OR-Tools CP-SAT deterministic solver. |
| `get_lineage_provenance` | `asset_id: str` | `LineageTrace` | 10-node DAG lineage trace back to raw telemetry. |
| `explain_decision_shap` | `decision_id: str` | `ShapExplanation` | Generates TreeSHAP feature importance breakdown. |
| `audit_context_freshness` | `dataset_id: str` | `SlaReport` | Validates data timestamps against freshness SLAs. |
| `query_operational_logs` | `query: str, top_k: int` | `List[LogRecord]` | Hybrid Dense + Sparse BM25 RAG search. |
| `execute_emergency_hold` | `sat_id: str, reason: str` | `HoldConfirmation`| Safe fallback halting automated commands on fault. |

---

## 3. Hybrid RAG Pipeline (Dense + BM25 with RRF)

To query operational flight rules, anomaly logs, and past mission debriefs with zero hallucination, ORBIT-X implements a **Hybrid Retrieval-Augmented Generation (RAG)** pipeline:

### 3.1 Retrieval Scoring Formula
For a given query $q$ across documents $d \in \mathcal{D}$:

$$\text{RRF\_Score}(d) = \frac{1}{k + \text{Rank}_{\text{Dense}}(d)} + \frac{1}{k + \text{Rank}_{\text{BM25}}(d)}$$

where smoothing constant $k = 60$.

### 3.2 Retrieval Benchmark Performance ($N=40$ Queries)

| Metric | Dense Vector Embeddings Only | BM25 Lexical Matching Only | Hybrid Dense + BM25 + RRF | Improvement |
| :--- | :--- | :--- | :--- | :--- |
| **NDCG@3** | $0.812$ | $0.732$ | **$0.955$** | **+30.4%** |
| **NDCG@10** | $0.845$ | $0.793$ | **$0.965$** | **+21.6%** |
| **Recall@5** | $33.0\%$ | $28.5\%$ | **$37.0\%$** | **+12.1%** |
| **MRR** | $0.653$ | $0.612$ | **$0.744$** | **+13.8%** |

---

## 4. Practical Agent Example: "Ask ORBIT-X"

### Query:
```
"Which satellite is best suited for high-resolution optical observation of Target Alpha (Mission 42) at 14:30 UTC, and why?"
```

### Agent Internal Execution Trace:
1. `audit_context_freshness(dataset="telemetry_stream")` $\to$ **PASS** (Freshness: 1.2 min, SLA: 30 min)
2. `get_orbital_passes(target="Target Alpha", window=3600)` $\to$ `SAT-03`, `SAT-07`, `SAT-12` in view.
3. `get_subsystem_health(sat_id="SAT-03")` $\to$ **Nominal (Health: 98.4%)**
4. `predict_mission_suitability(sat_id="SAT-03", mission="M42")` $\to$ **Predicted Score: 94.2**
5. `solve_constellation_schedule(candidate="SAT-03")` $\to$ **Feasible (Constraints: 8/8 satisfied)**

### Structured User-Facing Response:
```yaml
Recommended: SAT-03
Confidence: 94.2%

Decision Rationale:
  • Subsystem Health: 98.4% (No anomalous telemetry detected)
  • Power Availability: High (Battery DoD 38% vs 65% ceiling)
  • Geometry Window: 96.8% (Peak elevation 72°, Slew angle 12°)
  • Predicted Success: 94.2/100 (Top-1 neural candidate ranking)

Constraints Checked: 8/8 Verified
  [x] Battery Thermal Envelope: 18.4°C (Limit: [-5°C, 45°C])
  [x] Reaction Wheel Slew Rate: 1.1°/s (Limit: 1.8°/s)
  [x] Ground Station ISL Window: 320s contact window verified
  [x] Solar Array Sun-Pointing Margin: Compliant

Evidence & Lineage:
  Telemetry Stream -> Feature Extraction -> CrossAttentionNet -> CP-SAT Solver -> Decision
  Lineage ID: LIN-8849-SAT03 | Freshness: 1.2m ago (SLA: 30m)
```
