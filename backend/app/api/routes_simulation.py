"""FastAPI Router for Simulation Controls & Fault Injection."""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional

from app.core.schemas import ConstellationTick
from app.simulation.simulator import get_simulator

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


class SpeedRequest(BaseModel):
    speed: float


class FaultRequest(BaseModel):
    satellite_id: str
    fault_type: str


@router.get("/state", response_model=ConstellationTick)
async def get_state():
    """Fetches the current constellation state snapshot."""
    sim = get_simulator()
    return await sim.step_async(dt_seconds=0.0)


@router.post("/start")
async def start_sim():
    """Starts / unpauses continuous simulation."""
    sim = get_simulator()
    sim.is_running = True
    return {"status": "RUNNING", "sim_time_s": sim.sim_time_s}


@router.post("/pause")
async def pause_sim():
    """Pauses continuous simulation."""
    sim = get_simulator()
    sim.is_running = False
    return {"status": "PAUSED", "sim_time_s": sim.sim_time_s}


@router.post("/step", response_model=ConstellationTick)
async def step_sim(dt_seconds: float = 1.0, dt: Optional[float] = None):
    """Executes a single simulation step. Accepts 'dt_seconds' or 'dt' query param."""
    sim = get_simulator()
    step_dt = dt if dt is not None else dt_seconds
    return await sim.step_async(dt_seconds=step_dt)


@router.post("/speed")
async def set_speed(speed: Optional[float] = None, req: Optional[SpeedRequest] = Body(default=None)):
    """Sets simulation time speed multiplier (1x, 5x, 20x, 60x). Accepts 'speed' query param or JSON body."""
    sim = get_simulator()
    # Prefer query param, then body
    speed_val = speed if speed is not None else (req.speed if req else None)
    if speed_val is None:
        raise HTTPException(status_code=400, detail="Speed parameter is required")
    if speed_val <= 0 or speed_val > 100:
        raise HTTPException(status_code=400, detail="Speed must be between 0.1 and 100")
    sim.speed_multiplier = speed_val
    return {"speed_multiplier": sim.speed_multiplier}


@router.post("/reset")
async def reset_sim():
    """Resets the simulation clock and constellation state to t=0."""
    sim = get_simulator()
    sim.reset()
    return {"status": "RESET", "sim_time_s": 0.0}


@router.post("/inject_fault")
async def inject_fault(
    sat_id: Optional[str] = None,
    fault_type: Optional[str] = None,
    req: Optional[FaultRequest] = Body(default=None),
):
    """Injects synthetic telemetry fault into a satellite. Accepts query params or JSON body."""
    sim = get_simulator()
    # Prefer query params, then body
    satellite_id = sat_id or (req.satellite_id if req else None)
    fault = fault_type or (req.fault_type if req else None)
    if not satellite_id or not fault:
        raise HTTPException(status_code=400, detail="sat_id and fault_type are required")
    sim.inject_fault(satellite_id, fault)
    return {"status": "FAULT_INJECTED", "satellite_id": satellite_id, "fault_type": fault}


@router.post("/clear_faults")
async def clear_faults(sat_id: Optional[str] = None, satellite_id: Optional[str] = None):
    """Clears injected faults. Accepts 'sat_id' or 'satellite_id' query param."""
    sim = get_simulator()
    # Accept both sat_id (frontend) and satellite_id (legacy)
    target_id = sat_id or satellite_id
    sim.clear_faults(target_id)
    return {"status": "FAULTS_CLEARED", "satellite_id": target_id}
