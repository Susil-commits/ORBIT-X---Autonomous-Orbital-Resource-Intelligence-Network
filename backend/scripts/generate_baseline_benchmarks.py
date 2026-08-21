import os
import sys
import time
import json
import tracemalloc
import numpy as np
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.physics.orbit_propagator import propagate_orbit
from app.simulation.benchmark import run_benchmark_comparison
from app.intelligence.bid_value_network import get_bid_value_predictor
from eval.scale_benchmark import generate_synthetic_scaling_constellation

def benchmark_scheduler(iterations: int = 15):
    print(f"Benchmarking CP-SAT Scheduler over {iterations} iterations...")
    latencies = []
    success_count = 0
    
    # Run warmups
    for _ in range(2):
        run_benchmark_comparison(seed=42, num_missions=24)
        
    tracemalloc.start()
    
    for i in range(iterations):
        t0 = time.perf_counter()
        results = run_benchmark_comparison(seed=100 + i, num_missions=24)
        t1 = time.perf_counter()
        lat_ms = (t1 - t0) * 1000.0
        latencies.append(lat_ms)
        cpsat_res = next((r for r in results if "CP-SAT" in r.scheduler_name), None)
        if cpsat_res and cpsat_res.completion_rate_pct > 0:
            success_count += 1
            
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    latencies = np.array(latencies)
    return {
        "benchmark": "CP-SAT Constellation Scheduler",
        "iterations": iterations,
        "missions_per_run": 24,
        "success_rate_pct": (success_count / iterations) * 100.0,
        "latency_ms": {
            "mean": round(float(np.mean(latencies)), 2),
            "std": round(float(np.std(latencies)), 2),
            "p50": round(float(np.percentile(latencies, 50)), 2),
            "p95": round(float(np.percentile(latencies, 95)), 2),
            "p99": round(float(np.percentile(latencies, 99)), 2),
            "min": round(float(np.min(latencies)), 2),
            "max": round(float(np.max(latencies)), 2)
        },
        "throughput_runs_per_sec": round(float(1000.0 / np.mean(latencies)), 2),
        "memory_mb": {
            "current": round(float(current_mem / (1024 * 1024)), 2),
            "peak": round(float(peak_mem / (1024 * 1024)), 2)
        },
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def benchmark_propagation(scales = [12, 50, 100, 500, 1000], steps_per_scale: int = 10):
    print("Benchmarking SGP4 / Physics Propagation Throughput...")
    results = []
    for count in scales:
        sats = generate_synthetic_scaling_constellation(count)
        # Warmup
        for sat in sats:
            propagate_orbit(sat.keplerian, 1.0)
        
        step_times = []
        for step in range(steps_per_scale):
            t0 = time.perf_counter()
            for sat in sats:
                propagate_orbit(sat.keplerian, float(step + 1))
            t1 = time.perf_counter()
            step_times.append((t1 - t0) * 1000.0)
            
        avg_ms = float(np.mean(step_times))
        p95_ms = float(np.percentile(step_times, 95))
        throughput = float((count / (avg_ms / 1000.0))) if avg_ms > 0 else 0.0
        
        results.append({
            "constellation_size": count,
            "avg_step_duration_ms": round(avg_ms, 2),
            "p95_step_duration_ms": round(p95_ms, 2),
            "throughput_sats_per_sec": round(throughput, 1)
        })
        print(f"  Count: {count} | Avg Step: {avg_ms:.2f}ms | Throughput: {throughput:.1f} sats/sec")
        
    return {
        "benchmark": "Orbital Propagation Throughput",
        "scales_tested": results,
        "max_tested_constellation": max(scales),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def benchmark_ml_inference(iterations: int = 100):
    print("Benchmarking PyTorch BidValueMLP Neural Inference...")
    predictor = get_bid_value_predictor()
    
    # Feature vector sample (10 dimensions) as float32 numpy array
    sample_features = np.array([0.80, 0.85, 0.70, 0.10, 1.0, 0.90, 1.0, 0.60, 0.15, 0.25], dtype=np.float32)
    batch_features = np.tile(sample_features, (64, 1)).astype(np.float32)
    
    # Warmup
    for _ in range(10):
        predictor.predict_single(sample_features)
        
    single_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        predictor.predict_single(sample_features)
        t1 = time.perf_counter()
        single_latencies.append((t1 - t0) * 1000.0)
        
    batch_latencies = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        predictor.predict_batch(batch_features)
        t1 = time.perf_counter()
        batch_latencies.append((t1 - t0) * 1000.0)
        
    single_arr = np.array(single_latencies)
    batch_arr = np.array(batch_latencies)
    
    return {
        "benchmark": "Neural Bid-Valuation Model (BidValueMLP)",
        "single_item_inference_ms": {
            "mean": round(float(np.mean(single_arr)), 3),
            "p50": round(float(np.percentile(single_arr, 50)), 3),
            "p95": round(float(np.percentile(single_arr, 95)), 3),
            "p99": round(float(np.percentile(single_arr, 99)), 3),
            "throughput_inferences_per_sec": round(float(1000.0 / np.mean(single_arr)), 1)
        },
        "batch_64_inference_ms": {
            "mean": round(float(np.mean(batch_arr)), 3),
            "p50": round(float(np.percentile(batch_arr, 50)), 3),
            "p95": round(float(np.percentile(batch_arr, 95)), 3),
            "p99": round(float(np.percentile(batch_arr, 99)), 3),
            "effective_throughput_inferences_per_sec": round(float((64 * 1000.0) / np.mean(batch_arr)), 1)
        },
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

def main():
    benchmarks_dir = ROOT_DIR / "benchmarks"
    baseline_dir = benchmarks_dir / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    
    sched_data = benchmark_scheduler(iterations=5)
    with open(baseline_dir / "scheduler.json", "w", encoding="utf-8") as f:
        json.dump(sched_data, f, indent=2)
        
    prop_data = benchmark_propagation()
    with open(baseline_dir / "propagation.json", "w", encoding="utf-8") as f:
        json.dump(prop_data, f, indent=2)
        
    ml_data = benchmark_ml_inference(iterations=100)
    with open(baseline_dir / "ml_inference.json", "w", encoding="utf-8") as f:
        json.dump(ml_data, f, indent=2)
        
    # Write baseline README
    baseline_readme = f"""# ORBIT-X Pre-Production Baseline Benchmarks

These benchmarks capture the empirical performance profile of the ORBIT-X intelligence engine before architectural upgrades (Kafka, Redis, BullMQ, Observability, Kubernetes).

## Summary Snapshot

| Subsystem | Metric | Baseline Value |
|---|---|---|
| **CP-SAT Scheduler** | P50 Latency | `{sched_data['latency_ms']['p50']:.2f} ms` |
| **CP-SAT Scheduler** | P95 Latency | `{sched_data['latency_ms']['p95']:.2f} ms` |
| **CP-SAT Scheduler** | Success Rate | `{sched_data['success_rate_pct']:.1f}%` |
| **Orbital Propagation** | 1,000 Sats Step Time | `{prop_data['scales_tested'][-1]['avg_step_duration_ms']:.2f} ms` |
| **Orbital Propagation** | Throughput | `{prop_data['scales_tested'][-1]['throughput_sats_per_sec']:.1f} sats/sec` |
| **Neural Bid Surrogate** | Single Inference P50 | `{ml_data['single_item_inference_ms']['p50']:.3f} ms` |
| **Neural Bid Surrogate** | Batch-64 Inference P50 | `{ml_data['batch_64_inference_ms']['p50']:.3f} ms` |
| **Neural Bid Surrogate** | Batch Throughput | `{ml_data['batch_64_inference_ms']['effective_throughput_inferences_per_sec']:.1f} inf/sec` |

## Files
- `scheduler.json`: CP-SAT multi-mission optimization latency and memory.
- `propagation.json`: SGP4 propagation throughput across constellation scale (12 to 1,000 satellites).
- `ml_inference.json`: BidValueMLP single-item and batch-64 inference latency distributions.
"""
    with open(baseline_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(baseline_readme)
        
    # Write top-level benchmarks README
    top_readme = """# ORBIT-X Benchmarks Suite

This directory contains reproducible empirical benchmarks across all subsystems of ORBIT-X:

```text
benchmarks/
├── baseline/              # Pre-production baseline measurements (Phase 0)
│   ├── scheduler.json
│   ├── propagation.json
│   ├── ml_inference.json
│   └── README.md
├── scheduler/             # CP-SAT scheduler load & scale benchmarks
├── propagation/           # SGP4 & ISL mesh propagation benchmarks
├── ml/                    # Neural surrogate, PINN, TreeSHAP latency
├── api/                   # REST API latency and throughput
├── kafka/                 # Event throughput, lag and consumer latency
├── redis/                 # Cache hit ratio, lock latency, failover timing
└── load/                  # k6 end-to-end stress & emergency storm results
```

All figures reported in documentation and papers are directly generated from executable benchmarking scripts.
"""
    with open(benchmarks_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(top_readme)
        
    print(f"\\nBaseline benchmarks written successfully to {baseline_dir}")

if __name__ == "__main__":
    main()
