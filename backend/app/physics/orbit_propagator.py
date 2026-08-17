"""Keplerian Orbit Propagator with J2 Perturbations, Eclipse Geometry & Real TLE Support."""

import math
import json
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import numpy as np

from app.core.schemas import (
    KeplerianElements,
    Position3D,
    GeodeticLocation,
    SatelliteState,
    BatteryState,
    TelemetryFrame,
    HealthStatus,
)

# Physical Constants (WGS-84 / GGM02)
MU_EARTH = 398600.4418  # km^3 / s^2 (Earth gravitational parameter)
EARTH_RADIUS_KM = 6378.137  # km (Earth equatorial radius)
EARTH_ROTATION_RAD_S = 7.2921159e-5  # rad/s (Earth sidereal rotation rate)
J2 = 1.08262668e-3  # Earth oblateness harmonic J2

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def solve_kepler(mean_anomaly_rad: float, eccentricity: float, tolerance: float = 1e-8, max_iter: int = 50) -> float:
    """Solve Kepler's equation M = E - e*sin(E) for Eccentric Anomaly E via Newton-Raphson."""
    M = mean_anomaly_rad % (2.0 * math.pi)
    if eccentricity < 0.8:
        E = M
    else:
        E = math.pi

    for _ in range(max_iter):
        f = E - eccentricity * math.sin(E) - M
        f_prime = 1.0 - eccentricity * math.cos(E)
        delta = f / f_prime
        E -= delta
        if abs(delta) < tolerance:
            break
    return E


def get_sun_position_eci(sim_time_s: float) -> np.ndarray:
    """Approximate Sun position unit vector in ECI frame for eclipse calculations."""
    obliquity = math.radians(23.4392911)
    day_fraction = (sim_time_s / 86400.0) % 365.25
    ecliptic_lon = (2.0 * math.pi * day_fraction / 365.25)
    
    x = math.cos(ecliptic_lon)
    y = math.sin(ecliptic_lon) * math.cos(obliquity)
    z = math.sin(ecliptic_lon) * math.sin(obliquity)
    vec = np.array([x, y, z], dtype=float)
    return vec / np.linalg.norm(vec)


def is_satellite_sunlit(r_eci: np.ndarray, sim_time_s: float) -> bool:
    """Determine whether a satellite in ECI position is in sunlight or Earth's shadow (cylindrical shadow)."""
    sun_unit = get_sun_position_eci(sim_time_s)
    r_norm = np.linalg.norm(r_eci)
    if r_norm == 0:
        return True
    
    proj = np.dot(r_eci, sun_unit)
    if proj > 0:
        return True
    
    perp_dist = np.linalg.norm(r_eci - proj * sun_unit)
    return perp_dist > EARTH_RADIUS_KM


def compute_orbital_period_minutes(semi_major_axis_km: float) -> float:
    """Computes Keplerian orbital period in minutes."""
    if semi_major_axis_km <= 0:
        return 0.0
    period_s = 2.0 * math.pi * math.sqrt((semi_major_axis_km ** 3) / MU_EARTH)
    return period_s / 60.0


def propagate_orbit(
    elements: KeplerianElements,
    sim_time_s: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, GeodeticLocation, bool]:
    """
    Propagates Keplerian orbital elements at a given simulation time `sim_time_s`.
    Returns:
        r_eci: [x, y, z] in km
        v_eci: [vx, vy, vz] in km/s
        r_ecef: [x, y, z] in km
        geodetic: GeodeticLocation (lat, lon, alt_km)
        is_sunlit: bool
    """
    a = elements.semi_major_axis_km
    e = elements.eccentricity
    i_rad = math.radians(elements.inclination_deg)
    raan_rad = math.radians(elements.raan_deg)
    arg_p_rad = math.radians(elements.arg_perigee_deg)
    M0_rad = math.radians(elements.mean_anomaly_deg)
    
    dt = sim_time_s - elements.epoch_time_s
    
    # Mean motion n (rad/s)
    n = math.sqrt(MU_EARTH / (a ** 3))
    
    # J2 Nodal and Perigee Secular Precession
    p = a * (1.0 - e ** 2)
    j2_factor = 1.5 * J2 * ((EARTH_RADIUS_KM / p) ** 2) * n
    raan_dot = -j2_factor * math.cos(i_rad)
    arg_p_dot = 0.5 * j2_factor * (5.0 * (math.cos(i_rad) ** 2) - 1.0)
    
    raan_t = (raan_rad + raan_dot * dt) % (2.0 * math.pi)
    arg_p_t = (arg_p_rad + arg_p_dot * dt) % (2.0 * math.pi)
    M_t = (M0_rad + n * dt) % (2.0 * math.pi)
    
    # Solve Kepler's equation
    E_t = solve_kepler(M_t, e)
    
    # True Anomaly nu
    sin_nu_2 = math.sqrt(1.0 + e) * math.sin(E_t / 2.0)
    cos_nu_2 = math.sqrt(1.0 - e) * math.cos(E_t / 2.0)
    nu = 2.0 * math.atan2(sin_nu_2, cos_nu_2)
    
    # Distance r (km)
    r = a * (1.0 - e * math.cos(E_t))
    
    # Position & Velocity in Perifocal Frame (PQW)
    r_pqw = np.array([
        r * math.cos(nu),
        r * math.sin(nu),
        0.0
    ], dtype=float)
    
    h_ang = math.sqrt(MU_EARTH * p)
    v_pqw = np.array([
        -(MU_EARTH / h_ang) * math.sin(nu),
        (MU_EARTH / h_ang) * (e + math.cos(nu)),
        0.0
    ], dtype=float)
    
    # Rotation Matrix from PQW to ECI
    cos_O, sin_O = math.cos(raan_t), math.sin(raan_t)
    cos_i, sin_i = math.cos(i_rad), math.sin(i_rad)
    cos_w, sin_w = math.cos(arg_p_t), math.sin(arg_p_t)
    
    R_pqw_to_eci = np.array([
        [
            cos_O * cos_w - sin_O * sin_w * cos_i,
            -cos_O * sin_w - sin_O * cos_w * cos_i,
            sin_O * sin_i
        ],
        [
            sin_O * cos_w + cos_O * sin_w * cos_i,
            -sin_O * sin_w + cos_O * cos_w * cos_i,
            -cos_O * sin_i
        ],
        [
            sin_w * sin_i,
            cos_w * sin_i,
            cos_i
        ]
    ], dtype=float)
    
    r_eci = R_pqw_to_eci @ r_pqw
    v_eci = R_pqw_to_eci @ v_pqw
    
    # Rotation from ECI to ECEF (Greenwich sidereal angle)
    theta_g = (EARTH_ROTATION_RAD_S * sim_time_s) % (2.0 * math.pi)
    cos_th, sin_th = math.cos(theta_g), math.sin(theta_g)
    R_eci_to_ecef = np.array([
        [cos_th, sin_th, 0.0],
        [-sin_th, cos_th, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=float)
    
    r_ecef = R_eci_to_ecef @ r_eci
    
    # Convert ECEF to Geodetic Latitude, Longitude, Altitude
    x, y, z = r_ecef[0], r_ecef[1], r_ecef[2]
    lon_rad = math.atan2(y, x)
    lon_deg = math.degrees(lon_rad)
    
    p_xy = math.sqrt(x * x + y * y)
    lat_rad = math.atan2(z, p_xy)
    lat_deg = math.degrees(lat_rad)
    
    altitude_km = math.sqrt(x * x + y * y + z * z) - EARTH_RADIUS_KM
    sunlit = is_satellite_sunlit(r_eci, sim_time_s)
    
    geodetic = GeodeticLocation(
        lat=lat_deg,
        lon=lon_deg,
        alt=altitude_km
    )
    
    return r_eci, v_eci, r_ecef, geodetic, sunlit


def create_synthetic_constellation(
    num_planes: int = 3,
    sats_per_plane: int = 4,
    altitude_km: float = 550.0,
    inclination_deg: float = 53.0,
) -> List[SatelliteState]:
    """Generates a synthetic Walker-Delta type LEO constellation."""
    semi_major_axis = EARTH_RADIUS_KM + altitude_km
    satellites = []
    
    sat_idx = 1
    for p in range(num_planes):
        raan = (p * 360.0 / num_planes) % 360.0
        for s in range(sats_per_plane):
            phase_offset = (p * 360.0 / (num_planes * sats_per_plane))
            mean_anomaly = ((s * 360.0 / sats_per_plane) + phase_offset) % 360.0
            
            sat_id = f"SAT-{sat_idx:02d}"
            name = f"Aegis-{sat_idx:02d}"
            
            keplerian = KeplerianElements(
                semi_major_axis_km=semi_major_axis,
                eccentricity=0.001,
                inclination_deg=inclination_deg,
                raan_deg=raan,
                arg_perigee_deg=0.0,
                mean_anomaly_deg=mean_anomaly,
                epoch_time_s=0.0,
            )
            
            r_eci, v_eci, r_ecef, geodetic, sunlit = propagate_orbit(keplerian, 0.0)
            v_mag = float(np.linalg.norm(v_eci))
            
            battery = BatteryState(
                soc=0.95,
                capacity_wh=800.0,
                current_draw_w=45.0,
                solar_generation_w=180.0 if sunlit else 0.0,
                is_sunlit=sunlit,
                projected_min_soc=0.88,
            )
            
            telemetry = TelemetryFrame(
                timestamp_s=0.0,
                bus_voltage_v=28.2,
                solar_current_a=6.4 if sunlit else 0.0,
                battery_temp_c=18.5,
                payload_temp_c=22.0,
                reaction_wheel_jitter_dps=0.02,
                rf_snr_db=18.5,
                anomaly_score=0.02,
                health_status=HealthStatus.NOMINAL,
            )
            
            sat_state = SatelliteState(
                id=sat_id,
                name=name,
                norad_id=None,
                data_source="synthetic",
                orbit_plane=p + 1,
                keplerian=keplerian,
                position_eci=Position3D(x=float(r_eci[0]), y=float(r_eci[1]), z=float(r_eci[2])),
                position_ecef=Position3D(x=float(r_ecef[0]), y=float(r_ecef[1]), z=float(r_ecef[2])),
                geodetic=geodetic,
                velocity_kms=v_mag,
                battery=battery,
                telemetry=telemetry,
                onboard_storage_used_gb=0.0,
                max_storage_gb=256.0,
                active_mission_id=None,
                active_task_type=None,
                health_status=HealthStatus.NOMINAL,
            )
            satellites.append(sat_state)
            sat_idx += 1
            
    return satellites


def load_real_constellation(data_path: Optional[Path] = None) -> List[SatelliteState]:
    """
    Loads genuine orbital elements from real_constellation.json (extracted from Celestrak).
    Fails loudly if file does not exist.
    """
    if data_path is None:
        data_path = DATA_DIR / "real_constellation.json"
        
    if not data_path.exists():
        raise FileNotFoundError(
            f"FAIL LOUDLY: Real constellation file '{data_path}' not found. "
            f"Please run 'python -m app.data.fetch_real_constellation' to fetch genuine TLE data."
        )
        
    with open(data_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
        
    if payload.get("data_source") != "celestrak_real":
        raise ValueError(
            f"FAIL LOUDLY: Invalid data_source '{payload.get('data_source')}' in {data_path}. "
            f"Expected 'celestrak_real'."
        )
        
    satellites = []
    for item in payload.get("satellites", []):
        keplerian_raw = item["keplerian"]
        keplerian = KeplerianElements(
            semi_major_axis_km=keplerian_raw["semi_major_axis_km"],
            eccentricity=keplerian_raw["eccentricity"],
            inclination_deg=keplerian_raw["inclination_deg"],
            raan_deg=keplerian_raw["raan_deg"],
            arg_perigee_deg=keplerian_raw.get("arg_perigee_deg", 0.0),
            mean_anomaly_deg=keplerian_raw["mean_anomaly_deg"],
            epoch_time_s=keplerian_raw.get("epoch_time_s", 0.0),
        )
        
        r_eci, v_eci, r_ecef, geodetic, sunlit = propagate_orbit(keplerian, 0.0)
        v_mag = float(np.linalg.norm(v_eci))
        
        battery = BatteryState(
            soc=0.95,
            capacity_wh=800.0,
            current_draw_w=45.0,
            solar_generation_w=180.0 if sunlit else 0.0,
            is_sunlit=sunlit,
            projected_min_soc=0.88,
        )
        
        telemetry = TelemetryFrame(
            timestamp_s=0.0,
            bus_voltage_v=28.2,
            solar_current_a=6.4 if sunlit else 0.0,
            battery_temp_c=18.5,
            payload_temp_c=22.0,
            reaction_wheel_jitter_dps=0.02,
            rf_snr_db=18.5,
            anomaly_score=0.02,
            health_status=HealthStatus.NOMINAL,
        )
        
        sat_state = SatelliteState(
            id=item["id"],
            name=item["name"],
            norad_id=item.get("norad_id"),
            data_source="celestrak_real",
            orbit_plane=item.get("orbit_plane", 1),
            keplerian=keplerian,
            position_eci=Position3D(x=float(r_eci[0]), y=float(r_eci[1]), z=float(r_eci[2])),
            position_ecef=Position3D(x=float(r_ecef[0]), y=float(r_ecef[1]), z=float(r_ecef[2])),
            geodetic=geodetic,
            velocity_kms=v_mag,
            battery=battery,
            telemetry=telemetry,
            onboard_storage_used_gb=0.0,
            max_storage_gb=256.0,
            active_mission_id=None,
            active_task_type=None,
            health_status=HealthStatus.NOMINAL,
        )
        satellites.append(sat_state)
        
    return satellites


def create_initial_constellation(
    source: str = "synthetic",
    num_planes: int = 3,
    sats_per_plane: int = 4,
    altitude_km: float = 550.0,
    inclination_deg: float = 53.0,
) -> List[SatelliteState]:
    """
    Factory function returning either real Celestrak constellation or synthetic Walker-Delta.
    """
    if source == "celestrak_real":
        return load_real_constellation()
    return create_synthetic_constellation(
        num_planes=num_planes,
        sats_per_plane=sats_per_plane,
        altitude_km=altitude_km,
        inclination_deg=inclination_deg,
    )
