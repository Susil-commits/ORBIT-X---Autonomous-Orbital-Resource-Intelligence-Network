"""Constellation Digital Twin & Time-Stepped Simulation Engine."""

import time
import math
import datetime
from typing import List, Dict, Optional, Tuple
import numpy as np

from app.core.schemas import (
    SatelliteState,
    GroundStation,
    MissionRequest,
    AccessWindow,
    ConstellationTick,
    ScheduleDecision,
    DecisionExplanation,
    CollisionAlert,
    HealthStatus,
    MissionStatus,
    WindowType,
    Position3D,
    TelemetryFrame,
)
from app.physics.orbit_propagator import (
    propagate_orbit,
    create_initial_constellation,
)
from app.physics.access_model import (
    find_access_windows,
    get_default_ground_stations,
)
from app.physics.collision import evaluate_conjunctions
from app.intelligence.battery_model import compute_step_battery_update
from app.intelligence.health_ai import get_health_ai
from app.intelligence.optimizer import ConstellationOptimizer
from app.simulation.scenarios import get_default_missions, generate_random_mission


class ConstellationSimulator:
    def __init__(self):
        self.sim_time_s: float = 0.0
        self.tick: int = 0
        self.speed_multiplier: float = 5.0
        self.is_running: bool = False
        self.optimizer_time_limit: float = 2.0
        
        self.satellites: List[SatelliteState] = create_initial_constellation()
        self.ground_stations: List[GroundStation] = get_default_ground_stations()
        self.pending_missions: List[MissionRequest] = get_default_missions(0.0)
        self.active_missions: List[MissionRequest] = []
        self.completed_missions: List[MissionRequest] = []
        
        self.recent_explanations: List[DecisionExplanation] = []
        self.collision_alerts: List[CollisionAlert] = []
        
        self.health_ai = get_health_ai()
        self.optimizer = ConstellationOptimizer(time_limit_seconds=self.optimizer_time_limit)
        
        self.fault_overrides: Dict[str, Dict[str, float]] = {}  # sat_id -> telemetry modifications
        self.last_schedule_time_s: float = -999.0
        self.replan_interval_s: float = 120.0
        
        # Initial run of optimizer to establish schedule
        self.replan_schedule()

    def replan_schedule(self):
        """Runs the CP-SAT optimizer to generate or update constellation schedule."""
        if not self.pending_missions:
            return
            
        # 1. Compute candidate imaging windows for all pending missions
        imaging_windows_map: Dict[str, Dict[str, List[AccessWindow]]] = {}
        for m in self.pending_missions:
            imaging_windows_map[m.id] = {}
            for sat in self.satellites:
                wins = find_access_windows(
                    satellite_id=sat.id,
                    keplerian=sat.keplerian,
                    target_or_station_id=m.id,
                    location=m.target_location,
                    window_type=WindowType.IMAGING,
                    start_time_s=self.sim_time_s,
                    horizon_s=3600.0,
                    time_step_s=15.0,
                )
                imaging_windows_map[m.id][sat.id] = wins

        # 2. Compute candidate downlink windows to all ground stations
        downlink_windows_map: Dict[str, Dict[str, List[AccessWindow]]] = {}
        for sat in self.satellites:
            downlink_windows_map[sat.id] = {}
            for gs in self.ground_stations:
                if not gs.is_active:
                    continue
                dl_wins = find_access_windows(
                    satellite_id=sat.id,
                    keplerian=sat.keplerian,
                    target_or_station_id=gs.id,
                    location=gs.location,
                    window_type=WindowType.DOWNLINK,
                    start_time_s=self.sim_time_s,
                    horizon_s=3600.0,
                    time_step_s=15.0,
                    min_elevation_deg=gs.min_elevation_deg,
                )
                downlink_windows_map[sat.id][gs.id] = dl_wins

        # 3. Solve CP-SAT
        decision = self.optimizer.solve(
            current_tick=self.tick,
            sim_time_s=self.sim_time_s,
            missions=self.pending_missions,
            satellites=self.satellites,
            ground_stations=self.ground_stations,
            imaging_windows_map=imaging_windows_map,
            downlink_windows_map=downlink_windows_map,
        )
        
        self.recent_explanations = decision.assignments
        self.last_schedule_time_s = self.sim_time_s
        
        # Apply assignments to pending missions
        for exp in decision.assignments:
            m = next((m for m in self.pending_missions if m.id == exp.mission_id), None)
            if m and exp.selected_satellite_id and exp.assigned_window:
                m.assigned_satellite_id = exp.selected_satellite_id
                m.imaging_start_s = exp.assigned_window.start_time_s
                m.imaging_end_s = exp.assigned_window.end_time_s
                m.status = MissionStatus.SCHEDULED
                if exp.downlink_window and exp.downlink_station_id:
                    m.downlink_ground_station_id = exp.downlink_station_id
                    m.downlink_start_s = exp.downlink_window.start_time_s
                    m.downlink_end_s = exp.downlink_window.end_time_s

    def step(self, dt_seconds: float = 1.0) -> ConstellationTick:
        """Advances constellation physics, telemetry, health AI, and task execution by dt_seconds."""
        eff_dt = dt_seconds * self.speed_multiplier
        self.sim_time_s += eff_dt
        self.tick += 1
        
        sat_map = {s.id: s for s in self.satellites}
        
        # 1. Update each satellite state
        for sat in self.satellites:
            # Orbital propagation
            r_eci, v_eci, r_ecef, geodetic, is_sunlit = propagate_orbit(sat.keplerian, self.sim_time_s)
            sat.position_eci = Position3D(x=float(r_eci[0]), y=float(r_eci[1]), z=float(r_eci[2]))
            sat.position_ecef = Position3D(x=float(r_ecef[0]), y=float(r_ecef[1]), z=float(r_ecef[2]))
            sat.geodetic = geodetic
            sat.velocity_kms = float(np.linalg.norm(v_eci))
            sat.battery.is_sunlit = is_sunlit
            
            # Check active tasks for this satellite
            is_imaging = False
            is_downlinking = False
            active_m_id = None
            active_task_type = None
            active_target_name = None
            
            # Check scheduled/active missions
            all_current_missions = self.pending_missions + self.active_missions
            for m in all_current_missions:
                if m.assigned_satellite_id == sat.id:
                    # Check imaging window
                    if m.imaging_start_s and m.imaging_end_s:
                        if m.imaging_start_s <= self.sim_time_s <= m.imaging_end_s:
                            is_imaging = True
                            active_m_id = m.id
                            active_task_type = "IMAGING"
                            active_target_name = m.name
                            m.status = MissionStatus.IN_PROGRESS
                            # Fill data buffer
                            sat.onboard_storage_used_gb = min(
                                sat.max_storage_gb,
                                sat.onboard_storage_used_gb + (m.data_size_gb / max(1.0, m.duration_s)) * eff_dt,
                            )
                    # Check downlink window
                    if m.downlink_start_s and m.downlink_end_s:
                        if m.downlink_start_s <= self.sim_time_s <= m.downlink_end_s:
                            is_downlinking = True
                            active_m_id = m.id
                            active_task_type = "DOWNLINK"
                            active_target_name = f"Downlink @ {m.downlink_ground_station_id}"
                            # Empty data buffer
                            sat.onboard_storage_used_gb = max(
                                0.0,
                                sat.onboard_storage_used_gb - (m.data_size_gb / max(1.0, m.downlink_end_s - m.downlink_start_s)) * eff_dt,
                            )
                            
            sat.active_mission_id = active_m_id
            sat.active_task_type = active_task_type
            sat.active_target_name = active_target_name
            
            # Update Battery
            power_mult = 1.0
            solar_mult = 1.0
            if sat.id in self.fault_overrides:
                power_mult = self.fault_overrides[sat.id].get("power_mult", 1.0)
                solar_mult = self.fault_overrides[sat.id].get("solar_mult", 1.0)
                
            new_soc, draw_w, solar_w = compute_step_battery_update(
                current_soc=sat.battery.soc,
                capacity_wh=sat.battery.capacity_wh,
                dt_seconds=eff_dt,
                is_sunlit=is_sunlit,
                is_imaging=is_imaging,
                is_downlinking=is_downlinking,
                solar_multiplier=solar_mult,
                power_draw_multiplier=power_mult,
            )
            sat.battery.soc = round(new_soc, 4)
            sat.battery.current_draw_w = round(draw_w, 1)
            sat.battery.solar_generation_w = round(solar_w, 1)
            
            # Telemetry synthesis
            noise_v = np.random.normal(0, 0.1)
            base_v = 28.2 if is_sunlit else 27.6
            v_bus = base_v - (draw_w / 400.0) + noise_v
            i_sol = (solar_w / 28.0) + np.random.uniform(0, 0.2) if is_sunlit else 0.0
            t_batt = 18.0 + (draw_w / 20.0) + np.random.normal(0, 0.2)
            t_pay = (35.0 if is_imaging else 22.0) + np.random.normal(0, 0.3)
            jitter = (0.08 if is_imaging else 0.02) + np.random.exponential(0.005)
            rf_snr = (18.5 if is_downlinking else 0.0) + np.random.normal(0, 0.4)
            
            # Apply any injected faults
            if sat.id in self.fault_overrides:
                overrides = self.fault_overrides[sat.id]
                v_bus += overrides.get("v_bus_delta", 0.0)
                t_batt += overrides.get("t_batt_delta", 0.0)
                t_pay += overrides.get("t_pay_delta", 0.0)
                jitter += overrides.get("jitter_delta", 0.0)
                rf_snr += overrides.get("rf_snr_delta", 0.0)
                
            frame = TelemetryFrame(
                timestamp_s=self.sim_time_s,
                bus_voltage_v=round(float(v_bus), 2),
                solar_current_a=round(float(i_sol), 2),
                battery_temp_c=round(float(t_batt), 1),
                payload_temp_c=round(float(t_pay), 1),
                reaction_wheel_jitter_dps=round(float(jitter), 4),
                rf_snr_db=round(float(rf_snr), 1),
                anomaly_score=0.0,
                health_status=HealthStatus.NOMINAL,
            )
            
            # Evaluate via Isolation Forest Health AI
            score, health = self.health_ai.evaluate_telemetry(frame)
            frame.anomaly_score = round(score, 3)
            frame.health_status = health
            sat.telemetry = frame
            sat.health_status = health

        # 2. Check Mission Completion & Expiration
        still_pending = []
        for m in self.pending_missions:
            # If mission downlink completed
            if m.downlink_end_s and self.sim_time_s >= m.downlink_end_s:
                m.status = MissionStatus.COMPLETED
                m.completed_at_s = self.sim_time_s
                self.completed_missions.append(m)
            elif (not m.downlink_end_s) and m.imaging_end_s and self.sim_time_s >= m.imaging_end_s:
                # If no specific downlink was required
                m.status = MissionStatus.COMPLETED
                m.completed_at_s = self.sim_time_s
                self.completed_missions.append(m)
            elif self.sim_time_s > m.deadline_s:
                # Deadline missed
                m.status = MissionStatus.FAILED
                self.completed_missions.append(m)
            else:
                still_pending.append(m)
                
        self.pending_missions = still_pending
        
        # 3. Autonomous Re-Planning Trigger (every interval or if healthy satellite failed)
        needs_replan = (self.sim_time_s - self.last_schedule_time_s) >= self.replan_interval_s
        for sat in self.satellites:
            if sat.health_status == HealthStatus.CRITICAL_FAULT and sat.active_mission_id:
                needs_replan = True
                
        if needs_replan and self.pending_missions:
            self.replan_schedule()
            
        # 4. Conjunction / Collision Risk Check
        if self.tick % 10 == 0:
            self.collision_alerts = evaluate_conjunctions(
                satellites=self.satellites,
                current_time_s=self.sim_time_s,
                lookahead_s=3600.0,
                time_step_s=45.0,
            )
            
        # 5. Build Summary Metrics
        total_m = len(self.completed_missions) + len(self.pending_missions)
        comp_m = len([m for m in self.completed_missions if m.status == MissionStatus.COMPLETED])
        succ_rate = (comp_m / max(1, len(self.completed_missions))) * 100.0 if self.completed_missions else 100.0
        avg_soc = float(np.mean([s.battery.soc for s in self.satellites])) * 100.0
        
        metrics = {
            "total_missions": total_m,
            "completed_missions": comp_m,
            "success_rate_pct": round(succ_rate, 1),
            "average_battery_soc_pct": round(avg_soc, 1),
            "active_anomalies": len([s for s in self.satellites if s.health_status != HealthStatus.NOMINAL]),
            "collision_warnings": len(self.collision_alerts),
            "sim_speed": f"{self.speed_multiplier}x",
        }
        
        iso_str = datetime.datetime.fromtimestamp(1776250000 + self.sim_time_s, tz=datetime.timezone.utc).isoformat()
        
        return ConstellationTick(
            tick=self.tick,
            sim_time_s=round(self.sim_time_s, 1),
            wall_clock_iso=iso_str,
            speed_multiplier=self.speed_multiplier,
            satellites=self.satellites,
            ground_stations=self.ground_stations,
            active_missions=[m for m in self.pending_missions if m.status == MissionStatus.IN_PROGRESS],
            pending_missions=self.pending_missions,
            completed_missions=self.completed_missions[-10:],
            recent_explanations=self.recent_explanations,
            collision_alerts=self.collision_alerts[:5],
            metrics_summary=metrics,
        )

    def inject_fault(self, sat_id: str, fault_type: str):
        """Injects synthetic telemetry fault into a satellite."""
        if sat_id not in self.fault_overrides:
            self.fault_overrides[sat_id] = {}
            
        if fault_type == "BATTERY_THERMAL_RUNAWAY":
            self.fault_overrides[sat_id]["t_batt_delta"] = 35.0
            self.fault_overrides[sat_id]["v_bus_delta"] = -6.5
            self.fault_overrides[sat_id]["power_mult"] = 3.0
        elif fault_type == "REACTION_WHEEL_JITTER":
            self.fault_overrides[sat_id]["jitter_delta"] = 0.45
        elif fault_type == "TRANSPONDER_FAILURE":
            self.fault_overrides[sat_id]["rf_snr_delta"] = -15.0
        elif fault_type == "SOLAR_ARRAY_SHADOW":
            self.fault_overrides[sat_id]["solar_mult"] = 0.05
            
        # Force re-plan
        self.replan_schedule()

    def clear_faults(self, sat_id: Optional[str] = None):
        """Clears synthetic faults."""
        if sat_id:
            self.fault_overrides.pop(sat_id, None)
        else:
            self.fault_overrides.clear()
        self.replan_schedule()

    def add_mission(self, mission: MissionRequest):
        """Appends a new dynamic mission and triggers re-optimization."""
        self.pending_missions.append(mission)
        self.replan_schedule()

    def reset(self):
        """Resets the simulation to t=0."""
        self.sim_time_s = 0.0
        self.tick = 0
        self.satellites = create_initial_constellation()
        self.ground_stations = get_default_ground_stations()
        self.pending_missions = get_default_missions(0.0)
        self.active_missions.clear()
        self.completed_missions.clear()
        self.fault_overrides.clear()
        self.recent_explanations.clear()
        self.collision_alerts.clear()
        self.replan_schedule()


# Global Singleton Simulator
_SIMULATOR_INSTANCE: Optional[ConstellationSimulator] = None


def get_simulator() -> ConstellationSimulator:
    global _SIMULATOR_INSTANCE
    if _SIMULATOR_INSTANCE is None:
        _SIMULATOR_INSTANCE = ConstellationSimulator()
    return _SIMULATOR_INSTANCE
