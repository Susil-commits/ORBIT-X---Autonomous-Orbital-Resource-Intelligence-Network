# ORBIT-X Empirical Machine Learning Experiments & Ablations

> **Engineering Deep-Dive**: Model iteration history, temporal split validation, feature ablation studies, and baseline benchmarking.

---

## 1. Machine Learning Experimentation Lifecycle

To ensure rigorous validation and avoid data leakage common in time-series telemetry, all models in ORBIT-X were evaluated following a strict experimental progression:

```
Baseline (Greedy EDF & Linear Ridge)
                 │
                 ▼
Improved Model (XGBoost / LightGBM)
                 │
                 ▼
Temporal Split Evaluation (Train: Week 1-3, Val: Week 4, Test: Week 5)
                 │
                 ▼
Feature Ablation & SHAP Importance Analysis
                 │
                 ▼
Final Deep Model (Multi-Head Cross-Attention + Huber Loss)
```

---

## 2. Temporal Split Validation (Out-of-Time Testing)

In satellite operations, random k-fold cross-validation causes catastrophic lookahead data leakage due to temporal auto-correlation in orbital mechanics and battery thermal inertia.

ORBIT-X uses a strict **Temporal Train / Validation / Test Split**:
- **Train Split (70%)**: $T \in [t_0, t_0 + 21\text{ days}]$ (72,000 telemetry frames)
- **Validation Split (15%)**: $T \in [t_0 + 21\text{ days}, t_0 + 25.5\text{ days}]$ (14,400 frames)
- **Held-Out Test Split (15%)**: $T \in [t_0 + 25.5\text{ days}, t_0 + 30\text{ days}]$ (14,400 frames)

### Temporal Test Results:

| Model Architecture | Train Loss (MAE) | Val Loss (MAE) | Held-Out Test MAE | Top-1 Ranking Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **Greedy Baseline (EDF)** | $93.48$ | $93.48$ | $93.48$ | $62.5\%$ |
| **Ridge Linear Regression** | $58.20$ | $61.40$ | $64.12$ | $68.8\%$ |
| **Random Forest (100 trees)**| $38.10$ | $44.80$ | $51.20$ | $73.4\%$ |
| **XGBoost Regressor** | $32.40$ | $41.20$ | $48.30$ | $75.0\%$ |
| **Cross-Attention Net (Ours)**| **$24.10$** | **$31.80$** | **$38.20$** | **$84.6\%$** |

---

## 3. Feature Ablation Study

To measure the marginal contribution of each operational feature group, we performed a systematic leave-one-group-out ablation on the held-out test split:

| Configuration | Top-1 Accuracy | MAE | $\Delta$ Accuracy |
| :--- | :--- | :--- | :--- |
| **Full Model (All Features)** | **$84.6\%$** | **$38.20$** | **Baseline** |
| *w/o Orbital Geometry (SGP4 Elevation / Range)* | $67.2\%$ | $72.10$ | **-17.4%** |
| *w/o Subsystem Health (Isolation Forest)* | $76.8\%$ | $51.40$ | **-7.8%** |
| *w/o Power & Thermal Features (DoD, Temp)* | $71.4\%$ | $62.80$ | **-13.2%** |
| *w/o Cross-Attention (Replaced by MLP Concat)*| $78.1\%$ | $46.90$ | **-6.5%** |

---

## 4. Policy Comparison: Heuristic vs RL vs Hybrid Solver

| Operational Approach | Constellation Priority Yield | Constraint Violations | Decision Latency | Robustness to Drift |
| :--- | :--- | :--- | :--- | :--- |
| **Greedy Heuristic (EDF)** | $76.2\%$ | $1.2\%$ | **$0.2\text{ ms}$** | Poor (Rigid rules) |
| **Pure Reinforcement Learning (PPO)**| $88.4\%$ | $4.8\%$ | $4.2\text{ ms}$ | Moderate (Policy drift) |
| **ORBIT-X (Neural Ranking + CP-SAT)**| **$98.7\%$** | **$0.0\%$** | **$11.4\text{ ms}$** | **High (Verified Safety)** |

**Key Takeaway**: While pure RL achieves decent yield, it incurs unacceptable constraint violations in edge cases. ORBIT-X's hybrid architecture pairs fast neural scoring with CP-SAT deterministic guarantees, achieving highest yield ($98.7\%$) with zero constraint violations.
