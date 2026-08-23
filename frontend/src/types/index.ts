export type HealthStatus = 'NOMINAL' | 'DEGRADED' | 'CRITICAL_FAULT';
export type MissionStatus = 'PENDING' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
export type WindowType = 'IMAGING' | 'DOWNLINK';
export type SensorType = 'OPTICAL_RGB' | 'SAR_RADAR' | 'THERMAL_IR' | 'HYPERSPECTRAL';
export type ScenarioType =
  | 'NOMINAL'
  | 'SOLAR_STORM'
  | 'DEBRIS_CONJUNCTION'
  | 'GROUND_BLACKOUT'
  | 'DISASTER_SURGE'
  | 'SATELLITE_FAILURE'
  | 'ISL_FAILURE'
  | 'BATTERY_DEGRADATION'
  | 'THERMAL_OVERLOAD'
  | 'STALE_TLE'
  | 'GPS_DEGRADATION';


export interface Position3D {
  x: number;
  y: number;
  z: number;
}

export interface GeodeticLocation {
  lat: number;
  lon: number;
  alt: number;
}

export interface KeplerianElements {
  semi_major_axis_km: number;
  eccentricity: number;
  inclination_deg: number;
  raan_deg: number;
  arg_perigee_deg: number;
  mean_anomaly_deg: number;
  epoch_time_s: number;
}

export interface TelemetryFrame {
  timestamp_s: number;
  bus_voltage_v: number;
  solar_current_a: number;
  battery_temp_c: number;
  payload_temp_c: number;
  reaction_wheel_jitter_dps: number;
  rf_snr_db: number;
  anomaly_score: number;
  health_status: HealthStatus;
}

export interface BatteryState {
  soc: number;
  capacity_wh: number;
  current_draw_w: number;
  solar_generation_w: number;
  is_sunlit: boolean;
  projected_min_soc: number;
}

export interface SatelliteState {
  id: string;
  name: string;
  norad_id?: number | null;
  data_source?: 'synthetic' | 'celestrak_real' | string;
  orbit_plane: number;
  keplerian: KeplerianElements;
  position_eci: Position3D;
  position_ecef: Position3D;
  geodetic: GeodeticLocation;
  velocity_kms: number;
  battery: BatteryState;
  telemetry: TelemetryFrame;
  onboard_storage_used_gb: number;
  max_storage_gb: number;
  active_mission_id?: string | null;
  active_task_type?: string | null;
  active_target_name?: string | null;
  health_status: HealthStatus;
}

export interface GroundStation {
  id: string;
  name: string;
  location: GeodeticLocation;
  min_elevation_deg: number;
  bandwidth_gbps: number;
  is_active: boolean;
}

export interface MissionRequest {
  id: string;
  name: string;
  target_location: GeodeticLocation;
  priority: number;
  reward: number;
  deadline_s: number;
  duration_s: number;
  data_size_gb: number;
  energy_cost_wh: number;
  status: MissionStatus;
  assigned_satellite_id?: string | null;
  imaging_start_s?: number | null;
  imaging_end_s?: number | null;
  downlink_ground_station_id?: string | null;
  downlink_start_s?: number | null;
  downlink_end_s?: number | null;
  created_at_s: number;
  completed_at_s?: number | null;
}

export interface AccessWindow {
  window_id: string;
  satellite_id: string;
  target_or_station_id: string;
  window_type: WindowType;
  start_time_s: number;
  end_time_s: number;
  duration_s: number;
  max_elevation_deg: number;
  avg_range_km: number;
  is_sunlit: boolean;
}

export interface CollisionAlert {
  sat_1_id: string;
  sat_2_id: string;
  tca_s: number;
  min_distance_km: number;
  is_critical: boolean;
}

export interface CandidateEvaluation {
  satellite_id: string;
  eligible: boolean;
  bid_score: number;
  projected_soc_after_mission: number;
  access_start_s?: number | null;
  rejection_reason?: string | null;
}

export interface DecisionExplanation {
  mission_id: string;
  mission_name: string;
  priority: number;
  selected_satellite_id?: string | null;
  assigned_window?: AccessWindow | null;
  downlink_window?: AccessWindow | null;
  downlink_station_id?: string | null;
  selection_rationale: string;
  candidates_evaluated: CandidateEvaluation[];
  battery_margin_pct: number;
  binding_constraints: string[];
}

export interface ISLLink {
  sat_1_id: string;
  sat_2_id: string;
  distance_km: number;
  latency_ms: number;
  throughput_gbps: number;
  status: 'ACTIVE' | 'OCCLUDED' | 'OUT_OF_RANGE' | string;
  is_in_use: boolean;
}

export interface ISLRoute {
  source_sat_id: string;
  target_gs_id: string;
  hops: string[];
  total_distance_km: number;
  total_latency_ms: number;
  bottleneck_throughput_gbps: number;
}

export interface ISLMeshState {
  active_links_count: number;
  max_links_possible: number;
  average_latency_ms: number;
  routes: ISLRoute[];
  links: ISLLink[];
}

export interface ScenarioState {
  scenario_type: ScenarioType;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | string;
  is_active: boolean;
  activated_at_s: number;
  elapsed_s: number;
  ai_actions_taken: string[];
  debris_position?: Position3D | null;
  affected_satellite_ids: string[];
}

export interface TargetDispatchRequest {
  name: string;
  lat: number;
  lon: number;
  priority: number;
  sensor_type: SensorType;
  data_size_gb: number;
  deadline_offset_s: number;
}

export interface ConjunctionManeuver {
  satellite_id: string;
  debris_id: string;
  burn_delta_v_mps: number;
  execution_time_s: number;
  pre_maneuver_miss_distance_km: number;
  post_maneuver_miss_distance_km: number;
  status: string;
}

export interface ConstellationTick {
  tick: number;
  sim_time_s: number;
  wall_clock_iso: string;
  speed_multiplier: number;
  data_source?: 'synthetic' | 'celestrak_real' | string;
  satellites: SatelliteState[];
  ground_stations: GroundStation[];
  active_missions: MissionRequest[];
  pending_missions: MissionRequest[];
  completed_missions: MissionRequest[];
  recent_explanations: DecisionExplanation[];
  collision_alerts: CollisionAlert[];
  metrics_summary: Record<string, any>;
  isl_mesh?: ISLMeshState | null;
  active_scenario?: ScenarioState | null;
  active_maneuvers?: ConjunctionManeuver[];
}

export interface BenchmarkResult {
  scheduler_name: string;
  seed: number;
  data_source?: string;
  num_missions: number;
  completed_missions: number;
  completion_rate_pct: number;
  high_priority_completion_pct: number;
  avg_deadline_slack_s: number;
  avg_battery_reserve_pct: number;
  ground_station_utilization_pct: number;
  total_reward_yield: number;
  avg_solve_time_ms: number;
  constraint_violations?: number;
  neural_regret?: number;
  objective_value?: number;
}


export interface AgentBid {
  satellite_id: string;
  satellite_name: string;
  mission_id: string;
  imaging_window: AccessWindow;
  bid_value: number;
  battery_cost_wh: number;
  marginal_soc_remaining: number;
  slew_penalty: number;
  health_discount: number;
}

export interface AuctionResult {
  mission_id: string;
  winning_satellite_id?: string | null;
  winning_bid_value: number;
  winning_window?: AccessWindow | null;
  all_bids: AgentBid[];
  conflict_resolved: boolean;
  rationale: string;
}

// ----------------------------------------------------
// New AI, Neural, TreeSHAP & RAG Types
// ----------------------------------------------------

export interface FeatureAttribution {
  feature_name: string;
  feature_value: number;
  shap_value: number;
  contribution_direction: 'POSITIVE' | 'NEGATIVE';
  description: string;
}

export interface TreeSHAPExplanation {
  predicted_bid_score: number;
  base_value: number;
  is_distilled: boolean;
  feature_attributions: FeatureAttribution[];
}

export interface NeuralBidPreviewResponse {
  satellite_id: string;
  predicted_bid_score: number;
  cpsat_agreement_prob: number;
  explanation: TreeSHAPExplanation;
}

export interface MissionCitation {
  record_id: string;
  tick: number;
  sim_time_s: number;
  event_type: string;
  summary: string;
  relevance_score: number;
}

export interface MissionQAResponse {
  query: string;
  answer: string;
  grounded: boolean;
  confidence_score: number;
  citations: MissionCitation[];
  retrieved_records_count: number;
}

export interface FlightDirectorCommentary {
  commentary: string;
  event_type: string;
  sim_time_s: number;
  model_used: string;
  verified_factual: boolean;
}

export interface AgentHealingAction {
  action_type: string;
  triggered_by: string;
  status: string;
  details: string;
  timestamp_iso: string;
}

// ----------------------------------------------------
// Next-Gen Cross-Attention, Multi-Task & Battery/Thermal ODE Types
// ----------------------------------------------------

export interface CrossAttentionPredictionRequest {
  satellite_id: string;
  mission_id?: string;
  priority: number;
  battery_soc: number;
  max_elevation_deg: number;
  slew_penalty: number;
  health_status: string;
  storage_headroom: number;
  is_sunlit: boolean;
  deadline_slack_ratio: number;
  energy_cost_ratio: number;
  duration_s_ratio: number;
  cloud_cover_prob: number;
  solar_flux_index: number;
}

export interface MultiTaskPrediction {
  valuation_score: number;
  win_probability: number;
  estimated_latency_s: number;
  estimated_energy_wh: number;
}

export interface AttentionWeightEntry {
  source_feature: string;
  target_feature: string;
  weight: number;
}

export interface CrossAttentionPredictionResponse {
  satellite_id: string;
  mission_id?: string;
  predictions: MultiTaskPrediction;
  attention_matrix: number[][];
  satellite_feature_names: string[];
  mission_feature_names: string[];
  top_attended_features: AttentionWeightEntry[];
  model_architecture: string;
  inference_time_ms: number;
}

export interface FineTuningMetricHistory {
  epoch: number;
  train_loss: number;
  val_loss: number;
  top1_agreement_pct: number;
  mae: number;
  r2_score: number;
  learning_rate: number;
}

export interface FineTuningStatusResponse {
  is_training: boolean;
  current_epoch: number;
  total_epochs: number;
  active_model_name: string;
  model_hash: string;
  dataset_sample_count: number;
  latest_metrics: Record<string, number>;
  loss_history: FineTuningMetricHistory[];
  last_trained_utc?: string;
  scheduler_type: string;
}

export interface FineTuningTriggerRequest {
  epochs: number;
  batch_size: number;
  learning_rate: number;
  num_scenarios: number;
  missions_per_scenario: number;
  augment_geomagnetic: boolean;
  augment_cloud_cover: boolean;
}

export interface FineTuningTriggerResponse {
  status: string;
  message: string;
  epochs_requested: number;
  dataset_size: number;
  model_path: string;
}

export interface PINNBatteryThermalRequest {
  initial_soc: number;
  battery_temp_c: number;
  payload_active: boolean;
  is_sunlit: boolean;
  solar_flux_w_m2: number;
  duration_minutes: number;
  time_step_s: number;
}

export interface PINNTrajectoryPoint {
  time_min: number;
  soc: number;
  battery_temp_c: number;
  solar_power_w: number;
  thermal_radiation_w: number;
  degradation_rate: number;
}

export interface PINNBatteryThermalResponse {
  duration_minutes: number;
  min_projected_soc: number;
  max_projected_temp_c: number;
  final_soc: number;
  final_temp_c: number;
  trajectory: PINNTrajectoryPoint[];
  physics_residual_norm: number;
  confidence_score: number;
}

// Clean semantic type aliases
export type BatteryThermalRequest = PINNBatteryThermalRequest;
export type BatteryThermalTrajectoryPoint = PINNTrajectoryPoint;
export type BatteryThermalResponse = PINNBatteryThermalResponse;

export interface HybridMissionQARequest {
  query: string;
  top_k?: number;
  satellite_filter?: string;
  min_severity?: string;
  dense_weight?: number;
  bm25_weight?: number;
}

// ====================================================
// Context Layer & Semantic Metadata Catalog
// ====================================================

export interface DataCatalogColumn {
  name: string;
  type: string;
  description: string;
}

export interface DataCatalogEntry {
  dataset_name: string;
  owner: string;
  description: string;
  schema_version: string;
  storage_format: string;
  freshness_seconds: number;
  quality_score: number;
  sensitivity: string;
  status: 'VERIFIED' | 'DRAFT' | 'DEPRECATED' | string;
  last_reviewed?: string;
  certification_badge?: string;
  governance_policy?: string;
  columns: DataCatalogColumn[];
  downstream_consumers: string[];
}

export interface ContextQualityMetrics {
  metadata_completeness_pct: number;
  lineage_coverage_pct: number;
  freshness_sla_compliance_pct: number;
  overall_quality_score_pct: number;
  quality_score_pct?: number;
  verified_asset_ratio_pct: number;
  retrieval_groundedness_pct: number;
  metadata_completeness: number;
  lineage_coverage: number;
  freshness_sla_compliance: number;
  quality_score: number;
  verified_asset_ratio: number;
  retrieval_groundedness: number;
  total_assets: number;
  verified_assets: number;
  draft_assets: number;
  deprecated_assets: number;
  evaluated_at_iso: string;
}

export interface GovernedContextStep {
  step_number: number;
  step_name: string;
  status: string;
  summary: string;
  target_asset?: string | null;
  evidence_collected?: string | null;
}

export interface DataCatalogResponse {
  catalog_version: string;
  total_datasets: number;
  verified_count?: number;
  draft_count?: number;
  deprecated_count?: number;
  context_quality?: ContextQualityMetrics;
  datasets: DataCatalogEntry[];
}

export interface DataLineageNode {
  id: string;
  label: string;
  type: 'SOURCE_TELEMETRY' | 'DATASET' | 'FEATURE_TABLE' | 'ML_MODEL' | 'OPTIMIZER' | 'DECISION' | 'OUTCOME' | string;
  metadata?: Record<string, any>;
}

export interface DataLineageEdge {
  source: string;
  target: string;
  relationship: string;
}

export interface DataLineageResponse {
  target_id: string;
  nodes: DataLineageNode[];
  edges: DataLineageEdge[];
  lineage_path_summary: string;
}

export interface DataQualityAlert {
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  column?: string | null;
  alert_type: string;
  message: string;
  impact: string;
  recommended_action: string;
}

export interface DataQualityReport {
  dataset_name: string;
  timestamp_iso: string;
  total_records_checked: number;
  overall_quality_score: number;
  is_nominal: boolean;
  alerts: DataQualityAlert[];
  metrics: Record<string, any>;
}

// ====================================================
// ML Baselines & Feature Ablation
// ====================================================

export interface BaselineModelScore {
  model_name: string;
  model_category: 'HEURISTIC' | 'CLASSICAL_ML' | 'DEEP_LEARNING' | string;
  top1_agreement_pct: number;
  mae: number;
  accuracy_pct: number;
  f1_score: number;
  latency_ms_p50: number;
  latency_ms_p95: number;
  throughput_inferences_sec: number;
  description: string;
}

export interface DecisionSystemScore {
  system_name: string;
  system_category: 'NEURAL_ONLY' | 'HYBRID_EXACT' | string;
  constraint_violations: string;
  feasibility_rate_pct: number;
  decision_utility_pct: number;
  high_priority_completion_pct?: number;
  optimization_latency_ms_p50?: number | null;
  end_to_end_latency_ms_p50: number;
  description: string;
}

export interface BaselineComparisonReport {
  timestamp_iso: string;
  total_test_samples: number;
  evaluated_missions: number;
  ml_models: BaselineModelScore[];
  decision_systems: DecisionSystemScore[];
  models?: BaselineModelScore[];
  champion_ml_model?: string;
  champion_decision_system?: string;
  champion_model: string;
  selection_rationale: string;
}

export interface FeatureAblationEntry {
  ablation_name: string;
  removed_features: string[];
  remaining_feature_count: number;
  top1_agreement_pct: number;
  mae: number;
  performance_delta_pct: number;
  interpretation: string;
}

export interface FeatureAblationReport {
  timestamp_iso: string;
  baseline_top1_pct: number;
  ablations: FeatureAblationEntry[];
  key_findings: string[];
}

// ====================================================
// Trust Layer, Audit Trail & Human Feedback
// ====================================================

export interface Citation {
  record_id: string;
  sim_time_s: number;
  event_type: string;
  summary: string;
  relevance_score: number;
}

export interface TrustEvidenceItem {
  evidence_type: string;
  source_id: string;
  summary: string;
  verified: boolean;
  confidence_contribution: number;
}

export interface TrustLayerResponse {
  query: string;
  answer: string;
  confidence_score: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  grounded: boolean;
  evidence: TrustEvidenceItem[];
  citations: Citation[];
  tools_used: string[];
  lineage_summary?: string | null;
  governed_context_steps?: GovernedContextStep[];
  context_quality?: ContextQualityMetrics;
  requires_human_review: boolean;
  recommended_action?: string | null;
}

export interface HumanFeedbackRequest {
  decision_record_id: string;
  mission_id?: string | null;
  feedback_type: 'APPROVE' | 'REJECT' | 'INVESTIGATE';
  operator_notes?: string | null;
  suggested_alternative_satellite?: string | null;
}

export interface HumanFeedbackResponse {
  feedback_id: string;
  status: string;
  message: string;
  recorded_at_iso: string;
}


