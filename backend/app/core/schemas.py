"""Pydantic v2 domain schemas for ORBIT-X with AI/ML, Real TLE, and Explainability extensions."""

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
    norad_id: Optional[int] = None
    data_source: str = "synthetic"  # "synthetic" | "celestrak_real"
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


class SensorType(str, Enum):
    OPTICAL_RGB = "OPTICAL_RGB"
    SAR_RADAR = "SAR_RADAR"
    THERMAL_IR = "THERMAL_IR"
    HYPERSPECTRAL = "HYPERSPECTRAL"


class ScenarioType(str, Enum):
    NOMINAL = "NOMINAL"
    SOLAR_STORM = "SOLAR_STORM"
    DEBRIS_CONJUNCTION = "DEBRIS_CONJUNCTION"
    GROUND_BLACKOUT = "GROUND_BLACKOUT"
    DISASTER_SURGE = "DISASTER_SURGE"
    SATELLITE_FAILURE = "SATELLITE_FAILURE"
    ISL_FAILURE = "ISL_FAILURE"
    BATTERY_DEGRADATION = "BATTERY_DEGRADATION"
    THERMAL_OVERLOAD = "THERMAL_OVERLOAD"
    STALE_TLE = "STALE_TLE"
    GPS_DEGRADATION = "GPS_DEGRADATION"



class ISLLink(BaseModel):
    sat_1_id: str
    sat_2_id: str
    distance_km: float
    latency_ms: float
    throughput_gbps: float = 10.0
    status: str = "ACTIVE"
    is_in_use: bool = False


class ISLRoute(BaseModel):
    source_sat_id: str
    target_gs_id: str
    hops: List[str]
    total_distance_km: float
    total_latency_ms: float
    bottleneck_throughput_gbps: float = 10.0


class ISLMeshState(BaseModel):
    active_links_count: int = 0
    max_links_possible: int = 0
    average_latency_ms: float = 0.0
    routes: List[ISLRoute] = []
    links: List[ISLLink] = []


class ScenarioState(BaseModel):
    scenario_type: ScenarioType = ScenarioType.NOMINAL
    title: str = "Nominal Constellation Baseline"
    description: str = "All satellite payloads, solar arrays, attitude controllers, and ground downlinks operating within nominal envelope."
    severity: str = "LOW"
    is_active: bool = False
    activated_at_s: float = 0.0
    elapsed_s: float = 0.0
    ai_actions_taken: List[str] = []
    debris_position: Optional[Position3D] = None
    affected_satellite_ids: List[str] = []


class TargetDispatchRequest(BaseModel):
    name: str = Field(..., description="Target or mission name")
    lat: float = Field(..., ge=-90.0, le=90.0, description="Latitude degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Longitude degrees")
    priority: int = Field(4, ge=1, le=5, description="Priority level (1-5)")
    sensor_type: SensorType = Field(SensorType.OPTICAL_RGB, description="Payload sensor required")
    data_size_gb: float = Field(15.0, description="Data volume generated (GB)")
    deadline_offset_s: float = Field(3600.0, description="Time until deadline (seconds)")


class ConjunctionManeuver(BaseModel):
    satellite_id: str
    debris_id: str
    burn_delta_v_mps: float
    execution_time_s: float
    pre_maneuver_miss_distance_km: float
    post_maneuver_miss_distance_km: float
    status: str = "COMPLETED"


class ConstellationTick(BaseModel):
    tick: int
    sim_time_s: float
    wall_clock_iso: str
    speed_multiplier: float
    data_source: str = "synthetic"  # "synthetic" | "celestrak_real"
    satellites: List[SatelliteState]
    ground_stations: List[GroundStation]
    active_missions: List[MissionRequest]
    pending_missions: List[MissionRequest]
    completed_missions: List[MissionRequest]
    recent_explanations: List[DecisionExplanation]
    collision_alerts: List[CollisionAlert]
    metrics_summary: Dict[str, Any]
    isl_mesh: Optional[ISLMeshState] = None
    active_scenario: Optional[ScenarioState] = None
    active_maneuvers: List[ConjunctionManeuver] = []


class BenchmarkResult(BaseModel):
    scheduler_name: str
    seed: int
    data_source: str = "synthetic"
    num_missions: int
    completed_missions: int
    completion_rate_pct: float
    high_priority_completion_pct: float
    avg_deadline_slack_s: float
    avg_battery_reserve_pct: float
    ground_station_utilization_pct: float
    total_reward_yield: float
    avg_solve_time_ms: float
    constraint_violations: int = 0
    neural_regret: float = 0.0
    objective_value: float = 0.0



# ==========================================
# Neural Network & TreeSHAP Schemas
# ==========================================

class FeatureAttribution(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float
    contribution_direction: str  # "POSITIVE" | "NEGATIVE"
    description: str


class BidValuationExplanation(BaseModel):
    predicted_bid_score: float
    base_value: float
    is_distilled: bool = True
    model_hash: str
    drift_detected: bool = False
    feature_attributions: List[FeatureAttribution] = []


class NeuralBidPreviewRequest(BaseModel):
    satellite_id: str
    priority: int = 4
    battery_soc: float = 0.85
    max_elevation_deg: float = 65.0
    slew_penalty: float = 0.0
    health_status: str = "NOMINAL"
    storage_headroom: float = 0.90
    is_sunlit: bool = True
    deadline_slack_ratio: float = 0.80
    energy_cost_ratio: float = 0.02
    duration_s_ratio: float = 0.50


class NeuralBidPreviewResponse(BaseModel):
    satellite_id: str
    predicted_bid_score: float
    cpsat_agreement_prob: float
    explanation: BidValuationExplanation


# ==========================================
# RAG & LLM Commentary Schemas
# ==========================================

class Citation(BaseModel):
    record_id: str
    tick: int
    sim_time_s: float
    event_type: str
    summary: str
    relevance_score: float


class MissionQARequest(BaseModel):
    query: str
    top_k: int = 5


class MissionQAResponse(BaseModel):
    query: str
    answer: str
    grounded: bool
    confidence_score: float
    citations: List[Citation] = []
    retrieved_records_count: int = 0


class FlightDirectorCommentary(BaseModel):
    commentary: str
    event_type: str
    sim_time_s: float
    model_used: str  # e.g., "ollama:llama3.2" or "deterministic_template"
    verified_factual: bool = True


# ==========================================
# Eval Harness & Agent Loop Schemas
# ==========================================

class EvalMetric(BaseModel):
    metric_name: str
    baseline_value: float
    current_value: float
    delta: float
    status: str  # "PASS" | "WARN" | "FAIL"
    threshold: float


class EvalRunSummary(BaseModel):
    run_id: str
    timestamp_iso: str
    overall_status: str  # "PASS" | "REGRESSION_DETECTED"
    metrics: List[EvalMetric] = []
    regressions: List[str] = []


class AgentHealingAction(BaseModel):
    action_type: str
    triggered_by: str
    status: str
    details: str
    timestamp_iso: str


# ==========================================
# Next-Gen AI & Modern Multi-Task Schemas
# ==========================================

class CrossAttentionPredictionRequest(BaseModel):
    satellite_id: str
    mission_id: Optional[str] = None
    priority: int = 4
    battery_soc: float = 0.85
    max_elevation_deg: float = 65.0
    slew_penalty: float = 0.0
    health_status: str = "NOMINAL"
    storage_headroom: float = 0.90
    is_sunlit: bool = True
    deadline_slack_ratio: float = 0.80
    energy_cost_ratio: float = 0.02
    duration_s_ratio: float = 0.50
    cloud_cover_prob: float = 0.10
    solar_flux_index: float = 1.0


class MultiTaskPrediction(BaseModel):
    valuation_score: float = Field(..., description="Continuous CP-SAT valuation score [0, 100]")
    win_probability: float = Field(..., description="Probability of winning assignment [0.0, 1.0]")
    estimated_latency_s: float = Field(..., description="Estimated end-to-end ISL/downlink latency in seconds")
    estimated_energy_wh: float = Field(..., description="Projected energy consumption in Watt-hours")


class AttentionWeightEntry(BaseModel):
    source_feature: str
    target_feature: str
    weight: float


class CrossAttentionPredictionResponse(BaseModel):
    satellite_id: str
    mission_id: Optional[str] = None
    predictions: MultiTaskPrediction
    attention_matrix: List[List[float]] = []
    satellite_feature_names: List[str] = []
    mission_feature_names: List[str] = []
    top_attended_features: List[AttentionWeightEntry] = []
    model_architecture: str
    inference_time_ms: float


class FineTuningMetricHistory(BaseModel):
    epoch: int
    train_loss: float
    val_loss: float
    top1_agreement_pct: float
    mae: float
    r2_score: float
    learning_rate: float


class FineTuningStatusResponse(BaseModel):
    is_training: bool
    current_epoch: int
    total_epochs: int
    active_model_name: str
    model_hash: str
    dataset_sample_count: int
    latest_metrics: Dict[str, float] = {}
    loss_history: List[FineTuningMetricHistory] = []
    last_trained_utc: Optional[str] = None
    scheduler_type: str = "CosineAnnealingWarmRestarts"


class FineTuningTriggerRequest(BaseModel):
    epochs: int = 40
    batch_size: int = 32
    learning_rate: float = 0.0015
    num_scenarios: int = 60
    missions_per_scenario: int = 5
    augment_geomagnetic: bool = True
    augment_cloud_cover: bool = True


class FineTuningTriggerResponse(BaseModel):
    status: str
    message: str
    epochs_requested: int
    dataset_size: int
    model_path: str


class PINNBatteryThermalRequest(BaseModel):
    initial_soc: float = 0.85
    battery_temp_c: float = 20.0
    payload_active: bool = False
    is_sunlit: bool = True
    solar_flux_w_m2: float = 1361.0
    duration_minutes: float = 90.0
    time_step_s: float = 30.0


class PINNTrajectoryPoint(BaseModel):
    time_min: float
    soc: float
    battery_temp_c: float
    solar_power_w: float
    thermal_radiation_w: float
    degradation_rate: float


class PINNBatteryThermalResponse(BaseModel):
    duration_minutes: float
    min_projected_soc: float
    max_projected_temp_c: float
    final_soc: float
    final_temp_c: float
    trajectory: List[PINNTrajectoryPoint]
    physics_residual_norm: float
    confidence_score: float


class HybridMissionQARequest(BaseModel):
    query: str
    top_k: int = 5
    satellite_filter: Optional[str] = None
    min_severity: Optional[str] = None  # "ALL", "NOMINAL", "DEGRADED", "CRITICAL_FAULT"
    dense_weight: float = 0.6
    bm25_weight: float = 0.4


# ====================================================
# Layer 1 & Layer 4: Context Layer, Metadata & Lineage
# ====================================================

class DataCatalogColumn(BaseModel):
    name: str
    type: str
    description: str


class DataCatalogEntry(BaseModel):
    dataset_name: str
    owner: str
    description: str
    schema_version: str
    storage_format: str
    freshness_seconds: float
    quality_score: float
    sensitivity: str
    status: str = "VERIFIED"  # "VERIFIED", "DRAFT", "DEPRECATED"
    last_reviewed: str = "2026-08-22T12:00:00Z"
    certification_badge: str = "CERTIFIED_GOLD"
    governance_policy: Optional[str] = "Production agent decisions require VERIFIED assets only."
    columns: List[DataCatalogColumn]
    downstream_consumers: List[str]


class ContextQualityMetrics(BaseModel):
    metadata_completeness_pct: float
    lineage_coverage_pct: float
    freshness_sla_compliance_pct: float
    overall_quality_score_pct: float
    quality_score_pct: float
    verified_asset_ratio_pct: float
    retrieval_groundedness_pct: float
    metadata_completeness: float
    lineage_coverage: float
    freshness_sla_compliance: float
    quality_score: float
    verified_asset_ratio: float
    retrieval_groundedness: float
    total_assets: int
    verified_assets: int
    draft_assets: int
    deprecated_assets: int
    evaluated_at_iso: str


class GovernedContextStep(BaseModel):
    step_number: int
    step_name: str  # "discover_context", "identify_authoritative_dataset", "check_quality_freshness", "inspect_lineage", "retrieve_data", "reason"
    status: str = "COMPLETED"
    summary: str
    target_asset: Optional[str] = None
    evidence_collected: Optional[str] = None


class DataCatalogResponse(BaseModel):
    catalog_version: str
    total_datasets: int
    verified_count: int = 0
    draft_count: int = 0
    deprecated_count: int = 0
    context_quality: Optional[ContextQualityMetrics] = None
    datasets: List[DataCatalogEntry]


class DataLineageNode(BaseModel):
    id: str
    label: str
    type: str  # "SOURCE_TELEMETRY", "DATASET", "FEATURE_TABLE", "ML_MODEL", "OPTIMIZER", "DECISION", "OUTCOME"
    metadata: Dict[str, Any] = {}


class DataLineageEdge(BaseModel):
    source: str
    target: str
    relationship: str  # "INCORPORATES", "TRANSFORMS_INTO", "FEEDS_INTO", "PRODUCES", "VALIDATES"


class DataLineageResponse(BaseModel):
    target_id: str
    nodes: List[DataLineageNode]
    edges: List[DataLineageEdge]
    lineage_path_summary: str


class DataQualityAlert(BaseModel):
    severity: str  # "INFO", "WARNING", "CRITICAL"
    column: Optional[str] = None
    alert_type: str  # "MISSING_VALUES", "SCHEMA_DRIFT", "DISTRIBUTION_DRIFT", "STALE_DATA"
    message: str
    impact: str
    recommended_action: str


class DataQualityReport(BaseModel):
    dataset_name: str
    timestamp_iso: str
    total_records_checked: int
    overall_quality_score: float
    is_nominal: bool
    alerts: List[DataQualityAlert]
    metrics: Dict[str, Any] = {}


# ====================================================
# Layer 2: Baseline Models & Feature Ablation
# ====================================================

class BaselineModelScore(BaseModel):
    model_name: str
    model_category: str  # "HEURISTIC", "CLASSICAL_ML", "DEEP_LEARNING"
    top1_agreement_pct: float
    mae: float
    accuracy_pct: float
    f1_score: float
    latency_ms_p50: float
    latency_ms_p95: float
    throughput_inferences_sec: float
    description: str


class DecisionSystemScore(BaseModel):
    system_name: str
    system_category: str = "DECISION_SYSTEM"  # "NEURAL_ONLY", "HYBRID_EXACT"
    constraint_violations: str  # e.g., "3.4% boundary violations" or "0 (Modeled Invariants Enforced)"
    feasibility_rate_pct: float  # e.g., 96.6% vs 100.0%
    decision_utility_pct: float  # e.g., 84.5% vs 98.7%
    high_priority_completion_pct: float = 100.0  # e.g., 88.2% vs 100.0%
    optimization_latency_ms_p50: Optional[float] = None  # None/0.0 for pure ML, ~18.4ms for CP-SAT
    end_to_end_latency_ms_p50: float  # e.g., 0.372ms vs 18.77ms
    description: str


class BaselineComparisonReport(BaseModel):
    timestamp_iso: str
    total_test_samples: int
    evaluated_missions: int
    ml_models: List[BaselineModelScore] = []
    decision_systems: List[DecisionSystemScore] = []
    models: List[BaselineModelScore] = []  # For backward-compatible API consumers
    champion_ml_model: str = "ConstellationCrossAttentionNet"
    champion_decision_system: str = "Cross-Attention + Google OR-Tools CP-SAT"
    champion_model: str = "Hybrid Neural + CP-SAT"
    selection_rationale: str


class FeatureAblationEntry(BaseModel):
    ablation_name: str
    removed_features: List[str]
    remaining_feature_count: int
    top1_agreement_pct: float
    mae: float
    performance_delta_pct: float
    interpretation: str


class FeatureAblationReport(BaseModel):
    timestamp_iso: str
    baseline_top1_pct: float
    ablations: List[FeatureAblationEntry]
    key_findings: List[str]


# ====================================================
# Layer 4: Trust Layer, Audit Trail & Human-in-the-Loop
# ====================================================

class TrustEvidenceItem(BaseModel):
    evidence_type: str  # "TELEMETRY", "MISSION_METADATA", "MODEL_PREDICTION", "SHAP_XAI", "OPTIMIZER_RESULT", "LINEAGE"
    source_id: str
    summary: str
    verified: bool = True
    confidence_contribution: float = 0.0


class TrustLayerResponse(BaseModel):
    query: str
    decision_id: str = ""
    mission_id: Optional[str] = None
    risk_level: Optional[str] = None
    risk_reasons: List[str] = []
    answer: str
    recommendation: Optional[str] = None
    target_resource: Optional[str] = None
    confidence_score: float
    confidence_level: str  # "HIGH", "MEDIUM", "LOW"
    grounded: bool
    constraints_checked: List[Dict[str, Any]] = []
    evidence: List[TrustEvidenceItem]
    citations: List[Citation]
    tools_used: List[str]
    source_records: List[str] = []
    lineage_summary: Optional[str] = None
    governed_context_steps: List[GovernedContextStep] = []
    context_quality: Optional[ContextQualityMetrics] = None
    requires_human_review: bool = False
    recommended_action: Optional[str] = None
    available_actions: List[str] = ["APPROVE", "REJECT", "INVESTIGATE"]


class HumanFeedbackRequest(BaseModel):
    decision_record_id: str
    mission_id: Optional[str] = None
    feedback_type: str  # "APPROVE", "REJECT", "INVESTIGATE"
    operator_notes: Optional[str] = None
    suggested_alternative_satellite: Optional[str] = None


class HumanFeedbackResponse(BaseModel):
    feedback_id: str
    status: str
    message: str
    recorded_at_iso: str


