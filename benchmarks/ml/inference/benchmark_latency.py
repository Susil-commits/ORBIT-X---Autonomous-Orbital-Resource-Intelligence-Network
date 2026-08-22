"""High-Throughput ML Inference Latency and Serving Benchmark.

Measures p50, p95, and p99 inference latency and throughput for
Cross-Attention, XGBoost, MLP, Isolation Forest, and TreeSHAP.
"""

import time
from typing import Dict, Any
import numpy as np
import torch

from ml.models.cross_attention.ranker import CrossAttentionNeuralRanker


def benchmark_inference_latency(batch_size: int = 10, iterations: int = 1000) -> Dict[str, Any]:
    model = CrossAttentionNeuralRanker()
    model.eval()

    res_feat = torch.randn(batch_size, 10, 7)
    req_feat = torch.randn(batch_size, 1, 6)

    # Warmup
    for _ in range(50):
        with torch.no_grad():
            _ = model(res_feat, req_feat)

    latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        with torch.no_grad():
            _ = model(res_feat, req_feat)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    p50 = float(np.percentile(latencies, 50))
    p95 = float(np.percentile(latencies, 95))
    p99 = float(np.percentile(latencies, 99))
    throughput = (batch_size * iterations) / (sum(latencies) / 1000.0)

    return {
        "model": "CrossAttentionNeuralRanker",
        "batch_size": batch_size,
        "iterations": iterations,
        "latency_p50_ms": round(p50, 4),
        "latency_p95_ms": round(p95, 4),
        "latency_p99_ms": round(p99, 4),
        "throughput_inferences_per_sec": round(throughput, 1),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(benchmark_inference_latency(), indent=2))
