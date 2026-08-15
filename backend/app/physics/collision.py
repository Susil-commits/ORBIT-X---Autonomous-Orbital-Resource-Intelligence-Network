"""Pairwise Conjunction & Collision-Risk (TCA) Assessment."""

from typing import List, Tuple
import numpy as np

from app.core.schemas import SatelliteState, CollisionAlert
from app.physics.orbit_propagator import propagate_orbit


def evaluate_conjunctions(
    satellites: List[SatelliteState],
    current_time_s: float,
    lookahead_s: float = 3600.0,
    time_step_s: float = 30.0,
    critical_threshold_km: float = 25.0,
    warning_threshold_km: float = 50.0,
) -> List[CollisionAlert]:
    """
    Evaluates pairwise separation distances across all satellites in the constellation
    over the lookahead horizon to detect potential close approaches (TCA).
    """
    alerts: List[CollisionAlert] = []
    num_sats = len(satellites)
    if num_sats < 2:
        return alerts
    
    num_steps = int(lookahead_s / time_step_s) + 1
    times = [current_time_s + k * time_step_s for k in range(num_steps)]
    
    # Pre-propagate trajectories: trajectories[sat_idx][time_idx] = r_eci
    trajectories = []
    for sat in satellites:
        traj = []
        for t in times:
            r_eci, _, _, _, _ = propagate_orbit(sat.keplerian, t)
            traj.append(r_eci)
        trajectories.append(traj)
        
    for i in range(num_sats):
        for j in range(i + 1, num_sats):
            sat_1 = satellites[i]
            sat_2 = satellites[j]
            
            min_dist = float("inf")
            min_t = current_time_s
            
            for t_idx, t in enumerate(times):
                r1 = trajectories[i][t_idx]
                r2 = trajectories[j][t_idx]
                dist = float(np.linalg.norm(r1 - r2))
                if dist < min_dist:
                    min_dist = dist
                    min_t = t
                    
            if min_dist <= warning_threshold_km:
                alerts.append(
                    CollisionAlert(
                        sat_1_id=sat_1.id,
                        sat_2_id=sat_2.id,
                        tca_s=min_t,
                        min_distance_km=round(min_dist, 2),
                        is_critical=bool(min_dist <= critical_threshold_km),
                    )
                )
                
    # Sort by criticality and proximity
    alerts.sort(key=lambda a: (not a.is_critical, a.min_distance_km))
    return alerts
