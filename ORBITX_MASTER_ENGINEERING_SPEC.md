
# ORBIT-X — MASTER ENGINEERING & REMEDIATION SPECIFICATION
## Autonomous Orbital Resource & Intelligence Network
### Target: production-grade research prototype / ~90% architecture completeness

**Repository:** https://github.com/Susil-commits/ORBIT-X---Autonomous-Orbital-Resource-Intelligence-Network

## 0. PURPOSE

This is the single implementation contract for ORBIT-X.

The current public repository already contains:
CP-SAT scheduling, orbital propagation/J2, access and collision modules,
ISL networking, battery/thermal models, anomaly detection, neural
cross-attention, SHAP, RAG, MCP, multi-agent bidding, training pipelines,
React/Three.js visualization, Redis/PostgreSQL and CI/evaluation.

The next objective is NOT feature inflation.
It is correctness, reproducibility, physical validation, scalability,
fault tolerance and measurable AI benefit.

TARGET:

Real orbital data / scenario
        ->
Physics digital twin
        ->
State estimation
        ->
Constraint model
        ->
CP-SAT authoritative optimization
        ->
Neural surrogate / pre-filter
        ->
Multi-agent coordination
        ->
Risk / safety layer
        ->
Mission action
        ->
Telemetry update
        ->
Replanning

LLM/RAG/MCP are operator/intelligence interfaces, not the authoritative
physics or safety engine.

---

# 1. FIRST ACTION: FORENSIC BASELINE

Before modifying:

1. clean clone
2. install with uv
3. start backend
4. start frontend
5. run all tests
6. run eval harness
7. run benchmark
8. run training smoke tests
9. run Docker Compose
10. verify Redis/Postgres
11. record every error

Create:
`docs/BASELINE_AUDIT.md`

Record:
versions
tests
failures
benchmark outputs
startup time
memory
CPU
model artifacts
data availability
network dependency failures.

Never alter tests just to obtain a green result.

---

# 2. TARGET ARCHITECTURE

                ORBITAL DATA / TLE / SCENARIO
                           |
                    Data validation
                           |
                    Orbit propagation
                           |
                 Constellation digital twin
                           |
       +-------------------+--------------------+
       |                   |                    |
     Access              ISL               Collision
       |                   |                    |
       +-------------------+--------------------+
                           |
                     Health / Energy
                           |
                    Mission requests
                           |
                    Constraint builder
                           |
                     CP-SAT solver
                           |
                 Authoritative schedule
                           |
               +-----------+-----------+
               |                       |
        Neural surrogate         Multi-agent bids
               |                       |
               +-----------+-----------+
                           |
                     Risk/Safety
                           |
                      Action plan
                           |
                     Digital twin
                           |
                 Telemetry/event log
                           |
                Replanning / evaluation

---

# 3. PHYSICS AUTHORITY

The physics engine must be authoritative.

Modules:
orbit propagator
access model
collision model
ISL model
battery
thermal
attitude/slew where modeled

Every parameter classified:
- physical constant
- public-data-derived
- calibrated
- engineering assumption
- synthetic

Create:
`docs/PHYSICS_ASSUMPTIONS.md`

Never claim orbital accuracy beyond validated ranges.

---

# 4. ORBIT PROPAGATION

Support:
Keplerian baseline
J2 perturbation
SGP4/TLE path where available

Tests:
- orbital period
- altitude sanity
- inclination sanity
- propagation continuity
- deterministic seed for synthetic cases

Compare against known/reference ephemeris where possible.

Record:
position error
velocity error
time horizon
propagation method

Do not silently mix coordinate frames.

Every vector must declare:
frame
epoch
units.

---

# 5. REAL TLE / CELESTRAK DATA

Build:
`data/tle/`

Pipeline:
download -> cache -> parse -> validate -> version -> propagate

Record:
satellite ID
NORAD ID
epoch
source
retrieval time
TLE checksum/version

Handle:
expired TLE
malformed TLE
network failure
duplicate satellite
stale data

Fallback:
cached TLE -> synthetic constellation

Never silently use stale orbital data.

---

# 6. STATE ESTIMATION

Create a canonical:
ConstellationState

Contains:
satellite state
orbit
position/velocity
battery
thermal
health
communication
ISL
collision alerts
active missions
ground stations

Every state:
timestamp
epoch
schema_version
source

Use immutable snapshots for replay.

---

# 7. MISSION REQUEST MODEL

Mission:
mission_id
target
priority
deadline
duration
required_elevation
quality requirement
data volume
energy cost
ground-station requirement
risk tolerance

Validate impossible requests before scheduling.

---

# 8. ACCESS / VISIBILITY

Access model must calculate:
line of sight
elevation
visibility window
target geometry
ground-station contact

Test edge cases:
horizon
minimum elevation
polar crossing
dateline
short visibility windows
multiple simultaneous accesses.

Never schedule an observation outside a valid access interval.

---

# 9. COLLISION / CONJUNCTION

Current pairwise TCA/CAM capability must be expanded into a robust safety subsystem.

Inputs:
relative state
TCA
miss distance
uncertainty
threshold

Outputs:
collision_probability or risk proxy
TCA
miss_distance
required_action
confidence

Scenarios:
close approach
multiple conjunctions
bad telemetry
satellite loss
maneuver unavailable

Safety rule:
mission scheduling can NEVER override a hard collision constraint.

If uncertainty modeling is not statistically validated, label output
"risk proxy" rather than "collision probability."

---

# 10. ISL NETWORK

Model:
satellite-to-satellite links
line-of-sight
range
occlusion
capacity
latency
availability
routing

Validate:
link appears/disappears correctly
routing avoids unavailable nodes
capacity is respected
ground downlink contention is handled.

Add network stress tests:
satellite failure
link failure
ground station outage
high traffic.

---

# 11. BATTERY MODEL

State:
SoC
charge rate
discharge rate
solar input
payload consumption
communications consumption
thermal derating

Validate:
0 <= SoC <= 100
no impossible energy creation
sunlight/eclipse transitions
charge/discharge boundaries.

Compare analytical model with simulation traces.

---

# 12. THERMAL / PHYSICS-INFORMED MODEL

Current Stefan-Boltzmann/ODE subsystem should be validated rather than
treated as a decorative PINN.

Define:
heat sources
radiative loss
thermal capacity
temperature boundaries

If using PINN:
loss =
data_loss + lambda_physics * physics_residual

Report:
data MAE
physics residual
generalization
stability under extrapolation.

Compare:
analytical ODE
neural model
hybrid model.

---

# 13. HEALTH AI

Isolation Forest baseline:
- battery telemetry
- temperature
- voltage
- power
- communication health

Generate labeled synthetic faults:
thermal drift
battery degradation
voltage anomaly
sensor drift
communication degradation

Metrics:
precision
recall
F1
false alarm rate
detection latency

Never report accuracy alone on imbalanced anomaly data.

---

# 14. MISSION OPTIMIZATION

CP-SAT is the authoritative optimizer.

Objective should explicitly define:
mission priority
deadline
quality
energy reserve
ground contact
slew cost
collision risk
network cost

Hard constraints:
access
deadline
resource overlap
battery floor
thermal limit
collision
ground station capacity

Soft constraints:
quality
energy margin
revenue
fairness

Document objective weights.

Perform sensitivity analysis.

---

# 15. NEURAL SURROGATE

The neural model is NOT the authoritative scheduler.

Use:
CP-SAT -> labels / optimal decisions
        ->
training dataset
        ->
cross-attention / bid model
        ->
fast candidate valuation

Evaluate on held-out scenarios:
top-1 agreement
objective regret
constraint violations
objective gap
latency
memory

A high agreement score alone is insufficient.

Required result:
neural action must remain constraint-safe.

If neural output violates constraints:
CP-SAT or constraint projection must reject it.

---

# 16. DATASET GENERATION

Generate diverse scenarios:

number of satellites
number of missions
priority distributions
deadlines
battery levels
weather/thermal states
ground-station availability
ISL topology
collision alerts
failures

Dataset split:
scenario-level split, never row-level leakage.

Manifest:
scenario_version
seed
parameter ranges
solver version
dataset hash
row count
feature schema.

Store CP-SAT objective and constraint status with each sample.

---

# 17. TRAINING PIPELINE

Required:
dataset generation
validation
training
checkpoint
evaluation
export

Track:
dataset version
seed
hyperparameters
loss
validation
test
objective regret
constraint violation rate

Use MLflow or lightweight metadata if useful.

---

# 18. MULTI-AGENT AUCTION

Current bidding/Vickrey auction should be made explicit.

Agent:
satellite_id
local state
mission value
energy cost
risk
communication value

Bid:
mission_id
valuation
confidence
constraints

Auction must guarantee:
invalid bids rejected
no duplicate assignment
resource constraints preserved.

Compare:
central CP-SAT
greedy
auction
hybrid.

Metrics:
mission success
fairness
revenue/objective
latency
communication overhead.

---

# 19. RISK ENGINE

Risk:
collision
battery
thermal
communication
mission deadline
health
maneuver

Create:
RiskState

Risk-adjusted objective:
mission_value - risk_penalty

Do not let risk weights remain undocumented.

---

# 20. RESILIENCE / EXTREME SCENARIOS

Required scenarios:

SOLAR_STORM
DEBRIS_CONJUNCTION
GROUND_BLACKOUT
DISASTER_SURGE
SATELLITE_FAILURE
ISL_FAILURE
BATTERY_DEGRADATION
THERMAL_OVERLOAD
STALE_TLE
GPS/telemetry degradation

For every scenario:
detect
estimate
replan
validate constraints
execute fallback
measure recovery time.

---

# 21. SELF-HEALING / FALLBACK

Allowed:
restart worker
fallback to cached TLE
fallback neural -> CP-SAT
fallback LLM -> deterministic status
fallback Redis -> local cache where safe
rollback model checkpoint

Not allowed:
automatic source-code rewriting
silent physics modification
silent model replacement

Every fallback produces an event.

---

# 22. REPLANNING LOOP

ORBIT-X must support event-driven replanning.

Events:
new mission
mission cancellation
satellite failure
battery threshold
thermal threshold
collision alert
ground station outage
ISL loss
new TLE

Pipeline:
event -> state snapshot -> constraint rebuild -> optimize -> validate -> publish.

Prevent race conditions with versioned state:
state_version
plan_version

Reject stale plans.

---

# 23. 3D DIGITAL TWIN

Three.js frontend visualizes but does not own physics.

Render:
Earth
satellites
orbits
ground stations
visibility cones
ISL links
collision alerts
mission paths

Use backend authoritative timestamps.

Do not let visual interpolation alter simulation truth.

---

# 24. RAG / LLM / MCP

RAG:
historical missions
decision logs
operator manuals
scenario reports

Every answer needs source citations.

LLM:
commentary
operator explanation
natural-language query

MCP:
get_constellation_status
explain_assignment
ask_history
preview_bid
trigger_scenario

MCP must validate all inputs and enforce authorization for scenario injection.

Do not expose private chain-of-thought.
Return structured evidence and concise rationale.

---

# 25. API

Version:
`/api/v1/...`

Required:
constellation
missions
schedule
telemetry
health
collision
isl
benchmarks
training
scenarios
explainability
models

Pydantic schemas.
Request IDs.
Structured errors.
Rate limits on compute-heavy endpoints.

---

# 26. DATABASE / CACHE

PostgreSQL:
historical telemetry
missions
plans
experiments
models
events

Redis:
live state
pub/sub
short-lived job status

Never use Redis as permanent truth.

---

# 27. ERROR HANDLING

Categories:
PHYSICS_ERROR
TLE_ERROR
MISSION_ERROR
OPTIMIZATION_ERROR
MODEL_ERROR
SAFETY_ERROR
NETWORK_ERROR
DB_ERROR
CACHE_ERROR
LLM_ERROR
UI_ERROR

Fallback matrix:

TLE live -> cached TLE -> synthetic
neural -> CP-SAT
CP-SAT unavailable -> safe greedy fallback
Redis -> local cache
LLM -> deterministic response
Postgres unavailable -> controlled degraded mode

Never execute an unvalidated schedule.

---

# 28. SECURITY

Protect:
scenario injection
mission creation
model upload
training endpoints
MCP tools

Never commit secrets.

Validate file paths and model files.

Verify model SHA-256.

---

# 29. PERFORMANCE / SCALING

Benchmark:
12 satellites
50
100
500
1000

Metrics:
solver latency
neural latency
simulation step latency
memory
CPU
WebSocket latency
replanning latency
mission throughput

Use asynchronous/background CP-SAT solving.

Never block the FastAPI event loop with long optimization.

---

# 30. TESTING

Unit:
orbit
access
collision
ISL
battery
thermal
health
optimizer
auction
RAG
MCP schemas

Integration:
mission -> optimizer
optimizer -> digital twin
telemetry -> health
collision -> replanning
TLE -> propagation

Property:
SoC bounds
thermal bounds
no invalid orbit
no mission outside access
no schedule collision
no duplicate assignment
no hard safety constraint violation

E2E:
normal mission
high contention
failure
collision
ground outage
solar storm.

---

# 31. BENCHMARKS

Required baselines:
Random
Greedy EDF
CP-SAT
Auction
Neural surrogate
Hybrid

Metrics:
mission success
high-priority success
deadline slack
SoC retained
downlink utilization
objective value
constraint violations
solver latency
neural regret
recovery time

Run multiple seeds and report mean/std/confidence intervals.

Do not rely on one hand-picked scenario.

---

# 32. ABLATION

Run:
full system
-no health AI
-no thermal model
-no ISL
-no collision constraints
-no neural prefilter
-no auction
-no risk
-no RAG

Use identical scenario seeds.

Prove contribution of each subsystem.

---

# 33. MODEL VALIDATION

For neural surrogate:
MAE/RMSE where regression
classification F1 where classification
calibration
objective regret
constraint violations
latency

For anomaly detection:
precision/recall/F1
false alarm rate
time-to-detect

For PINN:
data error
physics residual
stability

For RAG:
retrieval recall@k
citation precision
answer grounding

---

# 34. MLOPS

Model registry:
model
version
dataset
features
seed
hyperparameters
metrics
checksum
promotion state

Promotion:
candidate -> validation -> production

Rollback on:
constraint violation
performance regression
drift
checksum mismatch.

---

# 35. FRONTEND

Views:
3D constellation
mission queue
schedule Gantt
collision
health
ISL
AI lab
benchmark
scenario director
explainability
RAG
multi-agent auction
system health

Frontend is visualization/control only.
Backend owns truth.

---

# 36. CI/CD

Gates:
lint
type check
tests
physics regression
benchmark smoke
model checksum
frontend build
Docker build
security scan

Any hard safety regression blocks merge.

---

# 37. P0/P1/P2 BUG TRIAGE

P0:
collision safety failure
invalid schedule
physics corruption
security breach
data corruption
production startup failure

P1:
wrong mission assignment
battery constraint violation
model constraint violation
replanning race
benchmark regression
API contract break

P2:
UI
performance
optional RAG/LLM
visual defects

Every fix:
reproduction -> root cause -> patch -> test -> regression result.

---

# 38. REQUIRED ACCEPTANCE GATES FOR ~90%

A:
clean clone runs

B:
all tests pass

C:
physics validation report generated

D:
real/cached TLE pipeline works

E:
CP-SAT benchmark reproducible

F:
neural surrogate evaluated on held-out scenarios

G:
zero hard safety violations in test suite

H:
failure scenarios recover correctly

I:
scales across constellation sizes

J:
one command regenerates benchmark report

K:
Docker deployment works

L:
frontend/backend integration works

---

# 39. IMPLEMENTATION ORDER

Phase 0:
baseline forensic audit

Phase 1:
state schemas + physics validation + data/TLE pipeline

Phase 2:
mission/access/collision/ISL correctness

Phase 3:
CP-SAT objective + constraints + benchmark

Phase 4:
health + thermal + battery validation

Phase 5:
dataset generation + neural surrogate

Phase 6:
multi-agent auction + risk

Phase 7:
event-driven replanning + resilience

Phase 8:
3D frontend + MCP/RAG hardening

Phase 9:
scale tests + ablation + MLOps + CI

Do not rewrite the entire project.

---

# 40. DEFINITION OF DONE

Every subsystem must satisfy:

[ ] implementation
[ ] runtime integration
[ ] schema
[ ] tests
[ ] benchmark
[ ] error handling
[ ] fallback
[ ] documentation
[ ] reproducible command

Report:
implemented / partial / blocked / deferred.

---

# 41. FINAL PROJECT CLAIM

After completion:

"ORBIT-X is an autonomous orbital resource-allocation research platform
combining orbital digital-twin simulation, constraint optimization,
physics-informed modeling, anomaly detection, neural scheduling
surrogates, multi-agent coordination, risk-aware replanning,
explainability and operator-facing AI tooling."

Do not claim flight-certified, operational spacecraft software or
collision probability accuracy beyond the validation actually performed.

