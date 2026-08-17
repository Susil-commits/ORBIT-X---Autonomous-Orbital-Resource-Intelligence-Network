# ORBIT-X Autonomous Constellation Network — Real Data, Neural Network, TreeSHAP, RAG & Atlan Cohort Extensions

## 1. Overview & Architecture Summary

ORBIT-X is an autonomous orbital resource intelligence and satellite constellation operations digital twin. This release replaces synthetic Keplerian elements with real TLE orbital mechanics, incorporates a PyTorch neural bid-valuation model, distilled TreeSHAP feature attributions, a grounded operational decision RAG engine, tactical Flight Director commentary with fact-consistency verification, an official Model Context Protocol (MCP) server, an automated CI evaluation harness, and a self-healing continuous verification loop.

---

## 2. Key Components Built & Verified

### A1. Real Celestrak TLE Data & Physical Verification
- **Live Celestrak Ingestion (`app/data/fetch_real_constellation.py`)**:
  - Pulls live Two-Line Element (TLE) sets for Starlink and Planet Labs constellations via Celestrak GP API using standard user-agent authentication.
  - Extracts Keplerian orbital elements: inclination $i$, RAAN $\Omega$, eccentricity $e$, argument of perigee $\omega$, mean anomaly $M_0$, and semi-major axis $a = (\mu / n^2)^{1/3}$ with WGS-84 gravitational parameter $\mu = 398600.4418 \text{ km}^3/\text{s}^2$.
  - Saved 12 real Starlink satellites to `backend/data/real_constellation.json` tagged with `data_source: "celestrak_real"`.
- **ISS Physical Ground-Truth Verification**:
  - Validated International Space Station (NORAD 25544, ZARYA) live TLE with calculated orbital period of **92.935 min** (deviation of only 0.255 min from standard 92.68 min at ~413 km altitude, achieving **99.7% physical parity**).

### A2. Neural Network Bid Valuation (`app/intelligence/bid_value_network.py`)
- **PyTorch MLP Architecture (`BidValueMLP`)**:
  - Input dimension: 10 normalized features (priority, battery SoC, elevation, slew penalty, health status, storage, sunlit flag, deadline slack, energy cost, duration).
  - Layers: $10 \to 64 \to 64 \to 32 \to 1$ with LayerNorm, ReLU activations, and positive clamp output.
- **CP-SAT Supervised Training & Honest Evaluation**:
  - Generated training dataset with Google OR-Tools CP-SAT optimizer across 50 multi-agent auction scenarios (`collect_cpsat_labels.py`).
  - Trained `BidValueMLP` (`train_bid_network.py`) and saved checkpoint to `backend/models/bid_network.pt`.
  - **Holdout Test Set Results**:
    - **MAE**: `16.62` / `20.10`
    - **Top-1 Agreement Rate with CP-SAT**: `66.7%` – `100.0%`
    - **Inference Latency**: `< 0.2 ms` (sub-millisecond preview).

### A3. Explainability — Distilled TreeSHAP & Model Drift (`app/intelligence/shap_explainer.py`)
- **Distilled Surrogate Explainer**:
  - Fits an `XGBRegressor` surrogate model on neural network predictions with `is_distilled: true`.
  - Uses `shap.TreeExplainer` for exact local feature attribution without kernel SHAP sampling approximations.
- **Model Checkpoint Drift Detection**:
  - Computes SHA-256 hash of active `bid_network.pt` weights and compares against the surrogate's trained hash to detect checkpoint drift.

### A4. Grounded Decision History RAG (`app/intelligence/mission_qa.py`)
- **Operational Event Logging (`DecisionLogger`)**:
  - Ring buffer capturing structured decision records (`[Record LOG-xxxx]`) with solver assignments, counterfactual rejections, CAM maneuvers, and telemetry anomalies.
- **Grounded Vector Retrieval & Citations**:
  - Embedded using `sentence-transformers` (`all-MiniLM-L6-v2`).
  - Calibrated cosine similarity threshold ($0.25$) ensures exact source citations on in-domain queries and **honest refusal** on unsupported questions.

### A5. Flight Director Commentary & Fact-Consistency Verifier (`app/intelligence/commentary_generator.py`)
- **Ollama Integration & Timeout Fallback**:
  - Queries local LLM with 1.5s sub-second timeout and falls back to deterministic factual templates.
- **Hallucination Prevention**:
  - `FactConsistencyVerifier` validates satellite IDs and mission names against the source event to prevent false status claims.

### B1. Model Context Protocol (MCP) Server (`app/mcp_server/server.py`)
- Standard MCP server exposing 5 tools for Claude Desktop, Claude Code, and Antigravity:
  1. `get_constellation_status`: Live telemetry, health status, and active missions.
  2. `explain_mission_assignment`: Solver rationale and rejected candidates for a specific mission.
  3. `ask_mission_history`: Grounded RAG queries with source citations.
  4. `preview_satellite_bid`: Sub-millisecond neural valuation with TreeSHAP feature breakdown.
  5. `trigger_scenario`: Extreme space scenario injection.

### B2. Automated Evaluation & Regression Scoring Harness (`backend/eval/run_eval.py`)
- Compares live model and scheduler performance against `baseline_scores.json`:
  - CP-SAT Completion Rate & Reward Yield
  - Neural Network Top-1 Agreement Rate & MAE
  - TreeSHAP surrogate drift status
  - Keplerian orbital period physical validity
- Exits with code 0 on PASS and code 1 if any regression is detected.

### B3. Self-Healing Continuous Verification Agent Loop (`app/intelligence/agent_loop.py`)
- Inspects surrogate weight alignment and eval regression gates.
- Automatically re-distills the TreeSHAP surrogate when weight hash drift is detected, logs recovery actions into `DecisionLogger`, and emits plain-language commentary.

### A6. Modern Stack & Infrastructure
- **Async Redis (`app/core/redis_client.py`)**: Async client (`redis.asyncio`) with offline fallback.
- **Async SQLAlchemy Database (`app/core/database.py`)**: PostgreSQL / SQLite asynchronous switch with `DecisionLogRecord` and `EvalRunRecord`.
- **Docker Compose (`docker-compose.yml`)**: Multi-container stack (Postgres 16, Redis 7, Backend, Frontend).
- **GitHub Actions CI (`.github/workflows/ci.yml`)**: Automated Pytest, AI Eval harness regression gates, and Vite production build.

---

## 3. Frontend UI Upgrades

1. **Constellation Data Source Toggle (`Header.tsx`)**:
   - One-click toggle between `SYNTHETIC WALKER-DELTA` and `CELESTRAK LIVE TLE (STARLINK)`.
   - ISS Ground-Truth Physical Verification modal showing NORAD 25544 orbital period (92.9 min).
2. **Flight Director Live Commentary Ticker (`FlightDirectorCommentaryBar.tsx`)**:
   - Real-time tactical commentary with `[FACT-CHECKED]` and model provenance indicators.
3. **Mission AI Copilot & Decision RAG Drawer (`MissionRAGDrawer.tsx`)**:
   - Interactive Q&A with quick suggestion chips, confidence gauges, citation cards (`[Record LOG-xxxx]`), and honest refusal badges.
4. **Interactive TreeSHAP Inspector (`ExplainabilityModal.tsx`)**:
   - Neural Bid preview with CP-SAT agreement probability.
   - Distilled TreeSHAP feature attribution bar chart with positive (green) and negative (amber) contributions.

---

## 4. Verification & Test Results

### Backend Automated Test Suite (Pytest)
```
============================= test session starts =============================
platform win32 -- Python 3.12.13, pytest-9.1.1
collected 31 items

backend\tests\test_benchmark.py::test_benchmark_suite_execution PASSED   [  3%]
backend\tests\test_celestrak_data.py::test_parse_iss_tle_ground_truth PASSED [  6%]
backend\tests\test_celestrak_data.py::test_malformed_tle_fails_loudly PASSED [  9%]
backend\tests\test_celestrak_data.py::test_real_constellation_loading PASSED [ 12%]
backend\tests\test_commentary_and_hallucination.py::test_fact_consistency_verifier PASSED [ 16%]
backend\tests\test_commentary_and_hallucination.py::test_deterministic_template_fallback PASSED [ 19%]
backend\tests\test_eval_harness.py::test_eval_harness_execution PASSED   [ 22%]
backend\tests\test_eval_harness.py::test_orbital_physics_within_nominal_envelope PASSED [ 25%]
backend\tests\test_health_ai.py::test_nominal_telemetry PASSED           [ 29%]
backend\tests\test_health_ai.py::test_severe_fault_telemetry PASSED      [ 32%]
backend\tests\test_isl_network.py::test_line_of_sight_occlusion PASSED   [ 35%]
backend\tests\test_isl_network.py::test_build_isl_mesh PASSED            [ 38%]
backend\tests\test_mcp_server.py::test_mcp_get_constellation_status PASSED [ 41%]
backend\tests\test_mcp_server.py::test_mcp_preview_satellite_bid PASSED  [ 45%]
backend\tests\test_mcp_server.py::test_mcp_ask_mission_history PASSED    [ 48%]
backend\tests\test_mcp_server.py::test_mcp_trigger_scenario PASSED       [ 51%]
backend\tests\test_mission_rag.py::test_rag_grounded_answer PASSED       [ 54%]
backend\tests\test_mission_rag.py::test_rag_honest_refusal PASSED        [ 58%]
backend\tests\test_neural_bid_network.py::test_feature_extraction PASSED [ 61%]
backend\tests\test_neural_bid_network.py::test_neural_network_forward_and_latency PASSED [ 64%]
backend\tests\test_neural_bid_network.py::test_predictor_loaded_and_hash PASSED [ 67%]
backend\tests\test_optimizer.py::test_cpsat_optimizer_scheduling PASSED  [ 70%]
backend\tests\test_optimizer.py::test_multi_agent_auction PASSED         [ 74%]
backend\tests\test_orbit_propagator.py::test_kepler_solver PASSED        [ 77%]
backend\tests\test_orbit_propagator.py::test_orbit_propagation_circular PASSED [ 80%]
backend\tests\test_orbit_propagator.py::test_constellation_generation PASSED [ 83%]
backend\tests\test_scenarios.py::test_scenario_director_lifecycle PASSED [ 87%]
backend\tests\test_scenarios.py::test_custom_target_dispatch PASSED      [ 90%]
backend\tests\test_shap_distillation.py::test_shap_explainer_ready_and_distilled PASSED [ 93%]
backend\tests\test_shap_distillation.py::test_shap_local_attributions PASSED [ 96%]
backend\tests\test_shap_distillation.py::test_drift_detection PASSED     [100%]

============================= 31 passed in 38.87s =============================
```

### AI Evaluation & Policy Regression Harness (`run_eval.py`)
```
=================================================================
      ORBIT-X AUTOMATED EVALUATION & REGRESSION HARNESS       
=================================================================

[1/4] Running CP-SAT Constellation Scheduler Benchmark...
  -> Completion Rate: 16.7% (PASS) | Reward Yield: 1277.5 (PASS)

[2/4] Evaluating Neural Network (BidValueMLP) against CP-SAT...
  -> Top-1 Agreement: 100.0% (PASS) | Test MAE: 16.62 (PASS)

[3/4] Checking TreeSHAP Surrogate Model Alignment & Drift...
  -> Drift Status: PASS (Drift Detected: False)

[4/4] Verifying Keplerian Orbital Period Physics...
  -> Measured Orbital Period: 95.65 min (PASS)

=================================================================
EVALUATION HARNESS RESULT: PASS
ALL 6 BENCHMARK & POLICY GATES PASSED CLEANLY.
Report saved to: latest_eval_report.json
=================================================================
```

### Frontend Production Build
```
> tsc -b && vite build
✓ built in 3.08s
dist/assets/index-DbGYVHhb.js   1,226.93 kB │ gzip: 332.93 kB
```
