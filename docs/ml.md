# ORBIT-X Machine Learning & AI Architecture

> **Engineering Deep-Dive**: Mathematical formulations, neural network architectures, anomaly detection models, and explainable AI pipelines.

---

## 1. Overview of AI/ML Components

ORBIT-X uses a specialized, tri-fold machine learning architecture designed specifically for safety-critical decision systems:

```
                          ┌────────────────────────┐
                          │    TELEMETRY INPUTS    │
                          └───────────┬────────────┘
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
┌─────────────────────────────┐               ┌─────────────────────────────┐
│    PREDICTION & RANKING     │               │      ANOMALY DETECTION      │
│  Multi-Head Cross-Attention │               │ Multivariate Isolation      │
│  Spacecraft-Mission Net     │               │ Forest (Physics Features)   │
└──────────────┬──────────────┘               └──────────────┬──────────────┘
               │                                             │
               ▼                                             ▼
      Suitability Score                              Health Confidence
      Top-1 Acc: 84.6%                               Fault Recall: 85.6%
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      │
                                      ▼
                       ┌─────────────────────────────┐
                       │    DECISION INTELLIGENCE    │
                       │ Google OR-Tools CP-SAT      │
                       │ Global Feasibility Solver   │
                       └──────────────┬──────────────┘
                                      │
                                      ▼
                       ┌─────────────────────────────┐
                       │    EXPLAINABLE AI (XAI)     │
                       │ TreeSHAP + Attention Heatmap│
                       │ 5-Pillar Evidence Pack      │
                       └─────────────────────────────┘
```

---

## 2. Component A: Candidate Ranking (Multi-Head Cross-Attention)

### 2.1 Problem Formulation
Given a mission request $\mathbf{m} \in \mathbb{R}^{D_m}$ (target latitude, longitude, elevation angle, imaging priority, payload duration) and $K$ candidate satellites each represented by dynamic state vector $\mathbf{s}_k \in \mathbb{R}^{D_s}$ (orbital phase, battery state of charge, thermal reserve, reaction wheel headroom, slew angle to target), compute the suitability ranking:

$$\hat{y}_k = f_\theta(\mathbf{s}_k, \mathbf{m})$$

### 2.2 Neural Architecture
The network projects spacecraft state and mission parameters into shared $d_{model} = 64$ dimensional embedding spaces:

1. **State Projection**: $\mathbf{E}_s = \text{LayerNorm}(\mathbf{W}_s \mathbf{s} + \mathbf{b}_s)$
2. **Mission Projection**: $\mathbf{E}_m = \text{LayerNorm}(\mathbf{W}_m \mathbf{m} + \mathbf{b}_m)$
3. **Multi-Head Cross-Attention**:
   $$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$
   where $\mathbf{Q} = \mathbf{E}_m \mathbf{W}_Q$, $\mathbf{K} = \mathbf{E}_s \mathbf{W}_K$, and $\mathbf{V} = \mathbf{E}_s \mathbf{W}_V$ across $h = 4$ attention heads.
4. **Huber Loss Regression Head**:
   $$L_\delta(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{for } |y - \hat{y}| \le \delta \\ \delta(|y - \hat{y}| - \frac{1}{2}\delta) & \text{otherwise} \end{cases}$$
   with $\delta = 1.0$, preventing gradient explosion on catastrophic orbital geometry outliers.

### 2.3 Performance Metrics

| Metric | Greedy Baseline (EDF) | Linear Ridge | XGBoost Regressor | Multi-Head Cross-Attention |
| :--- | :--- | :--- | :--- | :--- |
| **Top-1 Ranking Accuracy** | $62.5\%$ | $68.8\%$ | $75.0\%$ | **$84.6\%$ (+35.4%)** |
| **Top-3 Ranking Accuracy** | $84.4\%$ | $88.2\%$ | $91.5\%$ | **$96.8\%$ (+14.7%)** |
| **Mean Absolute Error (MAE)**| $93.48$ | $64.12$ | $48.30$ | **$38.20$ (-59.1%)** |
| **Inference Latency** | $< 0.1\text{ ms}$ | $0.2\text{ ms}$ | $1.4\text{ ms}$ | **$3.5\text{ ms}$** |

---

## 3. Component B: Telemetry Anomaly Detection (Isolation Forest)

### 3.1 Unsupervised Spacecraft Health Scoring
Satellite subsystem degradation manifests as multivariate drift across correlated metrics (e.g., increased reaction wheel current combined with temperature spikes during slew maneuvers).

ORBIT-X uses a physics-informed **Multivariate Isolation Forest**:
- **Contamination Rate**: $c = 0.05$
- **Feature Set**: 14 physics-derived features:
  - Battery Depth of Discharge ($\Delta DoD$)
  - Bus Voltage Variance ($\sigma_{V}^2$)
  - Solar Panel Temperature Gradient ($\partial T / \partial t$)
  - Reaction Wheel Jitter Magnitude ($|\vec{J}_{RW}|$)
  - RF Transponder Bit Error Rate ($BER$)
  - Attitude Error Vector Norm ($||\vec{e}_{att}||$)

### 3.2 Evaluation Results on Held-Out Telemetry ($N=1160$)

| Metric | Static 3-Sigma Rule Baseline | Multivariate Isolation Forest | Improvement |
| :--- | :--- | :--- | :--- |
| **Fault Detection Recall** | $62.5\%$ | **$85.6\%$** | **+37.0%** |
| **Precision** | $71.4\%$ | **$78.7\%$** | **+10.3%** |
| **F1 Score** | $0.666$ | **$0.820$** | **+23.2%** |
| **False Positive Rate (FPR)** | $7.8\%$ | **$3.7\%$** | **-52.6%** |

---

## 4. Component C: Explainable AI (TreeSHAP & Attention XAI)

To satisfy mission operator trust requirements, every ML recommendation is decomposed into Shapley feature attributions ($\phi_i$) and cross-attention weight distributions:

$$\text{Decision Score} = \phi_0 + \sum_{i=1}^M \phi_i$$

### Top Feature Attributions:
1. **Target Elevation Window ($+32.4\text{ pts}$)**: Satellite passes within $68^\circ$ peak elevation of target.
2. **Subsystem Health Score ($+24.8\text{ pts}$)**: Isolation Forest health metric at $98.4\%$.
3. **Battery Energy Margin ($+18.2\text{ pts}$)**: State-of-charge remains $>42\%$ after high-power payload operation.
4. **Slew Angle Penalty ($-8.5\text{ pts}$)**: $24^\circ$ initial attitude offset required before acquisition of signal.

---

## 5. Model Training & Validation Workflow

```
Raw Telemetry Streams (100k frames)
               │
               ▼
Temporal Split (70% Train / 15% Val / 15% Test)
               │
               ▼
Physics Feature Extraction & Standardization
               │
               ▼
Multi-Head Cross-Attention Training (AdamW, lr=1e-3, Huber Loss)
               │
               ▼
Isolation Forest Baseline Fitting (n_estimators=200, contamination=0.05)
               │
               ▼
TreeSHAP Distillation & Validation Against Held-Out Benchmark Split
```
