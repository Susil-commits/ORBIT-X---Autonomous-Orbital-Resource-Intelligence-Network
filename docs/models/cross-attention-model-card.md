# Model Card: ConstellationCrossAttentionNet

## 1. Model Purpose
`ConstellationCrossAttentionNet` is a deep neural ranking and allocation model designed to learn complex, non-linear interactions between available **operational resource-state features** (e.g. battery state-of-charge, internal temperature, slew availability, sunlit status) and incoming **task/request requirements** (e.g. required duration, priority level, optical look-angle, data volume, deadline slack).

It produces a fast, probabilistic candidate suitability score used to warm-start and prune the search space for deterministic optimization solvers.

## 2. Input Features (18-Dimensional Tabular Vector)

### Resource State Features (8 Dimensions)
1. `battery_soc` (float, [0, 1]) - Current battery State of Charge.
2. `internal_temp_c` (float, standardized) - Payload/bus operating temperature.
3. `is_sunlit` (binary, {0, 1}) - Solar illumination status (1 = sunlit, 0 = eclipse).
4. `energy_cost_ratio` (float, [0, 1]) - Ratio of estimated task power draw to available battery capacity.
5. `slew_penalty_norm` (float, [0, 1]) - Angular slew penalty required to re-orient payload towards target.
6. `memory_util_pct` (float, [0, 1]) - On-board storage utilization.
7. `comm_latency_norm` (float, [0, 1]) - Normalized round-trip communication latency.
8. `historical_reliability` (float, [0, 1]) - Historical task success rate for this node.

### Request / Mission Requirement Features (10 Dimensions)
9. `priority_norm` (float, [0, 1]) - Task priority score (1.0 = Emergency Disaster Response, 0.2 = Routine).
10. `duration_norm` (float, [0, 1]) - Observation window duration normalized against orbital pass length.
11. `duration_ratio` (float, [0, 1]) - Ratio of observation duration to total contact window.
12. `deadline_slack_ratio` (float, [0, 1]) - Ratio of available time slack before deadline.
13. `elevation_norm` (float, [0, 1]) - Optical look-angle elevation normalized to [0, 90] degrees.
14. `target_lat_norm` (float, [-1, 1]) - Target latitude normalized.
15. `target_lon_norm` (float, [-1, 1]) - Target longitude normalized.
16. `data_volume_norm` (float, [0, 1]) - Expected payload raw data generation.
17. `required_sensor_type` (categorical embedded, dim=8) - Sensor modality requirement (Optical, SAR, IR).
18. `weather_risk_factor` (float, [0, 1]) - Cloud cover / atmospheric attenuation index.

## 3. Output
- **Candidate Suitability Score (Bid Value):** Scalar float $\in [0, 100]$, representing the predicted marginal utility and feasibility of assigning the request to the candidate node.
- **Top-K Ranked Candidates:** Ordered ranking of all available candidate nodes.
- **Attention Map:** $4 \times 8 \times 10$ Cross-Attention weight matrix exposing the exact interaction strength between resource tokens and request tokens.

## 4. Architecture
The model implements a feature-tokenized Cross-Attention architecture:
```
  Resource Features (8-dim)             Request Features (10-dim)
             │                                      │
             ▼                                      ▼
   Linear Tokenizer (d=64)                Linear Tokenizer (d=64)
             │                                      │
             ▼                                      ▼
      LayerNorm + GELU                       LayerNorm + GELU
             │                                      │
             └──────────────────┬───────────────────┘
                                ▼
                Multi-Head Cross-Attention Layer
                  (Queries: Request Tokens, d=64)
                  (Keys/Values: Resource Tokens, d=64)
                  (4 Attention Heads, Dropout=0.1)
                                │
                                ▼
                     Residual Connection + LayerNorm
                                │
                                ▼
                     Feed-Forward MLP Network
                    [64 -> 128 -> 64 -> 32 -> 1]
                                │
                                ▼
                    Predicted Suitability Score
```

### Why Attention is Useful
The model receives two heterogeneous, highly correlated feature groups: **available resource state** and **incoming request requirements**. 

Standard MLPs treat all concatenated features symmetrically, ignoring the bipartite interaction structure. Cross-attention allows each mission demand dimension (such as high data volume) to dynamically query specific resource states (such as storage capacity and downlink SNR), learning fine-grained cross-modal dependencies.

## 5. Training Data
- **Corpus:** 5,000 multi-orbit simulated operational scenarios generated via `backend/training/advanced_dataset_generator.py`.
- **Labels:** Ground truth global optimal assignments and bid values generated via Google OR-Tools CP-SAT exhaustive optimization (`backend/training/collect_cpsat_labels.py`).
- **Splits:** 80% Train (4,000), 10% Validation (500), 10% Test (500).

## 6. Loss Function
Composite Huber loss and ranking margin loss:
$$\mathcal{L} = \text{HuberLoss}(y_{\text{pred}}, y_{\text{true}}, \delta=1.0) + \lambda \sum_{i < j} \max(0, \gamma - (y_{\text{pred}, i} - y_{\text{pred}, j}))$$
where $\gamma = 0.2$ is the ranking margin, and $\lambda = 0.1$ balances value regression against pairwise ranking concordance.

## 7. Hyperparameters
- **Optimizer:** AdamW (`lr=1e-3`, `weight_decay=1e-4`)
- **Learning Rate Scheduler:** Cosine Annealing with Warm Restarts (`T_0=10`, `T_mult=2`)
- **Embedding Dimension:** $d_{\text{model}} = 64$
- **Attention Heads:** 4
- **Dropout Rate:** 0.10
- **Batch Size:** 64
- **Training Epochs:** 50 with Early Stopping (Patience = 7 epochs on Validation Loss)

## 8. Evaluation Metrics
- **Top-1 Agreement with Optimal Solver:** 84.6%
- **Top-3 Inclusion Rate:** 96.2%
- **Mean Absolute Error (MAE):** 28.40
- **NDCG@5:** 0.912
- **Kendall's Tau Rank Correlation:** 0.784

## 9. Inference Latency & Throughput
- **Single Request Latency (p50):** 0.372 ms
- **Single Request Latency (p95):** 0.557 ms
- **Batch Latency (Batch=64, CUDA):** 1.82 ms
- **Inference Throughput:** 2,690.9 inferences/second (CPU) / 35,000+ inferences/second (GPU)

## 10. Known Limitations
1. **Unconstrained Hard Bounds:** Neural scores are probabilistic. In ~3.4% of edge cases, the top-ranked candidate may violate strict boundary constraints (e.g. sub-20% battery threshold). **Mitigation:** The production pipeline pipes neural candidates into CP-SAT for hard constraint verification.
2. **Tabular Feature Dependency:** Requires all 18 features to be present or properly imputed by the preprocessing layer.

## 11. Failure Cases & Degradation Modes
- **Extreme Telemetry Staleness (>15 min):** When resource telemetry is delayed, model assigns tasks to nodes that have since entered eclipse.
- **Simultaneous Disaster Surges (>20 priority-1 tasks):** Cross-attention scores alone can produce contention hotspots on the single best satellite.
- **Unseen Space Weather Events:** Extreme geomagnetic radiation anomalies not present in training data reduce ranking agreement to ~68%.

## 12. Model Version & Artifacts
- **Version:** `v2.2.0-champion`
- **Artifact File:** `backend/models/cross_attention_network.pt`
- **Metadata File:** `backend/models/metadata.json`
- **Surrogate Distillation:** `backend/models/shap_surrogate.json`

## 13. License & Ownership
- **Owner:** ORBIT-X Autonomous Decision Intelligence Team
- **License:** Apache 2.0 / Open Decision Systems Specification
