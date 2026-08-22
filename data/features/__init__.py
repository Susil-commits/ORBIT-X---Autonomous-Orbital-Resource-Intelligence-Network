"""Feature store definitions and 13-dimensional kinematic/thermal feature vectors."""

FEATURE_VECTOR_NAMES = [
    "battery_soc",
    "battery_temp_c",
    "bus_voltage_v",
    "available_storage_gb",
    "reaction_wheel_jitter",
    "rf_snr_db",
    "max_elevation_deg",
    "pass_duration_s",
    "slew_angle_deg",
    "mission_priority",
    "deadline_slack_s",
    "reward_value",
    "isl_hop_count",
]

__all__ = ["FEATURE_VECTOR_NAMES"]
