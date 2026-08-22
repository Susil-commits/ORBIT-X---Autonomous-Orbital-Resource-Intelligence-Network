# ORBIT-X API: Endpoints Reference & OpenAPI Specification

## 1. Overview
The ORBIT-X backend exposes asynchronous REST, WebSocket, and Prometheus endpoints for model serving, anomaly detection, semantic context exploration, agent interaction, and decision governance.

- **Base URL:** `http://localhost:8000`
- **Interactive Documentation:** `http://localhost:8000/docs` (Swagger UI) / `http://localhost:8000/redoc` (ReDoc)
- **Framework:** FastAPI (ASGI / Uvicorn)

---

## 2. API Endpoints Catalog

### 2.1 Model Serving & Inference
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/models` | List all available model architectures, versions, and champion status. |
| `POST` | `/api/models/predict` | Run neural Cross-Attention candidate ranking or MLP bid value estimation. |
| `POST` | `/api/models/explain` | Generate TreeSHAP local feature attributions and attention heatmap. |
| `GET` | `/api/models/benchmarks` | Retrieve latest measured baseline comparison and ablation reports. |

### 2.2 Anomaly Detection & Health Scoring
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/health/detect` | Run multivariate Isolation Forest scoring over input telemetry vector. |
| `GET` | `/api/health/status` | Retrieve current constellation health scores and active anomaly alerts. |
| `POST` | `/api/health/threshold`| Dynamically update or calibrate the anomaly contamination threshold. |

### 2.3 Semantic Context, Metadata & Lineage
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/context/datasets` | List all registered datasets with owner, quality, and schema versions. |
| `POST` | `/api/context/discover` | Natural language dataset discovery ("Show me datasets containing battery..."). |
| `GET` | `/api/context/metadata/{name}` | Retrieve comprehensive metadata record for a specific dataset or model. |
| `GET` | `/api/context/lineage/{entity_id}` | Retrieve bidirectional data lineage DAG from raw inputs to decisions. |
| `GET` | `/api/context/graph` | Fetch complete knowledge graph nodes and edges for interactive visualization. |

### 2.4 Autonomous AI Agent & MCP
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/agent/query` | Execute autonomous "Ask ORBIT-X" multi-step investigation loop. |
| `POST` | `/api/agent/rag` | Query hybrid context-aware RAG engine (Metadata + Dense Vectors + SQL). |
| `GET` | `/api/agent/tools` | List registered MCP tool schemas and parameter definitions. |
| `POST` | `/api/agent/execute-tool` | Directly execute a specific structured tool with input parameters. |

### 2.5 Decision Intelligence & Optimization
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/optimizer/solve` | Execute Google OR-Tools CP-SAT constraint optimization solver. |
| `GET` | `/api/decisions/history` | Retrieve historical decisions with audit trails, SHAP values, and outcomes. |
| `POST` | `/api/decisions/approve` | Human-in-the-loop endpoint to approve, reject, or flag a recommendation. |
| `POST` | `/api/decisions/feedback`| Record operator feedback for continuous model evaluation and fine-tuning. |

### 2.6 Constellation Telemetry & Simulation
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/simulation/telemetry` | Fetch live satellite telemetry streams and orbital state vectors. |
| `POST` | `/api/simulation/scenario` | Inject operational stress scenarios (e.g. solar storm, battery brownout). |
| `WS` | `/ws/telemetry` | WebSocket stream broadcasting real-time constellation telemetry. |

### 2.7 Observability & Infrastructure Health
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Liveness and readiness probe checking Redis, PostgreSQL, and ML models. |
| `GET` | `/metrics` | Prometheus metrics scrape endpoint (latencies, counts, agent traces). |
