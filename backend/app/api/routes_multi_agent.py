"""FastAPI Router for Multi-Agent Auction & Bidding Inspector."""

from fastapi import APIRouter
from typing import List, Dict

from app.core.schemas import AccessWindow, WindowType
from app.simulation.simulator import get_simulator
from app.physics.access_model import find_access_windows
from benchmarks.legacy.multi_agent import MultiAgentCoordinator, AuctionResult

router = APIRouter(prefix="/api/multi-agent", tags=["Multi-Agent"])


@router.get("/auction", response_model=List[AuctionResult])
async def get_auction_ledger():
    """Runs and returns the latest multi-agent bidding and conflict resolution ledger."""
    sim = get_simulator()
    
    # Compute candidate windows
    candidate_windows_map: Dict[str, Dict[str, List[AccessWindow]]] = {}
    for m in sim.pending_missions:
        candidate_windows_map[m.id] = {}
        for sat in sim.satellites:
            wins = find_access_windows(
                satellite_id=sat.id,
                keplerian=sat.keplerian,
                target_or_station_id=m.id,
                location=m.target_location,
                window_type=WindowType.IMAGING,
                start_time_s=sim.sim_time_s,
                horizon_s=3600.0,
            )
            candidate_windows_map[m.id][sat.id] = wins
            
    results = MultiAgentCoordinator.run_auction(
        missions=sim.pending_missions,
        satellites=sim.satellites,
        candidate_windows_map=candidate_windows_map,
    )
    return results
