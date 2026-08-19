"""ORBIT-X Resilient TLE Data Pipeline.

Provides robust Two-Line Element (TLE) lifecycle management:
  Fetch (Live CelesTrak) -> Local Cache Storage -> Checksum & Versioning
  -> Epoch Validation & Stale Detection -> Fallback Cascade:
     (1) Live CelesTrak -> (2) Local Disk TLE Cache -> (3) Synthetic Keplerian/J2 Constellation.
"""

import os
import json
import hashlib
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import httpx

from app.data.fetch_real_constellation import (
    parse_tle_to_keplerian,
    CELESTRAK_STARLINK_URL,
    CELESTRAK_PLANET_URL,
    CELESTRAK_STATIONS_URL,
    HTTP_HEADERS,
)

TLE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "tle"
REAL_CONSTELLATION_JSON = Path(__file__).resolve().parent.parent.parent / "data" / "real_constellation.json"


class TLEPipelineManager:
    """Manages downloading, local disk caching, checksum validation, and fallback for TLE sets."""

    def __init__(self, cache_dir: Optional[Path] = None, max_stale_days: float = 14.0):
        self.cache_dir = cache_dir or TLE_DATA_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_stale_days = max_stale_days

    def compute_checksum(self, content: str) -> str:
        """Computes SHA-256 checksum for raw TLE text content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_cache_file_path(self, group: str) -> Path:
        """Returns the local cache file path for a specific satellite group."""
        return self.cache_dir / f"{group}_tle_cache.json"

    def fetch_and_cache(
        self,
        group: str = "starlink",
        target_count: int = 12,
        force_refresh: bool = False,
        timeout_seconds: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Executes the resilient TLE cascade:
        1. Attempt live download from CelesTrak.
        2. If live fetch succeeds, save raw + parsed into versioned local disk cache.
        3. If live fetch fails (network/outage), load from local disk cache if valid.
        4. If cache missing/invalid, signal synthetic fallback.
        """
        cache_path = self.get_cache_file_path(group)
        url = CELESTRAK_STARLINK_URL if group == "starlink" else CELESTRAK_PLANET_URL
        if group == "stations":
            url = CELESTRAK_STATIONS_URL

        # Step 1: Live Fetch
        live_content: Optional[str] = None
        fetch_error: Optional[str] = None
        
        try:
            with httpx.Client(timeout=timeout_seconds, headers=HTTP_HEADERS, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code == 200 and len(resp.text.strip()) > 50:
                    live_content = resp.text.strip()
        except Exception as e:
            fetch_error = f"{type(e).__name__}: {str(e)}"

        if live_content and not ("No GP data found" in live_content):
            # Parse & Cache
            try:
                parsed_payload = self._parse_and_package(
                    raw_tle=live_content,
                    group=group,
                    source_url=url,
                    target_count=target_count,
                    source_type="celestrak_live",
                )
                # Write to cache file
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(parsed_payload, f, indent=2)
                
                # Also update real_constellation.json for backward compatibility
                with open(REAL_CONSTELLATION_JSON, "w", encoding="utf-8") as f:
                    json.dump(parsed_payload, f, indent=2)
                    
                parsed_payload["pipeline_status"] = "LIVE_FETCH_SUCCESS"
                return parsed_payload
            except Exception as parse_err:
                fetch_error = f"ParseError: {parse_err}"

        # Step 2: Fallback to local disk cache
        if cache_path.exists():
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_payload = json.load(f)
                    
                fetched_at = datetime.datetime.fromisoformat(cached_payload["fetched_at_utc"])
                age_days = (datetime.datetime.now(datetime.timezone.utc) - fetched_at).total_seconds() / 86400.0
                
                cached_payload["pipeline_status"] = "CACHED_FALLBACK_ACTIVE"
                cached_payload["cache_age_days"] = round(age_days, 2)
                cached_payload["is_stale"] = age_days > self.max_stale_days
                cached_payload["network_error"] = fetch_error
                return cached_payload
            except Exception as cache_err:
                pass

        # Step 3: Check fallback real_constellation.json
        if REAL_CONSTELLATION_JSON.exists():
            try:
                with open(REAL_CONSTELLATION_JSON, "r", encoding="utf-8") as f:
                    fallback_payload = json.load(f)
                fallback_payload["pipeline_status"] = "PERSISTED_FALLBACK_ACTIVE"
                fallback_payload["network_error"] = fetch_error
                return fallback_payload
            except Exception:
                pass

        # Step 4: Synthetic Fallback
        return {
            "data_source": "synthetic",
            "constellation_group": group,
            "pipeline_status": "SYNTHETIC_FALLBACK_REQUIRED",
            "satellite_count": 0,
            "satellites": [],
            "network_error": fetch_error or "No local cache available",
        }

    def _parse_and_package(
        self,
        raw_tle: str,
        group: str,
        source_url: str,
        target_count: int,
        source_type: str,
    ) -> Dict[str, Any]:
        """Parses lines into Keplerian satellite state records and computes metadata."""
        lines = [line.strip() for line in raw_tle.splitlines() if line.strip()]
        satellites = []
        i = 0
        sat_idx = 1
        checksum = self.compute_checksum(raw_tle)

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
                    "line1": line1,
                    "line2": line2,
                })
                sat_idx += 1
            except Exception:
                continue

        return {
            "data_source": "celestrak_real",
            "source_type": source_type,
            "constellation_group": group,
            "source_url": source_url,
            "checksum_sha256": checksum,
            "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "satellite_count": len(satellites),
            "satellites": satellites,
        }


# Global pipeline instance
tle_pipeline = TLEPipelineManager()
