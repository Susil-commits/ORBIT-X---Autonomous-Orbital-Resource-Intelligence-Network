export type HealthStatus = 'NOMINAL' | 'DEGRADED' | 'CRITICAL_FAULT';
export type MissionStatus = 'PENDING' | 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
export type WindowType = 'IMAGING' | 'DOWNLINK';

export interface Position3D {
  x: float;
  y: float;
  z: float;
}

export type float = number;

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

export interface ConstellationTick {
  tick: number;
  sim_time_s: number;
  wall_clock_iso: string;
  speed_multiplier: number;
  satellites: SatelliteState[];
  ground_stations: GroundStation[];
  active_missions: MissionRequest[];
  pending_missions: MissionRequest[];
  completed_missions: MissionRequest[];
  recent_explanations: DecisionExplanation[];
  collision_alerts: CollisionAlert[];
  metrics_summary: Record<string, any>;
}

export interface BenchmarkResult {
  scheduler_name: string;
  seed: number;
  num_missions: number;
  completed_missions: number;
  completion_rate_pct: number;
  high_priority_completion_pct: number;
  avg_deadline_slack_s: number;
  avg_battery_reserve_pct: number;
  ground_station_utilization_pct: number;
  total_reward_yield: number;
  avg_solve_time_ms: number;
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
