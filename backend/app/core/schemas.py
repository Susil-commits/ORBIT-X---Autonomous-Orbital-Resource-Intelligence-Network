"""Pydantic v2 domain schemas for ORBIT-X."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    NOMINAL = "NOMINAL"
    DEGRADED = "DEGRADED"
    CRITICAL_FAULT = "CRITICAL_FAULT"


class MissionStatus(str, Enum):
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class WindowType(str, Enum):
    IMAGING = "IMAGING"
    DOWNLINK = "DOWNLINK"


class Position3D(BaseModel):
    x: float = Field(..., description="X coordinate (km)")
    y: float = Field(..., description="Y coordinate (km)")
    z: float = Field(..., description="Z coordinate (km)")


class GeodeticLocation(BaseModel):
    lat: float = Field(..., description="Latitude in degrees [-90, 90]")
    lon: float = Field(..., description="Longitude in degrees [-180, 180]")
    alt: float = Field(0.0, description="Altitude in km")


class KeplerianElements(BaseModel):
    semi_major_axis_km: float = Field(..., description="Semi-major axis 'a' (km)")
    eccentricity: float = Field(0.0, description="Eccentricity 'e'")
    inclination_deg: float = Field(..., description="Inclination 'i' in degrees")
    raan_deg: float = Field(..., description="Right Ascension of Ascending Node in degrees")
    arg_perigee_deg: float = Field(0.0, description="Argument of perigee in degrees")
    mean_anomaly_deg: float = Field(0.0, description="Mean anomaly at epoch M0 in degrees")
    epoch_time_s: float = Field(0.0, description="Epoch reference time in seconds")


class TelemetryFrame(BaseModel):
    timestamp_s: float
    bus_voltage_v: float = Field(..., description="Main power bus voltage (28V nominal)")
    solar_current_a: float = Field(..., description="Solar array current (A)")
    battery_temp_c: float = Field(..., description="Battery cell temperature (°C)")
    payload_temp_c: float = Field(..., description="Optical/SAR payload sensor temperature (°C)")
    reaction_wheel_jitter_dps: float = Field(..., description="Attitude control RMS jitter (deg/s)")
    rf_snr_db: float = Field(..., description="X-band RF downlink SNR (dB)")
    anomaly_score: float = Field(0.0, description="ML anomaly score from Isolation Forest [0, 1]")
    health_status: HealthStatus = Field(HealthStatus.NOMINAL)


class BatteryState(BaseModel):
    soc: float = Field(..., ge=0.0, le=1.0, description="State of charge [0.0, 1.0]")
    capacity_wh: float = Field(800.0, description="Total battery capacity in Watt-hours")
    current_draw_w: float = Field(50.0, description="Instantaneous power draw in Watts")
    solar_generation_w: float = Field(0.0, description="Instantaneous solar power harvest in Watts")
    is_sunlit: bool = Field(True, description="True if satellite is in direct sunlight (not eclipsed)")
    projected_min_soc: float = Field(1.0, description="Projected minimum SoC over planning horizon")


class SatelliteState(BaseModel):
    id: str
    name: str
    orbit_plane: int = 1
    keplerian: KeplerianElements
    position_eci: Position3D
    position_ecef: Position3D
    geodetic: GeodeticLocation
    velocity_kms: float
    battery: BatteryState
    telemetry: TelemetryFrame
    onboard_storage_used_gb: float = 0.0
    max_storage_gb: float = 256.0
    active_mission_id: Optional[str] = None
    active_task_type: Optional[str] = None  # None, "IMAGING", "DOWNLINK"
    active_target_name: Optional[str] = None
    health_status: HealthStatus = HealthStatus.NOMINAL


class GroundStation(BaseModel):
    id: str
    name: str
    location: GeodeticLocation
    min_elevation_deg: float = 10.0
    bandwidth_gbps: float = 2.5
    is_active: bool = True


class MissionRequest(BaseModel):
    id: str
    name: str
    target_location: GeodeticLocation
    priority: int = Field(3, ge=1, le=5, description="1=Lowest, 5=Emergency/Critical")
    reward: float = 100.0
    deadline_s: float = Field(..., description="Simulation time deadline (seconds)")
    duration_s: float = Field(30.0, description="Required imaging duration (seconds)")
    data_size_gb: float = Field(12.0, description="Generated telemetry/raw payload data (GB)")
    energy_cost_wh: float = Field(15.0, description="Energy required for imaging pass (Wh)")
    status: MissionStatus = MissionStatus.PENDING
    assigned_satellite_id: Optional[str] = None
    imaging_start_s: Optional[float] = None
    imaging_end_s: Optional[float] = None
    downlink_ground_station_id: Optional[str] = None
    downlink_start_s: Optional[float] = None
    downlink_end_s: Optional[float] = None
    created_at_s: float = 0.0
    completed_at_s: Optional[float] = None


class AccessWindow(BaseModel):
    window_id: str
    satellite_id: str
    target_or_station_id: str
    window_type: WindowType
    start_time_s: float
    end_time_s: float
    duration_s: float
    max_elevation_deg: float
    avg_range_km: float
    is_sunlit: bool


class CollisionAlert(BaseModel):
    sat_1_id: str
    sat_2_id: str
    tca_s: float = Field(..., description="Time of closest approach in simulation seconds")
    min_distance_km: float = Field(..., description="Predicted minimum distance at TCA")
    is_critical: bool = Field(False, description="True if distance < safety threshold (e.g. 25km)")


class CandidateEvaluation(BaseModel):
    satellite_id: str
    eligible: bool
    bid_score: float = 0.0
    projected_soc_after_mission: float = 1.0
    access_start_s: Optional[float] = None
    rejection_reason: Optional[str] = None


class DecisionExplanation(BaseModel):
    mission_id: str
    mission_name: str
    priority: int
    selected_satellite_id: Optional[str] = None
    assigned_window: Optional[AccessWindow] = None
    downlink_window: Optional[AccessWindow] = None
    downlink_station_id: Optional[str] = None
    selection_rationale: str
    candidates_evaluated: List[CandidateEvaluation] = []
    battery_margin_pct: float = 0.0
    binding_constraints: List[str] = []


class ScheduleDecision(BaseModel):
    tick: int
    sim_time_s: float
    assignments: List[DecisionExplanation] = []
    solver_status: str = "OPTIMAL"
    solver_time_ms: float = 0.0
    total_reward: float = 0.0


class ConstellationTick(BaseModel):
    tick: int
    sim_time_s: float
    wall_clock_iso: str
    speed_multiplier: float
    satellites: List[SatelliteState]
    ground_stations: List[GroundStation]
    active_missions: List[MissionRequest]
    pending_missions: List[MissionRequest]
    completed_missions: List[MissionRequest]
    recent_explanations: List[DecisionExplanation]
    collision_alerts: List[CollisionAlert]
    metrics_summary: Dict[str, Any]


class BenchmarkResult(BaseModel):
    scheduler_name: str
    seed: int
    num_missions: int
    completed_missions: int
    completion_rate_pct: float
    high_priority_completion_pct: float
    avg_deadline_slack_s: float
    avg_battery_reserve_pct: float
    ground_station_utilization_pct: float
    total_reward_yield: float
    avg_solve_time_ms: float
