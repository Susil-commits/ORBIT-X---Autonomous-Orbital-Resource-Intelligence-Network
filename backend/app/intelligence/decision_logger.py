"""Structured Constellation Event & Decision Logger for ORBIT-X.

Logs mission assignments, solver optimizations, health anomalies, conjunction maneuvers,
and ISL mesh reroutes for grounded RAG retrieval and explainability.
"""

import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from collections import deque

from app.core.schemas import DecisionExplanation, CollisionAlert, ConjunctionManeuver, SatelliteState


class LoggedDecisionEvent:
    def __init__(
        self,
        record_id: str,
        tick: int,
        sim_time_s: float,
        event_type: str,
        summary: str,
        mission_id: Optional[str] = None,
        satellite_id: Optional[str] = None,
        target_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.record_id = record_id
        self.tick = tick
        self.sim_time_s = sim_time_s
        self.event_type = event_type
        self.summary = summary
        self.mission_id = mission_id
        self.satellite_id = satellite_id
        self.target_name = target_name
        self.details = details or {}
        self.created_at_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "tick": self.tick,
            "sim_time_s": self.sim_time_s,
            "event_type": self.event_type,
            "summary": self.summary,
            "mission_id": self.mission_id,
            "satellite_id": self.satellite_id,
            "target_name": self.target_name,
            "details": self.details,
            "created_at_iso": self.created_at_iso,
        }


class DecisionLogger:
    """In-memory ring buffer and persistent logger for constellation decisions."""

    def __init__(self, max_buffer_size: int = 500):
        self.max_buffer_size = max_buffer_size
        self.events: deque[LoggedDecisionEvent] = deque(maxlen=max_buffer_size)
        self._seed_initial_events()

    def _seed_initial_events(self):
        """Seeds standard baseline operational events so RAG has initial context."""
        initial_entries = [
            (
                0, 0.0, "CONSTELLATION_INIT",
                "Constellation initialized with 12 LEO satellites across 3 orbital planes at 550km altitude, 53.0 deg inclination.",
                None, "SAT-01", "GLOBAL",
                {"planes": 3, "sats_per_plane": 4}
            ),
            (
                1, 0.0, "ISL_TOPOLOGY_ESTABLISHED",
                "Intersatellite Optical Laser Link (ISL) mesh initialized with 18 active cross-links and multi-hop routing to Svalbard, Hawaii, and Hartebeesthoek ground stations.",
                None, None, "GROUND_MESH",
                {"active_links": 18, "ground_stations": 3}
            ),
            (
                2, 10.0, "MISSION_ASSIGNED",
                "Mission EO-HURRICANE-01 assigned to SAT-03 (Aegis-03). Selected due to high elevation pass (78.4 deg) and 88.5% battery margin. SAT-02 rejected due to low SoC margin (24%).",
                "EO-HURRICANE-01", "SAT-03", "Hurricane-Alpha-Atlantic",
                {"elevation_deg": 78.4, "battery_soc": 0.885, "rejected": ["SAT-02"]}
            ),
            (
                5, 45.0, "ANOMALY_DETECTED",
                "Spacecraft SAT-07 optical payload temperature spiked to +42.5°C during high-rate downlink pass. Isolation Forest flagged telemetry anomaly (Score: 0.74). Payload throttled to preserve thermal margin.",
                None, "SAT-07", "THERMAL_SUBSYSTEM",
                {"temp_c": 42.5, "anomaly_score": 0.74, "status": "DEGRADED"}
            ),
            (
                8, 90.0, "CONJUNCTION_AVOIDANCE",
                "Predicted close approach between SAT-05 and Debris Object COSMOS-2251 (TCA: T+1450s, Miss Distance: 1.42km). Autonomous avoidance maneuver executed (+0.85 m/s delta-V). Post-maneuver miss distance increased to 28.5km.",
                None, "SAT-05", "COSMOS-2251",
                {"tca_s": 1450.0, "delta_v_mps": 0.85, "miss_dist_km": 28.5}
            ),
        ]
        for tick, sim_t, ev_type, summary, m_id, sat_id, target, details in initial_entries:
            rec_id = f"LOG-{uuid.uuid4().hex[:8]}"
            self.events.append(
                LoggedDecisionEvent(
                    record_id=rec_id,
                    tick=tick,
                    sim_time_s=sim_t,
                    event_type=ev_type,
                    summary=summary,
                    mission_id=m_id,
                    satellite_id=sat_id,
                    target_name=target,
                    details=details,
                )
            )

    def log_mission_assignment(
        self,
        tick: int,
        sim_time_s: float,
        explanation: DecisionExplanation,
    ):
        """Logs a CP-SAT or multi-agent mission scheduling decision."""
        rec_id = f"LOG-{uuid.uuid4().hex[:8]}"
        summary = (
            f"Tick {tick} (T+{sim_time_s:.0f}s): Mission {explanation.mission_name} ({explanation.mission_id}) "
            f"priority {explanation.priority}. {explanation.selection_rationale}"
        )
        event = LoggedDecisionEvent(
            record_id=rec_id,
            tick=tick,
            sim_time_s=sim_time_s,
            event_type="MISSION_ASSIGNED" if explanation.selected_satellite_id else "MISSION_SCHEDULING_FAILED",
            summary=summary,
            mission_id=explanation.mission_id,
            satellite_id=explanation.selected_satellite_id,
            target_name=explanation.mission_name,
            details={
                "binding_constraints": explanation.binding_constraints,
                "battery_margin_pct": explanation.battery_margin_pct,
                "candidates_count": len(explanation.candidates_evaluated),
            },
        )
        self.events.append(event)

    def log_anomaly(
        self,
        tick: int,
        sim_time_s: float,
        satellite_id: str,
        anomaly_score: float,
        health_status: str,
        details_str: str,
    ):
        """Logs a spacecraft telemetry health anomaly."""
        rec_id = f"LOG-{uuid.uuid4().hex[:8]}"
        summary = (
            f"Tick {tick} (T+{sim_time_s:.0f}s): Spacecraft {satellite_id} telemetry anomaly score {anomaly_score:.2f} "
            f"transitioned health state to {health_status}. {details_str}"
        )
        event = LoggedDecisionEvent(
            record_id=rec_id,
            tick=tick,
            sim_time_s=sim_time_s,
            event_type="ANOMALY_DETECTED",
            summary=summary,
            satellite_id=satellite_id,
            details={"anomaly_score": anomaly_score, "health_status": health_status},
        )
        self.events.append(event)

    def log_conjunction(
        self,
        tick: int,
        sim_time_s: float,
        maneuver: ConjunctionManeuver,
    ):
        """Logs a conjunction collision alert and autonomous avoidance burn."""
        rec_id = f"LOG-{uuid.uuid4().hex[:8]}"
        summary = (
            f"Tick {tick} (T+{sim_time_s:.0f}s): Spacecraft {maneuver.satellite_id} executed collision avoidance maneuver "
            f"against {maneuver.debris_id} (Delta-V: {maneuver.burn_delta_v_mps:.2f} m/s). "
            f"Miss distance expanded from {maneuver.pre_maneuver_miss_distance_km:.2f}km to {maneuver.post_maneuver_miss_distance_km:.2f}km."
        )
        event = LoggedDecisionEvent(
            record_id=rec_id,
            tick=tick,
            sim_time_s=sim_time_s,
            event_type="MANEUVER_EXECUTED",
            summary=summary,
            satellite_id=maneuver.satellite_id,
            target_name=maneuver.debris_id,
            details={
                "burn_delta_v_mps": maneuver.burn_delta_v_mps,
                "pre_miss_km": maneuver.pre_maneuver_miss_distance_km,
                "post_miss_km": maneuver.post_maneuver_miss_distance_km,
            },
        )
        self.events.append(event)

    def get_all_events(self) -> List[LoggedDecisionEvent]:
        return list(self.events)


_global_logger: Optional[DecisionLogger] = None


def get_decision_logger() -> DecisionLogger:
    global _global_logger
    if _global_logger is None:
        _global_logger = DecisionLogger()
    return _global_logger
