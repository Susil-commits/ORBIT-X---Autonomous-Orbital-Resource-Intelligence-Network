# ORBIT-X — Autonomous Orbital Resource & Intelligence Network

**ORBIT-X V2.0** is an AI-driven autonomous orbital resource and constellation scheduling platform. It coordinates a simulated Low Earth Orbit (LEO) satellite constellation, balancing dynamic observation requests, orbital access windows, physical battery dynamics, spacecraft telemetry health, intersatellite optical laser mesh routing, and collision-risk constraints.

![ORBIT-X Architecture](https://img.shields.io/badge/ORBIT--X-Autonomous%20Constellation%20V2.0-00f0ff?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Google OR-Tools](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4?style=flat)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Isolation%20Forest-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Three.js](https://img.shields.io/badge/Three.js-WebGL%203D-black?style=flat&logo=three.js&logoColor=white)
![React](https://img.shields.io/badge/React%2018-Vite%20%2B%20TypeScript-61DAFB?style=flat&logo=react&logoColor=black)

---

## 1. System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ORBIT-X V2.0 SYSTEM OVERVIEW                      │
└────────────────────────────────────────────────────────────────────────┘
                                   │
 ┌─────────────────────────────────┴─────────────────────────────────┐
 │                   PHYSICS & PROPAGATION LAYER                     │
 │  • Keplerian Orbit Propagator (ECI/ECEF, ground track, day/night)  │
 │  • Line-of-Sight Access Model (ground targets, comm stations)     │
 │  • Intersatellite Optical Laser Links (ISL) Mesh & Earth Occlusion │
 │  • Pairwise Conjunction & Collision-Risk (TCA lookahead & CAM)    │
 └─────────────────────────────────┬─────────────────────────────────┘
                                   │ Constellation Ticks
 ┌─────────────────────────────────┴─────────────────────────────────┐
 │                   INTELLIGENCE & AI SUBSYSTEMS                    │
 │  • Battery Intelligence: Physics + Lookahead Energy Forecasting   │
 │  • Spacecraft Health AI: Isolation Forest Anomaly Detection       │
 │  • Extreme Space Scenario Director: Self-Healing Reactive Engine  │
 │  • Multi-Agent Coordination: Decentralized Bidding & ISL Routing  │
 │  • Mission Optimizer: Google OR-Tools CP-SAT Constraint Solver    │
 │  • Explainability Engine: Structured Decision Reasoning & Diffs   │
 └─────────────────────────────────┬─────────────────────────────────┘
                                   │ Real-time State & Schedules
 ┌─────────────────────────────────┴─────────────────────────────────┐
 │                     BACKEND SERVICE (FastAPI)                     │
 │  • Async REST APIs for missions, ISL mesh, scenarios & benchmarks │
 │  • High-frequency WebSocket stream (10 Hz) for 3D visualization   │
 │  • Benchmark Runner: CP-SAT vs. Greedy vs. Random baseline        │
 └─────────────────────────────────┬─────────────────────────────────┘
                                   │ WebSocket / REST
 ┌─────────────────────────────────┴─────────────────────────────────┐
 │               FRONTEND DASHBOARD (React + Three.js)               │
 │  • Three.js (@react-three/fiber): 3D Globe, orbits, laser ISL mesh │
 │  • Point-and-Click 3D Earth Observation Target Dispatcher         │
 │  • Scenario Director HUD: Solar Storm, Debris Evasion, Blackout   │
 │  • Real-time Telemetry HUD, Mission Gantt & Decision Inspector    │
 └───────────────────────────────────────────────────────────────────┘
```


---

## 2. Core Mathematical & AI Subsystems

### 2.1 Orbital Mechanics & Propagation
- **Keplerian Propagation**: Solves Kepler's equation $M = E - e \sin(E)$ via Newton-Raphson to determine true anomaly $\nu$ and orbital radius $r(t)$.
- **J2 Perturbations**: Accounts for Earth oblateness ($J_2 = 1.08263 \times 10^{-3}$) secular RAAN precession $\dot{\Omega} = -\frac{3}{2} J_2 \left(\frac{R_E}{p}\right)^2 n \cos(i)$ and perigee rotation.
- **Coordinate Transformations**: Perifocal $\to$ ECI $\to$ ECEF (sidereal angle $\theta_G(t)$) $\to$ Geodetic ($lat, lon, alt$).
- **Cylindrical Eclipse Geometry**: Evaluates satellite position relative to the solar vector to compute sunlit vs. shadow passes.

### 2.2 Line-of-Sight Access & Ground Comms
- Topocentric elevation angle: $\sin(el) = \frac{\mathbf{\rho} \cdot \mathbf{u}_{up}}{\|\mathbf{\rho}\|}$.
- Computes continuous observation windows (off-nadir angle $\le 40^\circ$) and ground station downlink passes (elevation $\ge 5^\circ$ or $10^\circ$).

### 2.3 Battery Intelligence & Energy Forecasting
- Physics-based State of Charge (SoC) integration:
  $$\Delta E = \left( P_{solar} \cdot \mathbb{I}_{sunlit} - P_{idle} - P_{payload} \cdot \mathbb{I}_{imaging} - P_{tx} \cdot \mathbb{I}_{downlink} \right) \Delta t$$
- Enforces a hard $20\%$ minimum reserve floor across all planned operations.

### 2.4 Spacecraft Health AI (Isolation Forest)
- Unsupervised anomaly detection on multivariate telemetry streams:
  `[bus_voltage_v, solar_current_a, battery_temp_c, payload_temp_c, reaction_wheel_jitter_dps, rf_snr_db]`
- Classifies satellite health into `NOMINAL`, `DEGRADED`, and `CRITICAL_FAULT`.

### 2.5 Google OR-Tools CP-SAT Mission Optimizer
- **Constraint Formulation**:
  - **Single Assignment**: $\sum_{s, w} x_{m, s, w} \le 1$
  - **Non-Overlapping Tasks**: `model.AddNoOverlap(intervals_per_satellite)`
  - **Ground Station Sharing**: `model.AddNoOverlap(intervals_per_station)`
  - **Downlink Precedence**: $start(window_{dl}) \ge end(window_{img})$
  - **Battery Energy Budget**: Total operational drain $\le \text{EnergyBudget}_{safe}$
  - **Storage Buffer**: $\sum x_{m, s, w} \cdot \text{DataSize}_m \le S_{max} - S_{used}$
- **Objective**: Maximize priority-weighted mission yield, elevation resolution bonus, and downlink completion minus slew and degradation penalties.

### 2.6 Multi-Agent Cooperative Bidding & Auctions
- Satellites act as autonomous agents computing internal valuations:
  $$\text{Bid}(s, m) = w_{prio} P_m + w_{soc} \text{SoC}_s + w_{elev} \frac{el}{90} - w_{slew} \Delta \theta - \text{Penalty}_{health}$$
- Resolves contested targets and ground downlink passes with social-welfare consensus.

---

## 3. Evaluation & Benchmarking

Comparative evaluation under identical scenario seeds ($N=24$ missions, 12 satellites, 1 injected fault):

| Metric | Random Baseline | Greedy EDF Heuristic | Google OR-Tools CP-SAT |
|---|:---:|:---:|:---:|
| **Mission Success Rate** | 41.7% | 75.0% | **91.7%** |
| **High-Priority (P4/P5) Completion** | 50.0% | 77.8% | **100.0%** |
| **Avg. Deadline Slack** | +312s | +640s | **+1120s** |
| **Avg. Battery Reserve** | 64.2% | 72.8% | **81.4%** |
| **Ground Downlink Utilization** | 32.0% | 58.5% | **88.2%** |
| **Total Reward Yield** | $1,840 | $3,450 | **$4,620** |
| **Average Solve Time** | 0.8 ms | 1.4 ms | 12.5 ms |

---

## 4. Quick Start & Execution

### Prerequisites
- Python 3.11+ and `uv`
- Node.js 18+ and `npm`

### 1. Start Backend
```powershell
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- WebSocket Stream: `ws://localhost:8000/ws/constellation`

### 2. Start Frontend
```powershell
cd frontend
npm run dev
```
- Open `http://localhost:5173` in your browser.

### 3. Run Backend Test Suite
```powershell
cd backend
uv run pytest
```
