"""Linear Trend Extrapolation Forecaster Baseline.

Simple linear extrapolation baseline for battery SoC and telemetry trends.
"""

from typing import Dict, Any, List, Optional
import numpy as np


class LinearDecayForecaster:
    """Linear trend extrapolation forecaster baseline."""

    def __init__(self, default_decay_rate_per_min: float = 0.003):
        self.model_id = "orbitx-forecasting-linear-decay-v1"
        self.version = "1.0.0"
        self.default_decay_rate_per_min = default_decay_rate_per_min

    def forecast_trajectory(
        self,
        current_soc: float,
        horizon_steps: int = 60,
        step_duration_s: float = 60.0,
        decay_rate_per_min: Optional[float] = None,
    ) -> Dict[str, Any]:
        rate = decay_rate_per_min if decay_rate_per_min is not None else self.default_decay_rate_per_min
        soc_profile = [
            float(round(np.clip(current_soc - (step * (step_duration_s / 60.0) * rate), 0.0, 1.0), 4))
            for step in range(horizon_steps + 1)
        ]
        return {
            "forecast_horizon_s": horizon_steps * step_duration_s,
            "min_projected_soc": min(soc_profile),
            "soc_profile": soc_profile,
            "mean_soc_forecast": round(float(np.mean(soc_profile)), 4),
        }
