"""FastAPI Router for Intersatellite Optical Laser Links (ISL) Mesh & Routing."""

from fastapi import APIRouter
from typing import List

from app.core.schemas import ISLMeshState, ISLRoute, ISLLink
from app.simulation.simulator import get_simulator

router = APIRouter(prefix="/api/isl", tags=["Intersatellite Links"])


@router.get("/topology", response_model=ISLMeshState)
async def get_isl_topology():
    """Fetches the active constellation ISL cross-link mesh topology."""
    sim = get_simulator()
    if sim.isl_mesh is None:
        from app.physics.isl_network import build_isl_mesh
        sim.isl_mesh = build_isl_mesh(sim.satellites, sim.ground_stations)
    return sim.isl_mesh


@router.get("/routes", response_model=List[ISLRoute])
async def get_isl_routes():
    """Fetches calculated multi-hop relay routes to ground stations."""
    sim = get_simulator()
    if sim.isl_mesh:
        return sim.isl_mesh.routes
    return []
