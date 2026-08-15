"""Tests for CP-SAT Optimizer & Multi-Agent Bidding."""

from app.physics.orbit_propagator import create_initial_constellation
from app.physics.access_model import find_access_windows, get_default_ground_stations
from app.intelligence.optimizer import ConstellationOptimizer
from app.intelligence.multi_agent import MultiAgentCoordinator
from app.simulation.scenarios import get_default_missions
from app.core.schemas import WindowType, HealthStatus


def test_cpsat_optimizer_scheduling():
    satellites = create_initial_constellation(num_planes=3, sats_per_plane=4)
    ground_stations = get_default_ground_stations()
    missions = get_default_missions(0.0)[:4]  # Take 4 missions
    
    # Calculate access windows
    imaging_windows_map = {}
    for m in missions:
        imaging_windows_map[m.id] = {}
        for sat in satellites:
            wins = find_access_windows(
                satellite_id=sat.id,
                keplerian=sat.keplerian,
                target_or_station_id=m.id,
                location=m.target_location,
                window_type=WindowType.IMAGING,
                start_time_s=0.0,
                horizon_s=3600.0,
            )
            imaging_windows_map[m.id][sat.id] = wins

    downlink_windows_map = {}
    for sat in satellites:
        downlink_windows_map[sat.id] = {}
        for gs in ground_stations:
            dl_wins = find_access_windows(
                satellite_id=sat.id,
                keplerian=sat.keplerian,
                target_or_station_id=gs.id,
                location=gs.location,
                window_type=WindowType.DOWNLINK,
                start_time_s=0.0,
                horizon_s=3600.0,
            )
            downlink_windows_map[sat.id][gs.id] = dl_wins

    optimizer = ConstellationOptimizer(time_limit_seconds=2.0)
    decision = optimizer.solve(
        current_tick=0,
        sim_time_s=0.0,
        missions=missions,
        satellites=satellites,
        ground_stations=ground_stations,
        imaging_windows_map=imaging_windows_map,
        downlink_windows_map=downlink_windows_map,
    )
    
    assert decision.solver_status in ["OPTIMAL", "FEASIBLE"]
    assert len(decision.assignments) == len(missions)
    # Check that at least some missions got scheduled
    scheduled = [a for a in decision.assignments if a.selected_satellite_id is not None]
    assert len(scheduled) > 0


def test_multi_agent_auction():
    satellites = create_initial_constellation(num_planes=2, sats_per_plane=3)
    missions = get_default_missions(0.0)[:3]
    
    candidate_windows_map = {}
    for m in missions:
        candidate_windows_map[m.id] = {}
        for sat in satellites:
            wins = find_access_windows(
                satellite_id=sat.id,
                keplerian=sat.keplerian,
                target_or_station_id=m.id,
                location=m.target_location,
                window_type=WindowType.IMAGING,
                start_time_s=0.0,
                horizon_s=3600.0,
            )
            candidate_windows_map[m.id][sat.id] = wins
            
    results = MultiAgentCoordinator.run_auction(
        missions=missions,
        satellites=satellites,
        candidate_windows_map=candidate_windows_map,
    )
    
    assert len(results) == len(missions)
