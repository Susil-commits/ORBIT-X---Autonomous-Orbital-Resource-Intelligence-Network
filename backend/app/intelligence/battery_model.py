"""Battery Energy Intelligence & Lookahead Forecasting Model."""

from typing import List, Tuple, Optional
from app.core.schemas import BatteryState, AccessWindow, WindowType

BATTERY_CAPACITY_WH_DEFAULT = 800.0
SOLAR_HARVEST_POWER_W = 200.0
BUS_IDLE_POWER_W = 45.0
PAYLOAD_IMAGING_POWER_W = 180.0
DOWNLINK_TRANSMITTER_POWER_W = 90.0
MIN_SAFE_SOC_THRESHOLD = 0.20  # Hard 20% safety floor reserve


def compute_step_battery_update(
    current_soc: float,
    capacity_wh: float,
    dt_seconds: float,
    is_sunlit: bool,
    is_imaging: bool = False,
    is_downlinking: bool = False,
    solar_multiplier: float = 1.0,
    power_draw_multiplier: float = 1.0,
) -> Tuple[float, float, float]:
    """
    Computes single time-step battery State of Charge (SoC).
    Returns: (new_soc, current_draw_w, solar_gen_w)
    """
    solar_gen_w = (SOLAR_HARVEST_POWER_W * solar_multiplier) if is_sunlit else 0.0
    
    draw_w = BUS_IDLE_POWER_W
    if is_imaging:
        draw_w += PAYLOAD_IMAGING_POWER_W
    if is_downlinking:
        draw_w += DOWNLINK_TRANSMITTER_POWER_W
        
    draw_w *= power_draw_multiplier
    
    net_power_w = solar_gen_w - draw_w
    delta_wh = net_power_w * (dt_seconds / 3600.0)
    
    new_energy_wh = (current_soc * capacity_wh) + delta_wh
    new_energy_wh = max(0.0, min(capacity_wh, new_energy_wh))
    new_soc = new_energy_wh / capacity_wh
    
    return new_soc, draw_w, solar_gen_w


def forecast_battery_profile(
    initial_soc: float,
    capacity_wh: float,
    start_time_s: float,
    horizon_s: float,
    sunlit_schedule: List[Tuple[float, float, bool]],  # (start_s, end_s, is_sunlit)
    assigned_tasks: List[Tuple[float, float, WindowType]],  # (start_s, end_s, type)
    dt_seconds: float = 30.0,
    power_multiplier: float = 1.0,
) -> Tuple[float, List[Tuple[float, float]]]:
    """
    Forecasts battery SoC over a forward horizon.
    Returns: (minimum_projected_soc, time_series_of_soc)
    """
    soc = initial_soc
    min_soc = initial_soc
    profile = []
    
    num_steps = int(horizon_s / dt_seconds) + 1
    
    for step in range(num_steps):
        t = start_time_s + step * dt_seconds
        
        # Check sunlit state
        is_sun = True
        for s_start, s_end, sun_state in sunlit_schedule:
            if s_start <= t < s_end:
                is_sun = sun_state
                break
                
        # Check active tasks
        is_img = False
        is_dl = False
        for task_start, task_end, task_type in assigned_tasks:
            if task_start <= t < task_end:
                if task_type == WindowType.IMAGING:
                    is_img = True
                elif task_type == WindowType.DOWNLINK:
                    is_dl = True
                    
        soc, _, _ = compute_step_battery_update(
            current_soc=soc,
            capacity_wh=capacity_wh,
            dt_seconds=dt_seconds,
            is_sunlit=is_sun,
            is_imaging=is_img,
            is_downlinking=is_dl,
            power_draw_multiplier=power_multiplier,
        )
        
        min_soc = min(min_soc, soc)
        profile.append((t, soc))
        
    return min_soc, profile


def estimate_mission_energy_cost(duration_s: float, window_type: WindowType) -> float:
    """Estimates energy consumed in Watt-hours for a given operation duration."""
    if window_type == WindowType.IMAGING:
        p_extra = PAYLOAD_IMAGING_POWER_W
    elif window_type == WindowType.DOWNLINK:
        p_extra = DOWNLINK_TRANSMITTER_POWER_W
    else:
        p_extra = 0.0
        
    return (p_extra + BUS_IDLE_POWER_W) * (duration_s / 3600.0)
