"""Structured Decision Explanation & Counterfactual Reasoning Generator."""

from typing import List, Dict, Optional
from app.core.schemas import (
    MissionRequest,
    SatelliteState,
    AccessWindow,
    CandidateEvaluation,
    DecisionExplanation,
    HealthStatus,
)


def generate_decision_explanation(
    mission: MissionRequest,
    selected_satellite: Optional[SatelliteState],
    assigned_window: Optional[AccessWindow],
    downlink_window: Optional[AccessWindow],
    downlink_station_id: Optional[str],
    all_satellites: List[SatelliteState],
    candidate_windows: Dict[str, List[AccessWindow]],
    rejection_reasons: Dict[str, str],
) -> DecisionExplanation:
    """
    Constructs an explainability trail detailing why a satellite was assigned
    and why candidate alternatives were rejected.
    """
    candidates_evaluated: List[CandidateEvaluation] = []
    binding_constraints: List[str] = []
    
    for sat in all_satellites:
        is_selected = (selected_satellite is not None) and (sat.id == selected_satellite.id)
        windows = candidate_windows.get(sat.id, [])
        valid_windows = [w for w in windows if w.end_time_s <= mission.deadline_s]
        
        rejection_reason = rejection_reasons.get(sat.id)
        eligible = True
        
        if sat.health_status == HealthStatus.CRITICAL_FAULT:
            eligible = False
            rejection_reason = f"Excluded: Spacecraft health state is {sat.health_status.value} (Telemetry Anomaly Score: {sat.telemetry.anomaly_score:.2f})"
        elif sat.battery.soc < 0.25:
            eligible = False
            rejection_reason = f"Excluded: Battery SoC ({sat.battery.soc * 100:.1f}%) near or below 20% safety threshold"
        elif not valid_windows and not is_selected:
            eligible = False
            if windows:
                rejection_reason = f"Excluded: Access window (T+{windows[0].start_time_s:.0f}s) occurs after mission deadline (T+{mission.deadline_s:.0f}s)"
            else:
                rejection_reason = "Excluded: No line-of-sight ground track intersection within planning horizon"
                
        bid_score = 0.0
        if eligible or is_selected:
            # Multi-attribute scoring heuristic
            soc_factor = sat.battery.soc * 40.0
            elev_factor = (valid_windows[0].max_elevation_deg / 90.0 * 30.0) if valid_windows else 20.0
            storage_factor = (1.0 - (sat.onboard_storage_used_gb / sat.max_storage_gb)) * 15.0
            prio_factor = mission.priority * 15.0
            bid_score = round(soc_factor + elev_factor + storage_factor + prio_factor, 1)
            
        proj_soc = max(0.0, sat.battery.soc - (mission.energy_cost_wh / sat.battery.capacity_wh))
        first_access = valid_windows[0].start_time_s if valid_windows else None
        
        candidates_evaluated.append(
            CandidateEvaluation(
                satellite_id=sat.id,
                eligible=eligible,
                bid_score=bid_score,
                projected_soc_after_mission=round(proj_soc, 3),
                access_start_s=first_access,
                rejection_reason=rejection_reason if not is_selected else None,
            )
        )
        
    # Sort candidates by bid score
    candidates_evaluated.sort(key=lambda c: c.bid_score, reverse=True)
    
    if selected_satellite and assigned_window:
        battery_margin = round((selected_satellite.battery.soc - 0.20) * 100.0, 1)
        binding_constraints.append("LINE_OF_SIGHT_ELEVATION")
        binding_constraints.append("BATTERY_SAFETY_FLOOR_20%")
        binding_constraints.append("DEADLINE_PRE_EXPIRY")
        if downlink_window:
            binding_constraints.append("DOWNLINK_PRECEDENCE_ORDER")
            
        dl_info = f" with scheduled downlink at {downlink_station_id} (T+{downlink_window.start_time_s:.0f}s)" if downlink_station_id and downlink_window else ""
        rationale = (
            f"Assigned {selected_satellite.name} ({selected_satellite.id}) during access window "
            f"T+{assigned_window.start_time_s:.0f}s-T+{assigned_window.end_time_s:.0f}s "
            f"(Max Elevation: {assigned_window.max_elevation_deg:.1f}°, Sunlit: {assigned_window.is_sunlit}). "
            f"Maintains {battery_margin:.1f}% battery reserve above safety floor{dl_info}. "
            f"{len(candidates_evaluated) - 1} alternative satellites evaluated."
        )
    else:
        battery_margin = 0.0
        rationale = f"Mission could not be scheduled within constraints (Deadline: T+{mission.deadline_s:.0f}s, Priority: {mission.priority})."
        binding_constraints.append("NO_FEASIBLE_WINDOW_OR_BATTERY_EXHAUSTION")
        
    return DecisionExplanation(
        mission_id=mission.id,
        mission_name=mission.name,
        priority=mission.priority,
        selected_satellite_id=selected_satellite.id if selected_satellite else None,
        assigned_window=assigned_window,
        downlink_window=downlink_window,
        downlink_station_id=downlink_station_id,
        selection_rationale=rationale,
        candidates_evaluated=candidates_evaluated,
        battery_margin_pct=battery_margin,
        binding_constraints=binding_constraints,
    )
