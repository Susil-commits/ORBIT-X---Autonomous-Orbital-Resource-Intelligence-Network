"""FastAPI Router for Simulation Controls & Fault Injection."""

from fastapi import APIRouter, HTTPException
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
async def step_sim(dt_seconds: float = 1.0):
    """Executes a single simulation step."""
    sim = get_simulator()
    return await sim.step_async(dt_seconds=dt_seconds)


@router.post("/speed")
async def set_speed(req: SpeedRequest):
    """Sets simulation time speed multiplier (1x, 5x, 20x, 60x)."""
    sim = get_simulator()
    if req.speed <= 0 or req.speed > 100:
        raise HTTPException(status_code=400, detail="Speed must be between 0.1 and 100")
    sim.speed_multiplier = req.speed
    return {"speed_multiplier": sim.speed_multiplier}


@router.post("/reset")
async def reset_sim():
    """Resets the simulation clock and constellation state to t=0."""
    sim = get_simulator()
    sim.reset()
    return {"status": "RESET", "sim_time_s": 0.0}


@router.post("/inject_fault")
async def inject_fault(req: FaultRequest):
    """Injects synthetic telemetry fault into a satellite."""
    sim = get_simulator()
    sim.inject_fault(req.satellite_id, req.fault_type)
    return {"status": "FAULT_INJECTED", "satellite_id": req.satellite_id, "fault_type": req.fault_type}


@router.post("/clear_faults")
async def clear_faults(satellite_id: Optional[str] = None):
    """Clears injected faults."""
    sim = get_simulator()
    sim.clear_faults(satellite_id)
    return {"status": "FAULTS_CLEARED", "satellite_id": satellite_id}
