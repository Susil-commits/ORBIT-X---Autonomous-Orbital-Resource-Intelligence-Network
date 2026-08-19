# ORBIT-X — Physics Engine Authority & Assumption Catalog

**Document Reference:** `docs/PHYSICS_ASSUMPTIONS.md`  
**Purpose:** Formal specification of physical constants, orbital mechanics, thermal ODEs, RF/laser communications, and coordinate frame transformations used across the ORBIT-X Digital Twin.

---

## 1. Physical Constants

The following values represent standard invariant astronomical and physical constants used across all simulation modules:

| Parameter | Symbol | Value | Units | Standard / Reference |
| :--- | :--- | :--- | :--- | :--- |
| **Earth Gravitational Parameter** | $\mu_E$ | $3.986004418 \times 10^{14}$ | $\text{m}^3 / \text{s}^2$ | WGS-84 / EGM96 |
| **Earth Mean Equatorial Radius** | $R_E$ | $6.378137 \times 10^6$ | $\text{m}$ | WGS-84 |
| **Earth J2 Geopotential Harmonic** | $J_2$ | $1.08262668 \times 10^{-3}$ | dimensionless | WGS-84 Oblateness |
| **Earth Angular Rotation Rate** | $\omega_E$ | $7.292115 \times 10^{-5}$ | $\text{rad} / \text{s}$ | IERS Convention |
| **Speed of Light in Vacuum** | $c$ | $2.99792458 \times 10^8$ | $\text{m} / \text{s}$ | CODATA 2018 |
| **Stefan-Boltzmann Constant** | $\sigma_{SB}$ | $5.670374419 \times 10^{-8}$ | $\text{W} / (\text{m}^2 \cdot \text{K}^4)$ | CODATA 2018 |
| **Solar Constant (at 1 AU)** | $S_0$ | $1361.0$ | $\text{W} / \text{m}^2$ | SORCE / TSIS-1 |
| **Deep Space Background Temp** | $T_{space}$ | $3.0$ | $\text{K}$ | Cosmic Microwave Background |

---

## 2. Coordinate Frame Definitions

ORBIT-X maintains explicit frame distinctions to prevent silent coordinate mixing:

1. **Earth-Centered Inertial (ECI - J2000)**:
   - **Origin**: Earth's center of mass.
   - **Fundamental Plane**: Earth's mean equator at epoch J2000.0 ($t_0 = \text{2000-01-01 12:00:00 TT}$).
   - **X-axis**: Points toward the First Point of Aries (Vernal Equinox $\Upsilon$).
   - **Z-axis**: Points along Earth's north rotational axis.
   - **Y-axis**: Completes right-handed orthogonal triad ($\hat{Y} = \hat{Z} \times \hat{X}$).
   - *Application*: Orbital state vectors $(\mathbf{r}_{ECI}, \mathbf{v}_{ECI})$, Keplerian propagation, J2 perturbation integration.

2. **Earth-Centered Earth-Fixed (ECEF - WGS-84)**:
   - **Origin**: Earth's center of mass.
   - **Fundamental Plane**: True equatorial plane rotating with the Earth.
   - **X-axis**: Passes through the Prime Meridian (Greenwich, $0^\circ\text{ Longitude}$).
   - **Z-axis**: True geographic North Pole.
   - *Application*: Ground station coordinates, surface target tracking, cloud cover occlusion maps.
   - *Transformation*: $\mathbf{r}_{ECEF}(t) = \mathbf{R}_z(\theta_{GAST}(t)) \cdot \mathbf{r}_{ECI}(t)$, where $\theta_{GAST}(t) = \theta_0 + \omega_E t$.

3. **Topocentric Horizon (AER - Azimuth, Elevation, Range)**:
   - **Origin**: Ground station antenna phase center or Target surface location $(\phi_{lat}, \lambda_{lon}, h_{alt})$.
   - **Elevation Angle ($\theta_{el}$)**: Angle above the local horizon plane. Minimum operational constraint: $\theta_{el} \ge 10.0^\circ$.
   - *Application*: Access window calculation for optical imaging and RF ground station downlink passes.

---

## 3. Orbital Mechanics & Perturbation Models

### Keplerian Propagation (Unperturbed Baseline)
$$\ddot{\mathbf{r}} = -\frac{\mu_E}{\|\mathbf{r}\|^3} \mathbf{r}$$
- Semi-major axis $a = R_E + h_{alt}$
- Orbital Mean Motion $n = \sqrt{\frac{\mu_E}{a^3}}$
- Orbital Period $T = \frac{2\pi}{n} = 2\pi \sqrt{\frac{a^3}{\mu_E}}$ (e.g., $T \approx 5739\text{ s} \approx 95.65\text{ min}$ for $h=550\text{ km}$).

### J2 Perturbation (Earth Oblateness Secular Rates)
Secular drift of the Right Ascension of the Ascending Node ($\dot{\Omega}$) and Argument of Perigee ($\dot{\omega}$):
$$\dot{\Omega} = -\frac{3}{2} J_2 \left(\frac{R_E}{p}\right)^2 n \cos(i)$$
$$\dot{\omega} = \frac{3}{4} J_2 \left(\frac{R_E}{p}\right)^2 n (5\cos^2(i) - 1)$$
where $p = a(1 - e^2)$ is the semi-latus rectum and $i$ is orbital inclination.

---

## 4. Intersatellite Optical Laser Links (ISL)

1. **Maximum Geometric Range Threshold**: $D_{max} = 2500\text{ km}$.
2. **Earth Horizon Occlusion (Ray-Sphere Intersection)**:
   - Ray between Sat 1 ($\mathbf{r}_1$) and Sat 2 ($\mathbf{r}_2$): $\mathbf{r}(t) = \mathbf{r}_1 + t(\mathbf{r}_2 - \mathbf{r}_1)$, $t \in [0, 1]$.
   - Minimum approach distance to Earth center:
     $$d_{min} = \frac{\|\mathbf{r}_1 \times \mathbf{r}_2\|}{\|\mathbf{r}_2 - \mathbf{r}_1\|}$$
   - Hard occlusion constraint: If $d_{min} < R_E + h_{atmos}$ (with atmospheric buffer $h_{atmos} = 80\text{ km}$), link is blocked.
3. **Data Rate Model**: $R_{ISL} = 10\text{ Gbps}$ optical channel with latency $\tau = \frac{\|\mathbf{r}_2 - \mathbf{r}_1\|}{c}$.

---

## 5. Thermal & Battery Physics-Informed Models

### Stefan-Boltzmann Radiative Equilibrium ODE
$$m C_p \frac{dT}{dt} = \dot{Q}_{solar} + \dot{Q}_{albedo} + \dot{Q}_{internal} - \epsilon \sigma_{SB} A_{rad} (T^4 - T_{space}^4)$$
- Spacecraft Thermal Mass: $m C_p = 450.0\text{ J} / \text{K}$
- Radiator Area: $A_{rad} = 1.2\text{ m}^2$
- Surface Emissivity: $\epsilon = 0.85$
- Solar Absorptivity: $\alpha = 0.65$

### Battery State of Charge (SoC) Dynamics
$$\frac{dSoC}{dt} = \frac{1}{E_{max}} \left[ \eta_{charge} P_{solar}(t) \cdot \mathbb{I}_{sunlit} - \frac{P_{bus} + P_{payload} + P_{comms}}{\eta_{discharge}} \right]$$
- Maximum Capacity: $E_{max} = 240.0\text{ Wh} = 864,000\text{ J}$
- Hard Safety Floor: $SoC(t) \ge 0.20$ ($20\%$ minimum reserve for bus survival).

---

## 6. Public Ephemeris & Data Pipeline Assumptions

1. **CelesTrak / Space-Track Two-Line Elements (TLE)**:
   - SGP4 propagation valid within $\pm 7\text{ days}$ of TLE epoch.
   - Fallback hierarchy: Live HTTP $\to$ Local Disk Cache $\to$ Synthetic J2 Walker Delta Constellation.
2. **Space Debris / Conjunction Analysis**:
   - Time of Closest Approach (TCA) calculated via relative position trajectory distance minimization.
   - Hard Safety Margin: Conjunction Distance $d_{TCA} \ge 5.0\text{ km}$.
