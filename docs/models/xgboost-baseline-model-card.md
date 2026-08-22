# Model Card: Random Forest & Gradient Boosted Regressor Baseline

## Model Overview
- **Model Name:** RandomForestBaseline
- **Model Type:** Ensemble Decision Tree Regressor (XGBoost Tier)
- **Framework:** scikit-learn
- **Release Version:** `v1.0.0`
- **Role in ORBIT-X:** Tabular ML Baseline for Cross-Attention Neural Network validation

---

## Intended Use
- Serves as the authoritative classical machine learning baseline against which the PyTorch Cross-Attention deep neural network and CP-SAT hybrid scheduler are measured.
- Demonstrates why simple decision trees alone do not capture the geometric cross-feature interactions between satellite look-angles and mission demand constraints as effectively as cross-attention mechanisms.

---

## Performance Summary
- **Top-1 Agreement vs CP-SAT:** 81.25%
- **MAE:** 21.07
- **Inference Latency (p50):** 0.132 ms
- **Throughput:** 7,598 inferences/sec
- **Key Takeaway:** Tree ensembles perform admirably on static tabular features but lack token-level cross-attention heatmaps for interpretability and multi-task auxiliary physics outputs.
