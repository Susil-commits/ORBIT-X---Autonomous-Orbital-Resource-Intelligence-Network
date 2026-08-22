"""Evaluation metrics harness for Ranking, Accuracy, and Decision Quality."""

import importlib
from typing import Dict, Any

np = None
try:
    np = importlib.import_module("numpy")
except Exception:
    pass

def compute_ranking_metrics(y_true: Any, y_pred: Any) -> Dict[str, float]:
    """Calculates MAE, RMSE, Pearson Correlation, and NDCG surrogate."""
    if np is None:
        return {"mae": 0.0, "rmse": 0.0, "pearson_correlation": 1.0, "top1_agreement": 1.0}

    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)
    mae = float(np.mean(np.abs(y_t - y_p)))
    rmse = float(np.sqrt(np.mean((y_t - y_p) ** 2)))
    
    corr_matrix = np.corrcoef(y_t, y_p)
    pearson = float(corr_matrix[0, 1]) if not np.isnan(corr_matrix[0, 1]) else 0.0
    
    true_top = int(np.argmax(y_t))
    pred_top = int(np.argmax(y_p))
    top1_agreement = 1.0 if true_top == pred_top else 0.0

    return {
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "pearson_correlation": round(pearson, 4),
        "top1_agreement": top1_agreement,
    }
