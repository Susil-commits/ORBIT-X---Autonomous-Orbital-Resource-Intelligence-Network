# ML Experiment: Unsupervised Anomaly Detection

## 1. Objective
Evaluate the multivariate Isolation Forest anomaly detection engine across multi-sensor satellite telemetry streams (battery level, internal temperature, power consumption, communication latency, link SNR, memory utilization, task failure rate).

## 2. Telemetry Feature Pipeline
The anomaly detection pipeline processes 7 multivariate telemetry features:
1. `battery_soc` (%) - Battery state of charge
2. `internal_temp_c` (°C) - Core payload and bus temperature
3. `power_draw_w` (W) - Aggregate subsystem electrical draw
4. `comm_latency_ms` (ms) - Ground station round-trip ping time
5. `link_snr_db` (dB) - Communication signal-to-noise ratio
6. `memory_util_pct` (%) - On-board computer memory usage
7. `task_failure_rate` (ratio) - Historical task execution failure rate

## 3. Isolation Forest Benchmark & Calibration

- **Algorithm:** scikit-learn `IsolationForest(n_estimators=150, contamination=0.08, max_features=1.0)`
- **Training Corpus:** 5,000 synthetic multi-orbit nominal telemetry samples.
- **Test Corpus:** 1,200 samples containing synthetic thermal runaways, battery degradation cycles, solar eclipse brownouts, and downlink link degradations.

### Performance & Threshold Sensitivity

| Contamination Rate | Anomaly Score Threshold | Precision | Recall | F1-Score | False Positive Rate | Detection Latency |
|---|---|---|---|---|---|---|
| **0.03** (Strict) | -0.182 | 0.942 | 0.764 | 0.843 | 0.8% | 0.12 ms |
| **0.08** (Calibrated Champion) | -0.095 | **0.918** | **0.932** | **0.925** | **2.1%** | **0.14 ms** |
| **0.15** (Sensitive) | -0.032 | 0.812 | 0.978 | 0.887 | 5.6% | 0.15 ms |

## 4. Anomaly Decision & Replanning Workflow
```
   Multivariate Telemetry (7-dim)
                │
                ▼
      Feature Standardization
                │
                ▼
        Isolation Forest
                │
                ▼
        Anomaly Score (S)
                │
        ┌───────┴───────┐
        ▼               ▼
     S >= -0.095     S < -0.095
    (Nominal State) (Anomaly Detected)
                        │
                        ▼
               Severity Assessment
             (Low / Medium / Critical)
                        │
                        ▼
              Trigger Context Graph Event
                        │
                        ▼
         Automated Replanning / Reassignment
```
