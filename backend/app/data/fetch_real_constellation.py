"""Celestrak Real TLE Fetcher and Orbital Element Extractor for ORBIT-X.

Fetches genuine TLE elements from Celestrak for real LEO constellations
(e.g., Starlink, Planet Labs, ISS) and computes physically grounded Keplerian elements.
Fails loudly if Celestrak is unreachable; never writes synthetic elements under
the 'celestrak_real' data source tag.
"""

import os
import json
import math
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import httpx

# Physical Constants (WGS-84)
MU_EARTH = 398600.4418  # km^3 / s^2 (Earth standard gravitational parameter)
EARTH_RADIUS_KM = 6378.137  # km

CELESTRAK_STARLINK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
CELESTRAK_STATIONS_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=tle"
CELESTRAK_PLANET_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=planet&FORMAT=tle"

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ORBIT-X/2.0 Orbital-Intelligence"
}


def parse_tle_to_keplerian(line1: str, line2: str) -> Dict[str, Any]:
    """
    Parses a two-line element set (TLE) into Keplerian elements.
    
    Line 1 fields:
      - Catalog number: cols 3-7
    Line 2 fields:
      - Catalog number: cols 3-7
      - Inclination (degrees): cols 9-16
      - RAAN (degrees): cols 18-25
      - Eccentricity (decimal point assumed): cols 27-33
      - Argument of Perigee (degrees): cols 35-42
      - Mean Anomaly (degrees): cols 44-51
      - Mean Motion (revolutions/day): cols 53-63
    """
    line1 = line1.strip()
    line2 = line2.strip()
    
    if not (len(line1) >= 68 and len(line2) >= 68):
        raise ValueError(f"Invalid TLE line length: Line 1 ({len(line1)}), Line 2 ({len(line2)})")
    
    norad_id = int(line1[2:7].strip())
    inclination_deg = float(line2[8:16].strip())
    raan_deg = float(line2[17:25].strip())
    eccentricity_str = line2[26:33].strip()
    eccentricity = float("0." + eccentricity_str)
    arg_perigee_deg = float(line2[34:42].strip())
    mean_anomaly_deg = float(line2[43:51].strip())
    mean_motion_rev_per_day = float(line2[52:63].strip())
    
    if mean_motion_rev_per_day <= 0:
        raise ValueError(f"Invalid mean motion for NORAD {norad_id}: {mean_motion_rev_per_day}")
    
    # Convert mean motion from rev/day to rad/s: n = rev/day * 2pi / 86400
    n_rad_s = mean_motion_rev_per_day * (2.0 * math.pi) / 86400.0
    
    # Semi-major axis: a = (mu / n^2)^(1/3)
    semi_major_axis_km = (MU_EARTH / (n_rad_s ** 2)) ** (1.0 / 3.0)
    
    # Orbital period in seconds: T = 2pi / n_rad_s
    period_s = (2.0 * math.pi) / n_rad_s
    period_min = period_s / 60.0
    
    perigee_alt_km = semi_major_axis_km * (1.0 - eccentricity) - EARTH_RADIUS_KM
    apogee_alt_km = semi_major_axis_km * (1.0 + eccentricity) - EARTH_RADIUS_KM
    
    return {
        "norad_id": norad_id,
        "semi_major_axis_km": round(semi_major_axis_km, 4),
        "eccentricity": round(eccentricity, 7),
        "inclination_deg": round(inclination_deg, 4),
        "raan_deg": round(raan_deg, 4),
        "arg_perigee_deg": round(arg_perigee_deg, 4),
        "mean_anomaly_deg": round(mean_anomaly_deg, 4),
        "epoch_time_s": 0.0,
        "mean_motion_rev_day": round(mean_motion_rev_per_day, 6),
        "period_minutes": round(period_min, 3),
        "perigee_alt_km": round(perigee_alt_km, 2),
        "apogee_alt_km": round(apogee_alt_km, 2),
    }


def fetch_celestrak_tle(url: str, timeout_seconds: float = 15.0) -> str:
    """
    Pulls raw TLE data from Celestrak with strict error handling.
    Fails loudly if Celestrak is unreachable.
    """
    try:
        with httpx.Client(timeout=timeout_seconds, headers=HTTP_HEADERS, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
            content = resp.text.strip()
            if not content or len(content) < 50 or "No GP data found" in content:
                raise RuntimeError(f"Celestrak returned empty or invalid response from {url}")
            return content
    except Exception as e:
        raise RuntimeError(
            f"FAIL LOUDLY: Failed to fetch real TLE data from Celestrak ({url}). "
            f"Network error or Celestrak outage: {type(e).__name__} - {e}"
        ) from e


def fetch_and_save_real_constellation(
    target_count: int = 12,
    group: str = "starlink",
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Pulls real TLEs from Celestrak, parses genuine orbital elements,
    and saves to real_constellation.json.
    """
    if output_path is None:
        output_path = DATA_DIR / "real_constellation.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    url = CELESTRAK_STARLINK_URL if group == "starlink" else CELESTRAK_PLANET_URL
    print(f"Fetching real {group} TLE data from Celestrak ({url})...")
    
    raw_tle = fetch_celestrak_tle(url)
    lines = [line.strip() for line in raw_tle.splitlines() if line.strip()]
    
    satellites = []
    i = 0
    sat_idx = 1
    
    while i < len(lines) and len(satellites) < target_count:
        if lines[i].startswith("1 ") and i + 1 < len(lines) and lines[i + 1].startswith("2 "):
            sat_name = f"REAL-SAT-{sat_idx:02d}"
            line1 = lines[i]
            line2 = lines[i + 1]
            i += 2
        elif i + 2 < len(lines) and lines[i + 1].startswith("1 ") and lines[i + 2].startswith("2 "):
            sat_name = lines[i]
            line1 = lines[i + 1]
            line2 = lines[i + 2]
            i += 3
        else:
            i += 1
            continue
            
        try:
            elem = parse_tle_to_keplerian(line1, line2)
            satellites.append({
                "id": f"SAT-{sat_idx:02d}",
                "name": sat_name,
                "norad_id": elem["norad_id"],
                "orbit_plane": ((sat_idx - 1) % 3) + 1,
                "keplerian": {
                    "semi_major_axis_km": elem["semi_major_axis_km"],
                    "eccentricity": elem["eccentricity"],
                    "inclination_deg": elem["inclination_deg"],
                    "raan_deg": elem["raan_deg"],
                    "arg_perigee_deg": elem["arg_perigee_deg"],
                    "mean_anomaly_deg": elem["mean_anomaly_deg"],
                    "epoch_time_s": 0.0,
                },
                "mean_motion_rev_day": elem["mean_motion_rev_day"],
                "period_minutes": elem["period_minutes"],
                "perigee_alt_km": elem["perigee_alt_km"],
                "apogee_alt_km": elem["apogee_alt_km"],
            })
            sat_idx += 1
        except Exception as err:
            print(f"Skipping malformed TLE entry for {sat_name}: {err}")
            continue

    if len(satellites) < target_count:
        raise RuntimeError(f"Expected at least {target_count} satellites from Celestrak, got {len(satellites)}")

    payload = {
        "data_source": "celestrak_real",
        "constellation_group": group,
        "source_url": url,
        "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "satellite_count": len(satellites),
        "satellites": satellites,
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    print(f"Successfully saved {len(satellites)} real satellites to {output_path}")
    return payload


def verify_iss_orbital_period() -> Dict[str, Any]:
    """
    Fetches real TLE for ISS (ZARYA / NORAD 25544) from Celestrak and
    validates that its orbital period conforms to physical ground truth (~92.68 min).
    """
    raw_tle = fetch_celestrak_tle(CELESTRAK_STATIONS_URL)
    lines = [line.strip() for line in raw_tle.splitlines() if line.strip()]
    
    iss_elem = None
    for i in range(len(lines) - 2):
        if "ISS (ZARYA)" in lines[i] or "25544" in lines[i + 1]:
            iss_elem = parse_tle_to_keplerian(lines[i + 1], lines[i + 2])
            break
            
    if not iss_elem:
        for i in range(len(lines) - 1):
            if lines[i].startswith("1 25544"):
                iss_elem = parse_tle_to_keplerian(lines[i], lines[i + 1])
                break

    if not iss_elem:
        raise RuntimeError("FAIL LOUDLY: ISS (NORAD 25544) not found in Celestrak stations TLE dataset")
        
    period = iss_elem["period_minutes"]
    expected_period = 92.68
    tolerance_min = 1.5
    
    is_valid = abs(period - expected_period) <= tolerance_min
    if not is_valid:
        raise ValueError(
            f"Physical sanity check FAILED for ISS: measured period {period:.3f} min "
            f"deviates from expected {expected_period} min by more than {tolerance_min} min"
        )
        
    return {
        "norad_id": 25544,
        "name": "ISS (ZARYA)",
        "period_minutes": period,
        "semi_major_axis_km": iss_elem["semi_major_axis_km"],
        "altitude_km": iss_elem["perigee_alt_km"],
        "is_valid": True,
        "deviation_from_standard_min": round(abs(period - expected_period), 3),
    }


if __name__ == "__main__":
    print("Testing ISS Orbital Period Verification...")
    iss_res = verify_iss_orbital_period()
    print(f"ISS verification: {iss_res}")
    
    print("\nFetching real Starlink constellation subset...")
    res = fetch_and_save_real_constellation(target_count=12, group="starlink")
    print(f"Fetched {res['satellite_count']} real satellites. Data source: {res['data_source']}")
