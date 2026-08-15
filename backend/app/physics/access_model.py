"""Orbital Access & Line-of-Sight Window Computation."""

import math
from typing import List, Dict, Tuple, Optional
import numpy as np

from app.core.schemas import (
    KeplerianElements,
    GeodeticLocation,
    GroundStation,
    MissionRequest,
    AccessWindow,
    WindowType,
)
from app.physics.orbit_propagator import (
    EARTH_RADIUS_KM,
    propagate_orbit,
)


def geodetic_to_ecef(geo: GeodeticLocation) -> np.ndarray:
    """Converts geodetic lat/lon/alt (deg, deg, km) to ECEF coordinates (km)."""
    lat_rad = math.radians(geo.lat)
    lon_rad = math.radians(geo.lon)
    r = EARTH_RADIUS_KM + geo.alt
    
    x = r * math.cos(lat_rad) * math.cos(lon_rad)
    y = r * math.cos(lat_rad) * math.sin(lon_rad)
    z = r * math.sin(lat_rad)
    return np.array([x, y, z], dtype=float)


def compute_elevation_and_range(
    sat_ecef: np.ndarray,
    site_geo: GeodeticLocation,
) -> Tuple[float, float, float]:
    """
    Computes topocentric elevation angle (deg), azimuth (deg), and slant range (km)
    from a ground site towards a satellite.
    """
    site_ecef = geodetic_to_ecef(site_geo)
    rho = sat_ecef - site_ecef
    range_km = float(np.linalg.norm(rho))
    if range_km == 0:
        return 90.0, 0.0, 0.0
    
    lat_rad = math.radians(site_geo.lat)
    lon_rad = math.radians(site_geo.lon)
    
    # Topocentric Up, East, North basis vectors
    u_up = np.array([
        math.cos(lat_rad) * math.cos(lon_rad),
        math.cos(lat_rad) * math.sin(lon_rad),
        math.sin(lat_rad),
    ])
    
    sin_el = np.dot(rho, u_up) / range_km
    sin_el = max(-1.0, min(1.0, sin_el))
    elev_deg = math.degrees(math.asin(sin_el))
    
    u_east = np.array([-math.sin(lon_rad), math.cos(lon_rad), 0.0])
    u_north = np.array([
        -math.sin(lat_rad) * math.cos(lon_rad),
        -math.sin(lat_rad) * math.sin(lon_rad),
        math.cos(lat_rad),
    ])
    
    east_comp = np.dot(rho, u_east)
    north_comp = np.dot(rho, u_north)
    az_deg = math.degrees(math.atan2(east_comp, north_comp)) % 360.0
    
    return elev_deg, az_deg, range_km


def compute_off_nadir_angle(sat_ecef: np.ndarray, target_geo: GeodeticLocation) -> float:
    """Computes satellite off-nadir angle (deg) looking down at a ground target."""
    target_ecef = geodetic_to_ecef(target_geo)
    rho = target_ecef - sat_ecef
    range_km = np.linalg.norm(rho)
    sat_r = np.linalg.norm(sat_ecef)
    
    if range_km == 0 or sat_r == 0:
        return 0.0
    
    nadir_unit = -sat_ecef / sat_r
    cos_theta = np.dot(rho, nadir_unit) / range_km
    cos_theta = max(-1.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))


def find_access_windows(
    satellite_id: str,
    keplerian: KeplerianElements,
    target_or_station_id: str,
    location: GeodeticLocation,
    window_type: WindowType,
    start_time_s: float,
    horizon_s: float = 3600.0,  # 1 hour lookahead
    time_step_s: float = 15.0,
    min_elevation_deg: float = 10.0,
    max_off_nadir_deg: float = 40.0,
) -> List[AccessWindow]:
    """Scans and extracts continuous line-of-sight access windows over the planning horizon."""
    windows: List[AccessWindow] = []
    
    in_window = False
    window_start = 0.0
    max_el = 0.0
    ranges = []
    sunlit_samples = []
    
    num_steps = int(horizon_s / time_step_s) + 1
    
    for step in range(num_steps):
        t = start_time_s + step * time_step_s
        r_eci, _, r_ecef, _, is_sunlit = propagate_orbit(keplerian, t)
        
        elev_deg, _, rng_km = compute_elevation_and_range(r_ecef, location)
        off_nadir = compute_off_nadir_angle(r_ecef, location)
        
        # Determine visibility based on window type
        if window_type == WindowType.DOWNLINK:
            visible = elev_deg >= min_elevation_deg
        else:  # IMAGING
            visible = (elev_deg >= 0.0) and (off_nadir <= max_off_nadir_deg)
        
        if visible:
            if not in_window:
                in_window = True
                window_start = t
                max_el = elev_deg
                ranges = [rng_km]
                sunlit_samples = [is_sunlit]
            else:
                max_el = max(max_el, elev_deg)
                ranges.append(rng_km)
                sunlit_samples.append(is_sunlit)
        else:
            if in_window:
                in_window = False
                window_end = t
                duration = window_end - window_start
                if duration >= 15.0:  # Ignore transient sub-step glitches
                    avg_range = sum(ranges) / max(1, len(ranges))
                    is_sun = sum(sunlit_samples) > (len(sunlit_samples) / 2)
                    w_id = f"WIN-{satellite_id}-{target_or_station_id}-{int(window_start)}"
                    windows.append(
                        AccessWindow(
                            window_id=w_id,
                            satellite_id=satellite_id,
                            target_or_station_id=target_or_station_id,
                            window_type=window_type,
                            start_time_s=window_start,
                            end_time_s=window_end,
                            duration_s=duration,
                            max_elevation_deg=max_el,
                            avg_range_km=avg_range,
                            is_sunlit=is_sun,
                        )
                    )
                ranges = []
                sunlit_samples = []
                
    # Close window if still open at end of horizon
    if in_window:
        window_end = start_time_s + horizon_s
        duration = window_end - window_start
        if duration >= 15.0:
            avg_range = sum(ranges) / max(1, len(ranges))
            is_sun = sum(sunlit_samples) > (len(sunlit_samples) / 2)
            w_id = f"WIN-{satellite_id}-{target_or_station_id}-{int(window_start)}"
            windows.append(
                AccessWindow(
                    window_id=w_id,
                    satellite_id=satellite_id,
                    target_or_station_id=target_or_station_id,
                    window_type=window_type,
                    start_time_s=window_start,
                    end_time_s=window_end,
                    duration_s=duration,
                    max_elevation_deg=max_el,
                    avg_range_km=avg_range,
                    is_sunlit=is_sun,
                )
            )
            
    return windows


def get_default_ground_stations() -> List[GroundStation]:
    """Returns standard global ground-station network for LEO downlinks."""
    return [
        GroundStation(
            id="GS-SVALBARD",
            name="Svalbard Satellite Station (SvalSat)",
            location=GeodeticLocation(lat=78.2297, lon=15.4077, alt=0.4),
            min_elevation_deg=5.0,
            bandwidth_gbps=3.0,
            is_active=True,
        ),
        GroundStation(
            id="GS-TROLL",
            name="Troll Antarctic Ground Station",
            location=GeodeticLocation(lat=-72.0114, lon=2.5350, alt=1.27),
            min_elevation_deg=5.0,
            bandwidth_gbps=2.5,
            is_active=True,
        ),
        GroundStation(
            id="GS-HAWAII",
            name="South Point Hawaii Tracking Station",
            location=GeodeticLocation(lat=19.0167, lon=-155.6667, alt=0.1),
            min_elevation_deg=10.0,
            bandwidth_gbps=2.0,
            is_active=True,
        ),
        GroundStation(
            id="GS-MAURITIUS",
            name="Indian Ocean Ground Station (Mauritius)",
            location=GeodeticLocation(lat=-20.3484, lon=57.5522, alt=0.05),
            min_elevation_deg=10.0,
            bandwidth_gbps=2.0,
            is_active=True,
        ),
        GroundStation(
            id="GS-ALASKA",
            name="Poker Flat Research Range (Alaska)",
            location=GeodeticLocation(lat=65.1200, lon=-147.4300, alt=0.5),
            min_elevation_deg=7.0,
            bandwidth_gbps=2.5,
            is_active=True,
        ),
    ]
