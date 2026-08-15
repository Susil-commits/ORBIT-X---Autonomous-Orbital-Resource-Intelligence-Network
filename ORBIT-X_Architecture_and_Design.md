# ORBIT-X — Autonomous Orbital Resource & Intelligence Network

**An AI system that coordinates a simulated satellite constellation, balancing mission requests, orbital access windows, battery, spacecraft health, and collision-risk constraints.**

*Educational simulation — not operational flight-control software.*

---

## 1. Overview

ORBIT-X answers: **which satellite should do which mission, when, and what should it transmit first — given limited battery, limited ground-station windows, and changing priorities?**

Same decision-intelligence loop as APEX and RESQ-X, applied to a resource-scheduling-under-constraints domain. Where APEX was RL-heavy and RESQ-X was optimization-heavy, ORBIT-X is **scheduling-and-multi-agent-heavy** — a third distinct skill set, which is exactly why it's built last: you're layering in the one remaining piece of range (constrained scheduling + cooperative multi-agent behavior) after the other two architectural patterns are already second nature to you.

```
Mission Requests + Orbital State → Predict Access/Health → Schedule/Optimize → Simulate Alternatives → Decide → Execute → Update State → Learn
```

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  ORBITAL SIMULATOR                                   │
│   Simplified orbit propagation, ground-track, day/night,             │
│   deterministic, seeded time-stepped physics                         │
└───────────────────────────────┬───────────────────────────────────┘
                                 │ state ticks
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  CONSTELLATION DIGITAL TWIN                          │
│   Per-satellite: position, velocity, battery, thermal, health,       │
│   payload status, comm windows, storage                              │
│   PostgreSQL (state/history) + Redis (hot state)                     │
└───────────────────────────────┬───────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
     ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
     │ Orbital Access  │ │ Battery         │ │ Spacecraft      │
     │ Model           │ │ Intelligence    │ │ Health AI        │
     │ (visibility,    │ │ (energy         │ │ (anomaly         │
     │ comm windows)   │ │ forecasting)    │ │ detection)       │
     └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
              └──────────────────┼──────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   MISSION OPTIMIZER         │
                    │  OR-Tools: constraint-      │
                    │  based scheduling (CP-SAT)  │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  MULTI-AGENT COORDINATION  │
                    │  Satellites negotiate/      │
                    │  cooperate on shared tasks   │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  COLLISION-RISK CHECK      │
                    │  Simplified TCA estimate    │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   EXPLAINABILITY LAYER     │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  FastAPI + WebSocket        │
                    └────────────┬────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │  React + Three.js Dashboard │
                    │  3D globe, orbits, schedule   │
                    └─────────────────────────┘
```

---

## 3. Core Modules (Detailed)

### 3.1 Orbital Simulator (Ground Truth Engine)
Propagates satellite positions over time and generates mission requests, battery drain, and occasional anomalies/failures.

- Use a **simplified circular/Keplerian orbit model** — position as a function of time, orbital period, inclination. You do not need real TLE (Two-Line Element) propagation accuracy for this to be legitimate; state clearly in your write-up that this is simplified physics, not flight-grade propagation.
- Optionally, once the simplified version works end-to-end, swap in **Skyfield** or **sgp4** for real TLE-based propagation as a stretch goal — this is the single easiest way to make this project look meaningfully more advanced later without rearchitecting anything.
- Deterministic, seeded — same reasoning as the other two projects.
- Emits `ConstellationState` (Pydantic) every tick: per-satellite position, battery, health, active mission.

### 3.2 Constellation Digital Twin
Live mirror of every satellite's state, queryable by scheduler and dashboard.

- Redis for hot current-tick state (positions, battery levels, active tasks).
- Postgres for historical event log — mission history, anomaly log, schedule decisions.
- No spatial DB needed here (unlike RESQ-X) — orbital mechanics is just numerical propagation, not geospatial querying.

### 3.3 Orbital Access Model
Determines, for each satellite, which ground targets are currently visible and when the next ground-station communication window opens.

- Simplified geometry: compute whether a target/ground-station is within the satellite's field-of-view cone given its current position — this is straightforward trigonometry, not aerospace-grade line-of-sight modeling.
- Output: `visible_targets`, `next_comm_window_start`, `comm_window_duration`.

### 3.4 Battery Intelligence
Predicts energy consumption forward in time and protects future mission availability — the core "resource conservation under uncertainty" model.

- A regression model (or even a physically-derived formula: solar charge during daylight passes minus payload/transmission draw) predicting battery level N steps ahead.
- This feeds directly into the scheduler as a hard constraint (don't assign a mission that would drain a satellite below a safety threshold).

### 3.5 Spacecraft Health AI
Detects anomalies in simulated telemetry (temperature, voltage, attitude error).

- Inject synthetic anomalies into your simulator (sudden voltage drop, thermal spike) and train a simple anomaly detector — Isolation Forest or a basic autoencoder reconstruction-error approach both work well and are genuinely appropriate tools for this problem, not overkill.
- Output feeds into the scheduler: unhealthy satellites get deprioritized or excluded from new mission assignment.

### 3.6 Mission Optimizer (the core of this project)
Assigns imaging/observation requests to satellites, respecting battery, visibility, health, deadline, and priority constraints.

- This is a **constraint scheduling problem** — use **OR-Tools CP-SAT solver**, which is built exactly for this (assign tasks to resources under a web of constraints, maximize priority-weighted completion).
- This is your strongest "advanced" signal in this project, same role the OR-Tools optimizer played in RESQ-X, but a different solver pattern (constraint programming vs. assignment/routing) — worth explicitly knowing the difference for interviews.

### 3.7 Multi-Agent Coordination
When multiple satellites can serve the same mission, or when a downlink window is shared/contested, satellites need to cooperate rather than greedily compete.

- Keep this genuinely lightweight: a simple auction/bidding mechanism (each satellite "bids" based on cost — remaining battery, visibility duration, priority match) resolved centrally by the optimizer. This demonstrates the multi-agent concept honestly without requiring decentralized multi-agent RL training, which was correctly cut from scope.

### 3.8 Collision-Risk Model (simplified)
Estimates time-to-closest-approach between simulated objects and flags elevated risk.

- Simple geometric closest-approach calculation between two propagated trajectories over a look-ahead window — not a full conjunction-assessment system. Frame this explicitly as "simplified, educational" in your write-up, exactly as the original spec intends.

### 3.9 Autonomous Recovery
When a satellite fails or a ground station goes down, reassign its in-progress/queued missions.

- This isn't a separate model — it's a re-trigger of the Mission Optimizer with updated constraints (one fewer available satellite). Cheap to implement once the optimizer exists, and a good scenario to demo live.

### 3.10 Explainability Layer
For every scheduling decision: which satellite, which mission, why this one over alternatives (visibility window, battery margin, priority, health status).

- Same structured `DecisionExplanation` pattern as the other two projects — by this third project, explicitly point out in your README/portfolio that this is a **reusable architectural pattern** you've applied three times. That's a stronger signal than three unrelated projects.

---

## 4. Modern Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Simulation & data | Python 3.12, NumPy, Pandas | Core numerical work |
| Orbital mechanics | Simplified Keplerian model → optional Skyfield/sgp4 upgrade | Legitimate without requiring aerospace background |
| Scheduling/optimization | Google OR-Tools **CP-SAT** | Constraint programming — different solver class from RESQ-X's assignment/routing |
| Anomaly detection | scikit-learn (Isolation Forest) or small PyTorch autoencoder | Appropriate-scale ML for health monitoring |
| Experiment tracking | MLflow | Track scheduler variants, anomaly detector performance |
| Backend API | FastAPI (async) + Pydantic v2 | Consistent with the other two projects |
| Real-time updates | WebSockets | Live constellation feed |
| Hot state | Redis | Current-tick satellite state |
| Persistent store | PostgreSQL + SQLAlchemy 2.0 (async) + Alembic | Event log, mission history |
| Dependency mgmt | `uv` | Fast, modern |
| Frontend | React 18 + Vite + TypeScript | Consistent with the other two |
| 3D visualization | Three.js (via `@react-three/fiber`) | 3D globe + orbit paths — the visually strongest dashboard of the three projects |
| Charts | Recharts | Battery levels, mission success rate over time |
| State mgmt | Zustand / TanStack Query | Consistent |
| Containerization | Docker + docker-compose | One-command spin-up |
| CI | GitHub Actions | Lint + test |
| Testing | Pytest, Vitest | Standard |

---

## 5. Data Flow (Single Decision Cycle)

1. Simulator advances one tick → satellites move, battery drains/charges, new mission requests arrive, occasional anomaly injected.
2. Digital Twin writes state to Redis, appends event to Postgres log.
3. Orbital Access Model computes current visibility + upcoming comm windows per satellite.
4. Battery Intelligence forecasts near-future energy availability per satellite.
5. Spacecraft Health AI flags any anomalous satellites.
6. Mission Optimizer (CP-SAT) computes the mission-to-satellite assignment respecting all constraints.
7. Multi-Agent Coordination resolves any contested missions/downlink windows via the bidding mechanism.
8. Collision-Risk Model checks the resulting trajectories for elevated risk.
9. Explainability Layer logs the reasoning trail.
10. Schedule broadcast over WebSocket to dashboard, persisted to Postgres.
11. Simulator executes assigned actions, advances state, loop repeats.

---

## 6. Database Design (Core Tables)

- `constellations` — constellation_id, config (num_satellites, orbit params, seed), created_at
- `satellite_ticks` — constellation_id, satellite_id, tick_number, state snapshot (JSONB: position, battery, health, active_mission)
- `missions` — constellation_id, mission_id, priority, deadline, target_location, status
- `schedule_decisions` — constellation_id, tick, satellite_id, mission_id, reasoning (JSONB)
- `anomaly_log` — constellation_id, satellite_id, tick, anomaly_type, detected_by
- `benchmark_results` — constellation_id, policy_name (cp_sat/greedy/random), mission_success_rate, avg_deadline_slack, energy_efficiency

---

## 7. Evaluation & Benchmarking (Your Strongest Interview Material)

Run identical mission-request scenarios (same seed) through three schedulers:

1. **Random assignment** — sanity floor.
2. **Greedy heuristic** — assign each mission to the first available/nearest-deadline satellite, no global optimization.
3. **CP-SAT optimizer** — your actual system.

Report: mission success rate, deadline satisfaction rate, energy efficiency (average battery margin maintained), communication window utilization. Same principle as the other two projects — this table is what proves the constraint solver earns its complexity.

---

## 8. Development Roadmap

1. Simplified orbital simulator (Keplerian propagation)
2. Constellation Digital Twin (Redis + Postgres wiring)
3. Orbital Access Model (visibility + comm windows)
4. Mission request generator + greedy baseline scheduler (get end-to-end working first)
5. Battery Intelligence forecasting model
6. Spacecraft Health AI (anomaly detection)
7. CP-SAT Mission Optimizer
8. Collision-risk check (simplified)
9. Multi-agent bidding/coordination mechanism
10. Autonomous recovery (re-trigger optimizer on failure)
11. Explainability layer
12. FastAPI + WebSocket backend
13. React + Three.js 3D dashboard (globe, orbits, schedule view, reasoning panel)
14. Benchmark suite (CP-SAT vs greedy vs random) + write-up
15. *(Stretch)* Swap in Skyfield/sgp4 for real TLE-based propagation

---

## 9. What Makes This "Advanced" Without Overreaching

- CP-SAT constraint scheduling — a third distinct optimization paradigm across your three projects (RL in APEX, assignment/routing in RESQ-X, constraint programming here), which is a genuinely strong "range" signal.
- Three.js 3D visualization — the most visually impressive dashboard of the three, good for a portfolio landing page/demo video.
- Multi-agent bidding mechanism — demonstrates the concept of cooperative agents without the training cost/fragility of true multi-agent RL.
- Same reusable digital-twin → predict → optimize → counterfactual → explain architecture as the other two — say this explicitly in your portfolio write-up.
- Clear, honest stretch path (Skyfield/sgp4) if you want to push further after the core system works.

---

## 10. Explicitly Out of Scope (and why)

- Real TLE data / live satellite tracking APIs as a baseline requirement — kept as an optional stretch goal instead, so the core simulator stays deterministic and controllable.
- Full conjunction-assessment collision modeling — replaced with a simplified closest-approach estimate, explicitly framed as educational.
- Decentralized multi-agent reinforcement learning — replaced with a lightweight centralized bidding mechanism that demonstrates the same "agents cooperating" concept without the training complexity and instability multi-agent RL is known for.
- Solar-weather event modeling as a separate ML system — implement as a scripted scenario (temporary battery-drain multiplier) rather than a modeled physical system; it's a good demo scenario, not a module worth its own model.
