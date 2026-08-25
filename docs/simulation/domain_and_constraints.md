# Simulation Domain & Operational Constraints

## 1. Domain Positioning
In the ORBIT-X architecture, the satellite constellation simulation environment serves as the **operational dataset and constraint testbed**. It generates high-velocity, multivariate telemetry streams and enforces physical boundary constraints used to train, benchmark, stress-test, and evaluate the decision intelligence platform.

---

## 2. Telemetry Generation Subsystems

```
                     SIMULATION TELEMETRY SUBSYSTEMS
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
  ORBITAL DYNAMICS           POWER & BATTERY             THERMAL & RF
  - SGP4 Propagation         - Solar array generation    - Stefan-Boltzmann radiator
  - Keplerian elements       - Depth of Discharge (DoD)  - Component dissipation
  - Eclipse transitions      - Coulombic degradation     - Free-space path loss (FSPL)
```

---

## 3. Operational Constraints Modeled

### 3.1 Hard Physical Constraints (Zero Violations Allowed)
1. **Minimum Battery State of Charge (SoC):** Battery must never drop below 20% during observation or downlink passes to prevent unrecoverable cell damage.
2. **Thermal Maximum Threshold:** Payload temperature must not exceed 45°C during active sensor operations.
3. **Geometric Line of Sight (LoS):** Target elevation must exceed minimum optical horizon threshold ($\ge 15^\circ$ for optical, $\ge 10^\circ$ for SAR).
4. **Mutual Exclusion:** A satellite cannot simultaneously perform imaging on Target A and cross-link downlink on Target B if slew rates or antenna pointings conflict.

### 3.2 Soft Optimization Objectives (Utility Maximization)
1. **Priority-Weighted Imaging Value:** Maximize completed mission priority scores.
2. **Ground Sample Distance (GSD):** Prioritize near-nadir observation passes with higher elevation angles for superior optical resolution.
3. **Energy Efficiency:** Minimize slew maneuver power costs and prioritize operations during full sunlit orbital segments.

---

## 4. Operational Stress Scenarios

The simulation engine can inject realistic fault scenarios to evaluate AI platform resilience:
- **Solar Storm / Radiation Surge:** High-energy particle flux inducing sensor noise and temporary bit-flip anomalies.
- **Battery Cell Degradation:** Sudden 30% reduction in battery capacity on target node to trigger anomaly detection and autonomous task migration.
- **Communication Blackout:** Ground station outage requiring inter-satellite link (ISL) multihop routing.
