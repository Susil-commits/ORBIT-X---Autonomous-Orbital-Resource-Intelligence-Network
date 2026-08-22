# ORBIT-X Simulation Environment & Astrodynamics Reference

## Purpose & Scope
The ORBIT-X Simulation Environment serves as the **high-fidelity domain testbed and synthetic telemetry generator** for evaluating the AI/ML decision intelligence platform. It provides realistic physical constraints, orbital pass geometry, line-of-sight communication windows, and thermal/power dynamics without obscuring the transferable AI engineering core of the platform.

---

## Architecture Overview
```
                     ORBIT-X AI / ML Platform
                                ▲
                                │ Operational Constraints & Telemetry Stream
                                ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DOMAIN SIMULATION ENVIRONMENT                        │
├──────────────────────┬────────────────────────┬────────────────────────┤
│  Orbital Dynamics    │   Spacecraft Physics   │   Scenario Injector    │
│  • SGP4 / TLE        │   • Battery ODEs       │   • Solar Flare        │
│  • WGS-84 J2 Drift   │   • Thermal Radiation  │   • Debris Conjunction │
│  • Keplerian 2-Body  │   • Reaction Wheels    │   • Ground Blackout    │
└──────────────────────┴────────────────────────┴────────────────────────┘
```

---

## Astrodynamics Formulations

### 1. Keplerian & Secular $J_2$ Earth Oblateness Perturbations
Satellite orbits are propagated using analytic two-body Keplerian mechanics augmented with first-order Earth oblateness ($J_2$) secular drift:

- **Orbital Period:**
  $$T = 2\pi \sqrt{\frac{a^3}{\mu}}$$
  where $\mu = 398,600.4418\text{ km}^3/\text{s}^2$, $R_E = 6,378.137\text{ km}$, $J_2 = 1.08263 \times 10^{-3}$.
- **Nodal Precession (RAAN drift $\dot{\Omega}$):**
  $$\dot{\Omega} = -\frac{3}{2} J_2 \left(\frac{R_E}{p}\right)^2 \bar{n} \cos(i)$$
- **Argument of Perigee Precession ($\dot{\omega}$):**
  $$\dot{\omega} = \frac{3}{4} J_2 \left(\frac{R_E}{p}\right)^2 \bar{n} (5\cos^2(i) - 1)$$

### 2. CelesTrak TLE Ingestion Pipeline
- **Ephemeris Ingestion:** Automated caching of active Two-Line Element (TLE) ephemeris from CelesTrak with SHA-256 integrity verification.
- **Failover Cascade:** Network → Local Disk Cache → Validated SHA-256 Package → Synthetic Constellation Fallback.

### 3. Spacecraft Power & Non-Linear Thermal Physics (PINN Simulator)
- **Solar Power Generation:**
  $$P_{\text{solar}} = I_{\text{sunlit}} \cdot \eta_{\text{array}} \cdot A_{\text{array}} \cdot G_{\text{solar}} \cos(\theta_{\text{sun}})$$
- **Stefan-Boltzmann Radiative Cooling ODE:**
  $$m_{\text{sat}} c_p \frac{dT_{\text{sat}}}{dt} = \dot{Q}_{\text{internal}} + \alpha_{\text{solar}} A_{\text{proj}} G_{\text{solar}} - \epsilon \sigma A_{\text{rad}} \left(T_{\text{sat}}^4 - T_{\text{space}}^4\right)$$

---

## 10 Operational Disruption Scenarios
The simulation includes an event-driven scenario director for evaluating AI resilience:
1. `SOLAR_STORM`: Extreme radiation flux, solar array degradation, and communication SNR loss.
2. `DEBRIS_CONJUNCTION`: Close approach with tracked orbital debris requiring autonomous avoidance maneuvers.
3. `GROUND_BLACKOUT`: Ground station hardware offline, forcing inter-satellite laser mesh (ISL) rerouting.
4. `DISASTER_SURGE`: Sudden influx of high-priority emergency imaging targets (hurricanes, wildfires).
5. `SATELLITE_FAILURE`: Instantaneous spacecraft power bus collapse triggering automated load re-distribution.
6. `ISL_LOSS`: Intersatellite optical link failure requiring ground-hop fallback.
7. `BATTERY_DEGRADATION`: Subsystem cell loss lowering usable State-of-Charge headroom.
8. `THERMAL_OVERLOAD`: Optical imaging sensor temperature spike requiring duty-cycle throttling.
9. `STALE_TLE`: Ephemeris data corruption triggering checksum fallback.
10. `GPS_JITTER`: Attitude control jitter forcing reaction wheel desaturation.
