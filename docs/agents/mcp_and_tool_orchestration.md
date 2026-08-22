# AI Agents & Model Context Protocol (MCP): Tool Orchestration, Trust, and Observability

## 1. Overview
The ORBIT-X Agent Layer connects Large Language Models (LLMs) to real backend operational infrastructure via the **Model Context Protocol (MCP)**, structured tool calling, deterministic validation gates, and an auditable trust layer.

---

## 2. Agent Planning & Execution Lifecycle

```
                           AGENT PLANNING LIFECYCLE
                                       │
                                  User Query
                                       │
                                       ▼
                             Intent Understanding
                                       │
                                       ▼
                              Multi-Step Planning
                                       │
                                       ▼
                                Tool Selection
                                       │
                                       ▼
                                Tool Execution
                           (MCP Protocol / JSON-RPC)
                                       │
                                       ▼
                              Evidence Collection
                                       │
                                       ▼
                             Grounded Reasoning
                                       │
                                       ▼
                             Trust & Hallucination
                               Verification Gate
                                       │
                                       ▼
                         Auditable Operator Response
                                       │
                                       ▼
                           Human-in-the-Loop Review
```

---

## 3. Structured Agent & MCP Tools

ORBIT-X implements 10 standardized tool schemas exposed via both native Python callers and the Model Context Protocol (MCP) server (`backend/app/mcp_server/server.py`):

| Tool Name | Parameters | Return Schema | Purpose |
|---|---|---|---|
| `get_dataset_metadata` | `dataset_name: str` | `DatasetMetadataDict` | Query semantic catalog, quality score, freshness, and fields. |
| `get_mission` | `mission_id: str` | `MissionDetailDict` | Retrieve mission requirements, target coords, priority, and deadlines. |
| `get_satellite_state` | `satellite_id: str` | `SatelliteTelemetryDict` | Retrieve live telemetry, battery SoC, temperature, and orbit status. |
| `search_telemetry` | `query: str, time_range_min: int` | `List[TelemetryPoint]` | Multivariate search across sensor channels and historical streams. |
| `get_anomalies` | `satellite_id: str` | `List[AnomalyRecord]` | Fetch active Isolation Forest anomaly detections and severity scores. |
| `get_model_prediction`| `satellite_id: str, mission_id: str` | `BidPredictionDict` | Query neural Cross-Attention ranking suitability score. |
| `explain_prediction` | `satellite_id: str, mission_id: str` | `SHAPExplanationDict` | Retrieve TreeSHAP local feature attributions and attention heatmap. |
| `get_decision_history`| `limit: int = 10` | `List[DecisionRecord]` | Fetch historical operational assignments and human review outcomes. |
| `run_optimizer` | `mission_ids: List[str]` | `OptimizationResultDict`| Execute Google OR-Tools CP-SAT hard constraint optimization. |
| `get_system_metrics` | `subsystem: str = "all"` | `SystemHealthMetrics` | Query latency, queue lengths, memory usage, and error counts. |

---

## 4. Hero Feature: "Ask ORBIT-X" Deep Investigation

When an operator queries a critical operational issue, ORBIT-X executes an autonomous multi-step investigation:

### Example Query:
> *"Why is Mission M-204 at risk and what should we do?"*

### Autonomous Agent Execution Trace:
1. **`classify_intent`:** Identifies risk assessment and operational replanning task.
2. **`get_mission("M-204")`:** Retrieves priority (Priority 1: Disaster Imaging), deadline (in 18 min), target (Lat 34.05, Lon -118.25).
3. **`get_satellite_state("S-21")`:** Live telemetry reveals battery SoC at 24.5%, internal temp at 48.2°C (nominal max 45°C).
4. **`get_anomalies("S-21")`:** Isolation Forest detected thermal anomaly ($S = -0.142$, Severity: HIGH).
5. **`get_model_prediction("S-21", "M-204")`:** Cross-Attention score drops to 32.4/100 due to battery-thermal penalties.
6. **`explain_prediction("S-21", "M-204")`:** TreeSHAP indicates negative attribution: `internal_temp_c` (-28.4), `battery_soc` (-22.1).
7. **`run_optimizer(["M-204"])`:** CP-SAT re-evaluates candidate pool; identifies Satellite **S-17** as optimal (SoC: 88%, Temp: 22°C, Score: 94.2).
8. **`generate_grounded_response`:** Synthesizes structured recommendation with auditable evidence checklist.
9. **`trust_verification`:** Verifies facts against source records; calculates Confidence = 91%.
10. **`request_human_approval`:** Dispatches action card to UI with `[Approve]` `[Reject]` `[Investigate]` buttons.

---

## 5. Trust & Grounding Layer

Every AI response generated by ORBIT-X exposes an auditable trust envelope:
- **Confidence Score:** Probabilistic metric based on telemetry freshness, model certainty, and constraint slack.
- **Evidence Checklist:** Clickable direct references to underlying telemetry points, anomaly alerts, and SHAP explanations.
- **Tool Trace Log:** Complete record of tool invocations, inputs, execution latencies, and output payloads.

---

## 6. Human-in-the-Loop & Feedback Loop

```
  Agent Recommendation
          │
          ▼
    Human Review (Approve / Reject / Investigate)
          │
          ▼
   Executed Action & Audit Record (PostgreSQL)
          │
          ▼
    Feedback Dataset (`human_feedback_history.json`)
          │
          ▼
  Continuous Model Evaluation & Prompt Refinement
          │
          ▼
     New Model Checkpoint / Production Version
```

---

## 7. Agent Observability & Prometheus Metrics

ORBIT-X exposes granular metrics on agent and tool performance:
- `orbitx_agent_latency_seconds`: Histogram of total agent reasoning and execution time.
- `orbitx_agent_tool_calls_total`: Counter of tool calls labeled by tool name and status.
- `orbitx_agent_tool_failures_total`: Counter of failed tool invocations.
- `orbitx_rag_retrieval_latency_seconds`: Histogram of vector and metadata retrieval speed.
- `orbitx_grounding_verification_score`: Gauge tracking factual grounding confidence.
