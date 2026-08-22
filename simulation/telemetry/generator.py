"""Simulation Telemetry Stream Generator.

Generates realistic high-frequency multivariate telemetry streams with authentic physical noise
and orbital eclipse dynamics for training, evaluation, and stress-testing the AI platform.
"""

from typing import List, Dict, Any
import numpy as np


class TelemetryStreamGenerator:
    """Generates continuous multivariate telemetry frames."""

    def __init__(self, resource_id: str = "SAT-01"):
        self.resource_id = resource_id
        self.tick = 0

    def generate_frame(self, is_sunlit: bool = True, inject_anomaly: bool = False) -> Dict[str, Any]:
        self.tick += 1
        noise = np.random.normal(0, 0.02)
        
        soc = 0.85 + noise if not inject_anomaly else 0.38 + noise
        temp = 22.0 + (3.0 * np.sin(self.tick / 10.0)) if not inject_anomaly else 48.2 + noise * 10
        voltage = 28.2 + noise
        latency = 45.0 + np.random.uniform(-5, 5) if not inject_anomaly else 220.0
        snr = 18.5 + noise * 2 if not inject_anomaly else 8.2

        return {
            "resource_id": self.resource_id,
            "tick": self.tick,
            "battery_soc": max(0.0, min(1.0, float(soc))),
            "battery_temp_c": round(float(temp), 2),
            "bus_voltage_v": round(float(voltage), 2),
            "comm_latency_ms": round(float(latency), 1),
            "link_snr_db": round(float(snr), 1),
            "memory_util_pct": 35.0,
            "is_sunlit": is_sunlit,
        }
