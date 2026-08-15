"""Google OR-Tools CP-SAT Constellation Mission & Downlink Optimizer."""

import time
import math
from typing import List, Dict, Tuple, Optional
from ortools.sat.python import cp_model

from app.core.schemas import (
    MissionRequest,
    SatelliteState,
    GroundStation,
    AccessWindow,
    ScheduleDecision,
    DecisionExplanation,
    HealthStatus,
    WindowType,
)
from app.intelligence.explainability import generate_decision_explanation


class ConstellationOptimizer:
    """
    CP-SAT constraint solver for multi-satellite, multi-ground-station,
    time-window constrained imaging and downlink scheduling.
    """

    def __init__(self, time_limit_seconds: float = 3.0):
        self.time_limit_seconds = time_limit_seconds

    def solve(
        self,
        current_tick: int,
        sim_time_s: float,
        missions: List[MissionRequest],
        satellites: List[SatelliteState],
        ground_stations: List[GroundStation],
        imaging_windows_map: Dict[str, Dict[str, List[AccessWindow]]],  # [mission_id][sat_id] -> [AccessWindow]
        downlink_windows_map: Dict[str, Dict[str, List[AccessWindow]]],  # [sat_id][station_id] -> [AccessWindow]
    ) -> ScheduleDecision:
        """Formulates and solves the CP-SAT constellation scheduling problem."""
        start_time_bench = time.perf_counter()
        
        model = cp_model.CpModel()
        
        # Decision Variables
        # x_vars[(m_id, s_id, w_idx)] = BoolVar
        # x_intervals[(m_id, s_id, w_idx)] = IntervalVar
        x_vars: Dict[Tuple[str, str, int], cp_model.IntVar] = {}
        x_windows: Dict[Tuple[str, str, int], AccessWindow] = {}
        sat_all_intervals: Dict[str, List[cp_model.IntervalVar]] = {s.id: [] for s in satellites}
        
        # y_vars[(m_id, s_id, g_id, dw_idx)] = BoolVar
        y_vars: Dict[Tuple[str, str, str, int], cp_model.IntVar] = {}
        y_windows: Dict[Tuple[str, str, str, int], AccessWindow] = {}
        station_all_intervals: Dict[str, List[cp_model.IntervalVar]] = {g.id: [] for g in ground_stations}
        
        # 1. Create Imaging Decision Variables
        for mission in missions:
            m_windows = imaging_windows_map.get(mission.id, {})
            for sat in satellites:
                if sat.health_status == HealthStatus.CRITICAL_FAULT:
                    continue  # Satellite excluded due to critical health
                if sat.battery.soc < 0.20:
                    continue  # Below safety threshold
                    
                candidate_wins = m_windows.get(sat.id, [])
                for w_idx, win in enumerate(candidate_wins):
                    # Check deadline
                    if win.end_time_s > mission.deadline_s:
                        continue
                        
                    var_key = (mission.id, sat.id, w_idx)
                    var_name = f"img_{mission.id}_{sat.id}_{w_idx}"
                    x_var = model.NewBoolVar(var_name)
                    x_vars[var_key] = x_var
                    x_windows[var_key] = win
                    
                    # Create interval variable for non-overlap constraint
                    # Round time to integer seconds
                    start_int = int(math.floor(win.start_time_s))
                    dur_int = max(1, int(math.ceil(win.duration_s)))
                    end_int = start_int + dur_int
                    
                    interval_var = model.NewOptionalIntervalVar(
                        start=start_int,
                        size=dur_int,
                        end=end_int,
                        is_present=x_var,
                        name=f"interval_{var_name}",
                    )
                    sat_all_intervals[sat.id].append(interval_var)

        # 2. Create Downlink Decision Variables
        for sat in satellites:
            if sat.health_status == HealthStatus.CRITICAL_FAULT:
                continue
            sat_dl_map = downlink_windows_map.get(sat.id, {})
            for g_station in ground_stations:
                if not g_station.is_active:
                    continue
                dl_wins = sat_dl_map.get(g_station.id, [])
                for dw_idx, dwin in enumerate(dl_wins):
                    for mission in missions:
                        # Only create downlink option if there's a potential imaging var for this (mission, sat)
                        matching_imgs = [k for k in x_vars if k[0] == mission.id and k[1] == sat.id]
                        if not matching_imgs:
                            continue
                            
                        # Downlink window must start after at least one candidate imaging window
                        feasible_precedence = any(x_windows[k].end_time_s <= dwin.start_time_s for k in matching_imgs)
                        if not feasible_precedence:
                            continue
                            
                        y_key = (mission.id, sat.id, g_station.id, dw_idx)
                        y_name = f"dl_{mission.id}_{sat.id}_{g_station.id}_{dw_idx}"
                        y_var = model.NewBoolVar(y_name)
                        y_vars[y_key] = y_var
                        y_windows[y_key] = dwin
                        
                        start_int = int(math.floor(dwin.start_time_s))
                        dur_int = max(1, int(math.ceil(dwin.duration_s)))
                        end_int = start_int + dur_int
                        
                        dl_interval_var = model.NewOptionalIntervalVar(
                            start=start_int,
                            size=dur_int,
                            end=end_int,
                            is_present=y_var,
                            name=f"dl_interval_{y_name}",
                        )
                        sat_all_intervals[sat.id].append(dl_interval_var)
                        station_all_intervals[g_station.id].append(dl_interval_var)

        # Constraint 1: At most one imaging assignment per mission
        for mission in missions:
            mission_img_vars = [x_vars[k] for k in x_vars if k[0] == mission.id]
            if mission_img_vars:
                model.Add(sum(mission_img_vars) <= 1)

        # Constraint 2: No-Overlap on Satellite Activities (Imaging + Downlink)
        for sat in satellites:
            intervals = sat_all_intervals[sat.id]
            if len(intervals) > 1:
                model.AddNoOverlap(intervals)

        # Constraint 3: No-Overlap on Ground Station Downlinks (Station Antenna Sharing)
        for g_station in ground_stations:
            g_intervals = station_all_intervals[g_station.id]
            if len(g_intervals) > 1:
                model.AddNoOverlap(g_intervals)

        # Constraint 4: Downlink Precedence & Coupling
        for mission in missions:
            mission_img_keys = [k for k in x_vars if k[0] == mission.id]
            for img_k in mission_img_keys:
                _, sat_id, _ = img_k
                img_win = x_windows[img_k]
                
                # Valid subsequent downlink vars for this satellite & mission
                valid_dl_vars = [
                    y_vars[yk] for yk in y_vars
                    if yk[0] == mission.id and yk[1] == sat_id and y_windows[yk].start_time_s >= img_win.end_time_s
                ]
                
                if valid_dl_vars:
                    # If imaged in this window, assign at least one downstream downlink
                    model.Add(sum(valid_dl_vars) >= x_vars[img_k])

        # Constraint 5: Battery Energy Conservation per Satellite
        for sat in satellites:
            sat_img_keys = [k for k in x_vars if k[1] == sat.id]
            sat_dl_keys = [yk for yk in y_vars if yk[1] == sat.id]
            
            # Energy budget = (SoC - 0.20) * capacity_wh (scaled as integer x10)
            max_drain_wh = max(0.0, (sat.battery.soc - 0.20) * sat.battery.capacity_wh)
            max_drain_scaled = int(math.floor(max_drain_wh * 10))
            
            img_energy_terms = []
            for k in sat_img_keys:
                m_id = k[0]
                m_obj = next((m for m in missions if m.id == m_id), None)
                cost_wh = m_obj.energy_cost_wh if m_obj else 15.0
                img_energy_terms.append(x_vars[k] * int(math.ceil(cost_wh * 10)))
                
            dl_energy_terms = []
            for yk in sat_dl_keys:
                dl_cost_wh = 10.0  # ~10Wh for downlink pass
                dl_energy_terms.append(y_vars[yk] * int(math.ceil(dl_cost_wh * 10)))
                
            if img_energy_terms or dl_energy_terms:
                model.Add(sum(img_energy_terms + dl_energy_terms) <= max_drain_scaled)

        # Constraint 6: Onboard Storage Capacity
        for sat in satellites:
            sat_img_keys = [k for k in x_vars if k[1] == sat.id]
            avail_storage_gb = max(0.0, sat.max_storage_gb - sat.onboard_storage_used_gb)
            avail_storage_scaled = int(math.floor(avail_storage_gb * 10))
            
            storage_terms = []
            for k in sat_img_keys:
                m_id = k[0]
                m_obj = next((m for m in missions if m.id == m_id), None)
                data_gb = m_obj.data_size_gb if m_obj else 12.0
                storage_terms.append(x_vars[k] * int(math.ceil(data_gb * 10)))
                
            if storage_terms:
                model.Add(sum(storage_terms) <= avail_storage_scaled)

        # Objective Function
        objective_terms = []
        
        # Value from mission execution
        for k, x_var in x_vars.items():
            m_id, sat_id, _ = k
            win = x_windows[k]
            m_obj = next((m for m in missions if m.id == m_id), None)
            priority = m_obj.priority if m_obj else 3
            reward = int(m_obj.reward) if m_obj else 100
            
            # Base priority weight
            weight = priority * reward * 10
            # Elevation bonus (higher elevation = sharper optical resolution)
            weight += int(win.max_elevation_deg * 5)
            # Sunlight bonus
            if win.is_sunlit:
                weight += 50
                
            # Satellite health penalty
            sat_obj = next((s for s in satellites if s.id == sat_id), None)
            if sat_obj and sat_obj.health_status == HealthStatus.DEGRADED:
                weight -= 150
                
            objective_terms.append(x_var * max(10, weight))
            
        # Value from downlinking data
        for yk, y_var in y_vars.items():
            objective_terms.append(y_var * 100)
            
        if objective_terms:
            model.Maximize(sum(objective_terms))
            
        # Solve Model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit_seconds
        solver.parameters.num_search_workers = 4
        
        status = solver.Solve(model)
        solve_time_ms = round((time.perf_counter() - start_time_bench) * 1000.0, 2)
        
        status_name = solver.StatusName(status)
        total_reward = 0.0
        explanations: List[DecisionExplanation] = []
        
        sat_map = {s.id: s for s in satellites}
        
        for mission in missions:
            assigned_sat: Optional[SatelliteState] = None
            assigned_win: Optional[AccessWindow] = None
            assigned_dl_win: Optional[AccessWindow] = None
            assigned_gs_id: Optional[str] = None
            rejection_reasons: Dict[str, str] = {}
            
            # Check if mission was scheduled
            for k, x_var in x_vars.items():
                if k[0] == mission.id and solver.Value(x_var) == 1:
                    assigned_sat = sat_map.get(k[1])
                    assigned_win = x_windows[k]
                    total_reward += mission.reward * mission.priority
                    break
                    
            # Check assigned downlink
            if assigned_sat:
                for yk, y_var in y_vars.items():
                    if yk[0] == mission.id and yk[1] == assigned_sat.id and solver.Value(y_var) == 1:
                        assigned_dl_win = y_windows[yk]
                        assigned_gs_id = yk[2]
                        break
                        
            # Generate Candidate Explanation
            m_windows = imaging_windows_map.get(mission.id, {})
            exp = generate_decision_explanation(
                mission=mission,
                selected_satellite=assigned_sat,
                assigned_window=assigned_win,
                downlink_window=assigned_dl_win,
                downlink_station_id=assigned_gs_id,
                all_satellites=satellites,
                candidate_windows=m_windows,
                rejection_reasons=rejection_reasons,
            )
            explanations.append(exp)
            
        return ScheduleDecision(
            tick=current_tick,
            sim_time_s=sim_time_s,
            assignments=explanations,
            solver_status=status_name,
            solver_time_ms=solve_time_ms,
            total_reward=total_reward,
        )
