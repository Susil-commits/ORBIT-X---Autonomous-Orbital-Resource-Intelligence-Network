"""FastAPI Router for Celestrak Real TLE Data Synchronization & Verification."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.simulation.simulator import get_simulator
from app.data.fetch_real_constellation import (
    fetch_and_save_real_constellation,
    verify_iss_orbital_period,
)

router = APIRouter(prefix="/api/constellation", tags=["Constellation Data & Real TLE"])


@router.get("/source")
async def get_constellation_source():
    """Returns the active constellation data source ('synthetic' or 'celestrak_real')."""
    sim = get_simulator()
    sat = sim.satellites[0] if sim.satellites else None
    source = sat.data_source if sat else "synthetic"
    return {
        "active_source": source,
        "satellite_count": len(sim.satellites),
    }


@router.post("/switch_source")
async def switch_constellation_source(source: str):
    """
    Switches constellation data source between 'synthetic' Walker-Delta and 'celestrak_real' TLEs.
    Fails loudly if Celestrak real data is requested but unavailable.
    """
    if source not in ["synthetic", "celestrak_real"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid source. Must be 'synthetic' or 'celestrak_real'."
        )
        
    sim = get_simulator()
    try:
        sim.switch_constellation_source(source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "status": "SOURCE_SWITCHED",
        "new_source": source,
        "satellite_count": len(sim.satellites),
    }


@router.post("/fetch_celestrak")
async def fetch_live_celestrak_tle(group: str = "starlink", count: int = 12):
    """
    Fetches genuine live TLE elements from Celestrak for Starlink or Planet Labs.
    Fails loudly if Celestrak is unreachable.
    """
    try:
        payload = fetch_and_save_real_constellation(target_count=count, group=group)
        return {
            "status": "FETCH_SUCCESS",
            "data_source": payload["data_source"],
            "satellite_count": payload["satellite_count"],
            "fetched_at_utc": payload["fetched_at_utc"],
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Celestrak live fetch failed: {e}")


@router.get("/iss_verification")
async def get_iss_orbital_verification():
    """
    Fetches real ISS (NORAD 25544) TLE from Celestrak and returns ground-truth
    orbital period verification metrics (~92.68 min).
    """
    try:
        res = verify_iss_orbital_period()
        return res
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ISS verification failed: {e}")
