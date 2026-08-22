# Context & Metadata Layer: Semantic Graph, Discovery, and Lineage

## 1. Overview
The **Context & Metadata Layer** transforms raw tabular databases and machine learning endpoints into a semantic knowledge graph. It provides semantic data discovery, automated cataloging, and end-to-end bidirectional data lineage for every operational decision.

---

## 2. Semantic Graph Architecture

### 2.1 Core Entities (10 Types)
1. **`Dataset`:** Structured collections of operational data (e.g. `satellite_telemetry`, `mission_requests`).
2. **`Mission`:** Operational objectives and task requests (e.g. `M-204 Disaster Response`).
3. **`Satellite`:** Physical orbital assets and sensor platforms (e.g. `S-21 Sentinel`).
4. **`TelemetryStream`:** Real-time sensor channels (e.g. `battery_soc_stream`, `thermal_bus_stream`).
5. **`Feature`:** Reusable engineered mathematical features (e.g. `elevation_norm`, `energy_cost_ratio`).
6. **`Model`:** Machine learning and neural models (e.g. `ConstellationCrossAttentionNet`, `IsolationForestHealth`).
7. **`Prediction`:** Inference outputs produced by models (e.g. `BidValue=88.4`, `AnomalyScore=-0.14`).
8. **`Anomaly`:** Identified telemetry deviations and subsystem warnings.
9. **`Decision`:** Final resource assignments and scheduling commands approved or executed.
10. **`Tool`:** Executable agent capabilities and MCP tools.

### 2.2 Entity Relationships

```
              ┌───────────────┐
              │   Satellite   │
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │ generates   │ participates│ produces    │ triggers
        ▼             ▼             ▼             ▼
   Telemetry       Mission       Dataset       Anomaly
        │                           │             │
        │ contains                  │ contains    │ affects
        ▼                           ▼             ▼
     Feature ──────────────────►  Model ─────► Decision
                                    │             ▲
                                    │ produces    │ influences
                                    ▼             │
                                Prediction ───────┘
```

---

## 3. Metadata Layer Schema

Every dataset, model, and feature maintains structured metadata in the catalog:

```json
{
  "dataset": "satellite_telemetry",
  "owner": "operations-team",
  "description": "High-frequency multivariate operational telemetry covering battery, thermal, and RF subsystems",
  "schema_version": "v2.2.0",
  "quality_score": 0.984,
  "freshness_seconds": 12,
  "upstream_sources": [
    "ground_station_receiver_01",
    "inter_satellite_link_relay"
  ],
  "downstream_consumers": [
    "anomaly_detector_isolation_forest",
    "cross_attention_ranker",
    "flight_director_hud"
  ],
  "sensitivity_level": "OPERATIONAL_CONFIDENTIAL",
  "fields": [
    {"name": "battery_soc", "type": "float", "unit": "percentage", "range": [0, 100]},
    {"name": "internal_temp_c", "type": "float", "unit": "celsius", "range": [-20, 65]},
    {"name": "power_draw_w", "type": "float", "unit": "watts", "range": [10, 450]}
  ]
}
```

---

## 4. Natural Language Data Discovery

The context layer exposes semantic search over metadata records, enabling operators and AI agents to discover datasets through natural language without hallucinations:

### Example Queries & Grounded System Responses:
1. **Query:** *"Show me datasets containing battery telemetry."*
   - **System Resolution:** Searches semantic embeddings and metadata fields.
   - **Grounded Output:** Returns `satellite_telemetry` and `historical_power_logs` with exact fields (`battery_soc`, `battery_temp`, `charge_rate`).
2. **Query:** *"Which dataset is freshest?"*
   - **System Resolution:** Evaluates `freshness_seconds` property across active datasets.
   - **Grounded Output:** `satellite_telemetry (updated 12 seconds ago)` vs `ground_station_schedule (updated 4 hours ago)`.

---

## 5. Bidirectional Data Lineage

Lineage tracking maps the complete provenance path for every decision and dataset:

```
  Raw Telemetry (7-dim Sensor Stream)
                │
                ▼
  Cleaned Dataset (Quality: 0.984, Validated)
                │
                ▼
  Feature Table (18-dim Standardized Vectors)
                │
                ▼
  ML Model (ConstellationCrossAttentionNet v2.2)
                │
                ▼
  Prediction (Candidate S-17 Score: 94.2)
                │
                ▼
  Optimization (Google OR-Tools CP-SAT Validation)
                │
                ▼
  Decision (Assigned Mission M-204 -> Satellite S-17)
                │
                ▼
  Mission Outcome (Successful Imaging Pass, SNR: 28 dB)
```

### Auditing Capabilities:
- **Forward Impact Analysis:** *"Which models depend on this dataset?"* $\rightarrow$ Returns list of dependent models, feature pipelines, and downstream APIs.
- **Backward Provenance Audit:** *"What data influenced this decision?"* $\rightarrow$ Returns exact telemetry snapshot, feature vector, model weights version, SHAP attribution, and CP-SAT solver parameters.
