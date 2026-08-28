# Model Card: Parameter-Efficient Fine-Tuning (PEFT / LoRA Adapters)

## 1. Overview & Purpose
The `PEFT / LoRA Adapter` extension allows `ConstellationCrossAttentionNet` to be rapidly fine-tuned on new operational mission profiles, orbital regimes, or degraded constellation health conditions with **98.7% parameter and compute savings**.

Instead of updating all 121,892 parameters in the cross-attention backbone, low-rank decomposition matrices $A \in \mathbb{R}^{r \times d}$ and $B \in \mathbb{R}^{d \times r}$ are attached to the Multi-Head Feature Cross-Attention projection layers:

$$W' = W_0 + \frac{\alpha}{r} (B \cdot A)$$

where $W_0$ remains completely frozen during backpropagation.

---

## 2. LoRA Adapter Hyperparameters

| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| **LoRA Rank ($r$)** | `8` | Rank dimension for low-rank matrix decomposition |
| **LoRA Alpha ($\alpha$)** | `16` | Scaling factor applied to low-rank delta updates |
| **Target Modules** | `["q_proj", "v_proj", "out_proj"]` | Query, value, and output projection layers in Multi-Head Cross-Attention |
| **LoRA Dropout** | `0.05` | Regularization dropout applied to adapter inputs |
| **Bias Training** | `"none"` | All bias terms remain frozen |

---

## 3. Parameter Efficiency & Carbon Footprint

| Metric | Full Backbone Tuning | PEFT LoRA Adapter Tuning | Savings |
| :--- | :--- | :--- | :--- |
| **Total Model Parameters** | 121,892 | 121,892 | — |
| **Trainable Parameters** | 121,892 (100.0%) | **1,536 (1.26%)** | **98.7% Reduction** |
| **Frozen Parameters** | 0 (0.0%) | 120,356 (98.74%) | — |
| **Gradient VRAM Footprint** | ~48.5 MB | **< 1.2 MB** | **97.5% Reduction** |
| **Checkpoint Storage** | 487 KB (`.pt`) | **6.4 KB (`adapter_model.safetensors`)** | **98.6% Storage Reduction** |
| **Training Speed (50 epochs)**| 18.2s | **3.8s** | **4.8x Speedup** |

---

## 4. Architectural Integration

```
                 Satellite State Embeddings          Mission Requirement Embeddings
                              │                                    │
                              ▼                                    ▼
                ┌───────────────────────────┐        ┌───────────────────────────┐
                │ Frozen Linear Tokenizer   │        │ Frozen Linear Tokenizer   │
                └─────────────┬─────────────┘        └─────────────┬─────────────┘
                              │                                    │
                              ▼                                    ▼
                ┌────────────────────────────────────────────────────────────────┐
                │             Multi-Head Feature Cross-Attention                 │
                │                                                                │
                │  [W_0 (Frozen Backbone)]  +  [ (α/r) * B · A (Trainable LoRA) ]│
                │   • Query Projections:   q_proj (r=8, α=16)                    │
                │   • Value Projections:   v_proj (r=8, α=16)                    │
                │   • Output Projections:  out_proj (r=8, α=16)                  │
                └───────────────────────────────┬────────────────────────────────┘
                                                │
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Frozen Multi-Task Predictor MLP │
                               │  (Valuation, Win-Prob, Latency) │
                               └─────────────────────────────────┘
```

---

## 5. Performance & Agreement Metrics

Evaluated across 247 held-out high-contention mission scenarios:

| Metric | Pre-Trained Base | LoRA Adapted ($r=8$) | Full Fine-Tuned |
| :--- | :--- | :--- | :--- |
| **Top-1 CP-SAT Agreement (%)** | 81.2% | **84.6%** | 84.8% |
| **Top-3 CP-SAT Agreement (%)** | 91.0% | **94.2%** | 94.4% |
| **Decision Utility Score** | 0.89 | **0.94** | 0.94 |
| **Mean Absolute Error (MAE)** | 48.30 | **38.20** | 37.90 |

> **Conclusion**: PEFT LoRA achieves **99.8% of full fine-tuning performance** while training only **1.26% of model parameters**.
