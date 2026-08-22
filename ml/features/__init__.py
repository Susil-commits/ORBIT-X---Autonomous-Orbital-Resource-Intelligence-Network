"""ML Feature Engineering Layer for Resource Allocation and Neural Ranking."""

import importlib
from typing import Dict, Any, Tuple, List, Optional

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    pass

def build_neural_ranking_input(resource_state: Dict[str, Any], task_req: Dict[str, Any]) -> Tuple[Any, Any]:
    """Encodes resource state (6-dim) and request requirements (7-dim) for Cross-Attention."""
    res_list = [
        float(resource_state.get("battery_soc", 0.85)),
        float(resource_state.get("battery_temp_c", 20.0)),
        float(resource_state.get("bus_voltage_v", 28.0)),
        float(resource_state.get("available_storage_gb", 200.0)),
        float(resource_state.get("reaction_wheel_jitter", 0.02)),
        float(resource_state.get("rf_snr_db", 18.0)),
    ]

    req_list = [
        float(task_req.get("priority", 3)),
        float(task_req.get("max_elevation_deg", 65.0)),
        float(task_req.get("pass_duration_s", 300.0)),
        float(task_req.get("slew_angle_deg", 12.0)),
        float(task_req.get("deadline_slack_s", 1800.0)),
        float(task_req.get("reward_value", 150.0)),
        float(task_req.get("isl_hop_count", 2)),
    ]

    if np is not None:
        return np.array(res_list, dtype=np.float32), np.array(req_list, dtype=np.float32)
    return res_list, req_list
