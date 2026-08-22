"""ORBIT-X Data Processing Pipeline.

Formalizes the transformation from raw simulation / telemetry feeds into validated,
cleaned, and feature-engineered datasets ready for ML training and real-time inference:

Raw Data -> Validation -> Cleaning -> Feature Engineering -> Processed Dataset -> ML
"""

import math
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from pydantic import ValidationError

from data.schemas.entities import Telemetry, MissionRequest


class DataProcessingPipeline:
    """End-to-end data validation, imputation, and feature extraction pipeline."""

    FEATURE_NAMES = [
        "battery_soc",
        "battery_temp_norm",
        "bus_voltage_norm",
        "comm_latency_norm",
        "link_snr_norm",
        "memory_util_norm",
        "is_sunlit_flag",
        "priority_norm",
        "duration_norm",
        "elevation_norm",
        "deadline_slack_ratio",
        "energy_cost_ratio",
        "slew_penalty_norm",
    ]

    def __init__(self):
        # Normalization reference bounds
        self.temp_min, self.temp_max = -20.0, 60.0
        self.voltage_nominal = 28.0
        self.latency_max = 300.0
        self.snr_min, self.snr_max = 0.0, 30.0
        self.max_duration = 600.0

    def validate_telemetry(self, raw_data: Dict[str, Any]) -> Tuple[Optional[Telemetry], Optional[str]]:
        """Step 1: Validate incoming raw telemetry using Pydantic schemas."""
        try:
            telemetry = Telemetry(**raw_data)
            return telemetry, None
        except ValidationError as e:
            return None, f"Schema validation error: {e}"

    def clean_telemetry(self, telemetry: Telemetry) -> Dict[str, float]:
        """Step 2: Clean and impute telemetry values, clamping out-of-physical bounds."""
        soc = max(0.0, min(1.0, float(telemetry.battery_soc)))
        temp = max(-50.0, min(100.0, float(telemetry.battery_temp_c)))
        voltage = max(18.0, min(36.0, float(telemetry.bus_voltage_v)))
        latency = max(5.0, min(1000.0, float(telemetry.comm_latency_ms)))
        snr = max(-5.0, min(45.0, float(telemetry.link_snr_db)))
        mem = max(0.0, min(100.0, float(telemetry.memory_util_pct)))
        sunlit = 1.0 if telemetry.is_sunlit else 0.0

        return {
            "battery_soc": soc,
            "battery_temp_c": temp,
            "bus_voltage_v": voltage,
            "comm_latency_ms": latency,
            "link_snr_db": snr,
            "memory_util_pct": mem,
            "is_sunlit": sunlit,
        }

    def extract_features(
        self,
        cleaned_telemetry: Dict[str, float],
        request: MissionRequest,
        elevation_deg: float = 45.0,
        slew_penalty_deg: float = 5.0,
        current_time_s: float = 0.0,
    ) -> np.ndarray:
        """Step 3: Feature Engineering into standardized feature vector."""
        # Normalized telemetry
        soc = cleaned_telemetry["battery_soc"]
        temp_norm = (cleaned_telemetry["battery_temp_c"] - self.temp_min) / (self.temp_max - self.temp_min)
        volt_norm = cleaned_telemetry["bus_voltage_v"] / self.voltage_nominal
        lat_norm = min(1.0, cleaned_telemetry["comm_latency_ms"] / self.latency_max)
        snr_norm = max(0.0, min(1.0, (cleaned_telemetry["link_snr_db"] - self.snr_min) / (self.snr_max - self.snr_min)))
        mem_norm = cleaned_telemetry["memory_util_pct"] / 100.0
        sunlit = cleaned_telemetry["is_sunlit"]

        # Normalized request features
        priority_norm = (request.priority - 1.0) / 4.0
        duration_norm = min(1.0, request.duration_s / self.max_duration)
        elevation_norm = max(0.0, min(1.0, elevation_deg / 90.0))

        # Interaction & Slack features
        slack_s = max(0.0, request.deadline_epoch_s - current_time_s)
        slack_ratio = min(1.0, slack_s / 3600.0)
        energy_cost_est = (request.duration_s * 15.0) / 1000.0  # Approx energy cost
        energy_cost_ratio = min(1.0, energy_cost_est / max(0.01, soc))
        slew_norm = min(1.0, slew_penalty_deg / 90.0)

        feature_vector = np.array(
            [
                soc,
                temp_norm,
                volt_norm,
                lat_norm,
                snr_norm,
                mem_norm,
                sunlit,
                priority_norm,
                duration_norm,
                elevation_norm,
                slack_ratio,
                energy_cost_ratio,
                slew_norm,
            ],
            dtype=np.float32,
        )
        return feature_vector

    def process_batch(
        self,
        raw_telemetry_list: List[Dict[str, Any]],
        request: MissionRequest,
        current_time_s: float = 0.0,
    ) -> Tuple[np.ndarray, List[str]]:
        """Processes a batch of candidate resources for a specific task request."""
        valid_vectors = []
        valid_resource_ids = []

        for raw in raw_telemetry_list:
            telemetry, err = self.validate_telemetry(raw)
            if err or telemetry is None:
                continue
            cleaned = self.clean_telemetry(telemetry)
            feat = self.extract_features(cleaned, request, current_time_s=current_time_s)
            valid_vectors.append(feat)
            valid_resource_ids.append(telemetry.resource_id)

        if not valid_vectors:
            return np.empty((0, len(self.FEATURE_NAMES)), dtype=np.float32), []

        return np.vstack(valid_vectors), valid_resource_ids


# Singleton instance
_pipeline_instance: Optional[DataProcessingPipeline] = None


def get_data_pipeline() -> DataProcessingPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = DataProcessingPipeline()
    return _pipeline_instance
