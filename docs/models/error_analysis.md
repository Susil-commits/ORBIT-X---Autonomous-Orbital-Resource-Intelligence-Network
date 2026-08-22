# ML Error Analysis: Diagnostic & Boundary Case Evaluation

## 1. Overview
This document provides a rigorous error analysis of the machine learning and deep learning models deployed within ORBIT-X. Rather than presenting aggregate accuracy numbers in isolation, this analysis isolates specific operational failure modes, error distributions, and systemic edge cases.

---

## 2. Categorization of Error Modes

```
                       ERROR TAXONOMY & FAILURE MODES
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
  RESOURCE BOUNDARY           CONTENTION & LOAD          DATA DEGRADATION
  - Eclipse transitions       - Conflicting priorities   - Telemetry staleness
  - Deep discharge (<20%)     - Multi-target overlaps    - Missing look-angles
  - Thermal throttles         - Burst request floods     - Sensor drift / noise
```

---

## 3. Detailed Error Mode Breakdown

### 3.1 Resource Boundary Errors (False Positives on High Utility)
- **Failure Phenomenon:** The model ranks a satellite with 85% score for an optical imaging mission because elevation angle (88°) and slew speed (0.1°/s) are optimal, but the satellite is scheduled to enter Earth's shadow (eclipse) 45 seconds into the 60-second observation window.
- **Root Cause:** Symmetrical feature weighting fails to treat the binary `is_sunlit` transition as a hard step-function when battery State-of-Charge is hovering at 22%.
- **Frequency:** 3.4% of unconstrained neural predictions.
- **System Solution:** The Hybrid ML + CP-SAT pipeline rejects the candidate during hard constraint checking and falls back to the second-highest ranked candidate located in full sunlight.

### 3.2 Conflicting High-Priority Requests (Contention Hotspots)
- **Failure Phenomenon:** When multiple disaster response requests arrive within seconds of each other in the same geographic quadrant, the Cross-Attention network assigns the exact same "best" satellite to 4 distinct simultaneous tasks.
- **Root Cause:** The neural network scores each request-resource pair independently without global stateful lock awareness.
- **Frequency:** 14.2% under simulated crisis surge scenarios.
- **System Solution:** Candidate pruning selects Top-5 feasible satellites per task; CP-SAT global solver solves the bipartite matching formulation with mutual exclusion constraints.

### 3.3 Missing Data & Telemetry Staleness
- **Failure Phenomenon:** When ground station contact is lost and telemetry freshness degrades past 15 minutes, model MAE increases from 21.1 to 48.6.
- **Root Cause:** Historical battery state does not reflect discharge during silent orbital passes.
- **Frequency:** 6.1% under degraded communication links.
- **System Solution:** `DataQualityAgent` flags telemetry staleness > 10 min, down-weights confidence score in Trust Layer, and invokes Conservative Greedy Fallback.

### 3.4 Unseen Feature Combinations (Out-of-Distribution Weather / Solar Flare)
- **Failure Phenomenon:** Simultaneous high geomagnetic K-index (>7) coupled with heavy cloud cover produces indeterminate neural bid scores with high variance across attention heads.
- **Root Cause:** OOD tabular feature subspace not represented in nominal training sets.
- **System Solution:** Uncertainty estimation triggers an automated "INVESTIGATE" operator flag and falls back to deterministic heuristic scheduling.

---

## 4. Error Analysis Summary Table

| Operational Scenario | Error Pattern | Unassisted Neural Top-1 | Hybrid ML+CP-SAT Top-1 | Primary Mitigation Mechanism |
|---|---|---|---|---|
| **Nominal Daytime Passes** | Minor score variance | 94.2% | 100.0% | Standard neural inference |
| **Eclipse Transitions** | False positive on low-SoC node | 81.5% | 100.0% | CP-SAT hard battery constraint |
| **Multi-Request Contention** | Duplicate resource assignment | 68.2% | 100.0% | Global bipartite CP-SAT matching |
| **Stale Telemetry (>15 min)** | Power state misestimation | 72.4% | 96.0% | Data quality agent alert & fallback |
| **Space Weather Flare (OOD)** | High score entropy | 64.0% | 94.0% | Trust Layer operator escalation |
