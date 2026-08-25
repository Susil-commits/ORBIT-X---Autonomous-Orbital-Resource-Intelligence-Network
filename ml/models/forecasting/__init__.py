"""Forecasting Models for Spacecraft Telemetry and Resource Health.

Exports:
- LookaheadBatteryForecaster (Physics-informed lookahead SoC & thermal forecaster)
- LinearDecayForecaster (Linear extrapolation baseline)
"""

from ml.models.forecasting.battery_forecaster import LookaheadBatteryForecaster
from ml.models.forecasting.linear_forecaster import LinearDecayForecaster

__all__ = [
    "LookaheadBatteryForecaster",
    "LinearDecayForecaster",
]
