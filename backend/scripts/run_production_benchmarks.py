"""Reproducible Production Benchmarks Suite for ORBIT-X Distributed Architecture."""

import os
import sys
import time
import json
import asyncio
import numpy as np
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.redis_client import AsyncRedisManager
from app.core.kafka_client import AsyncKafkaManager
from app.core.events import MissionCreatedEvent, TelemetryReceivedEvent, TOPIC_MISSIONS, TOPIC_TELEMETRY
from app.simulation.benchmark import run_benchmark_comparison
from app.intelligence.bid_value_network import get_bid_value_predictor
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import init_db


async def benchmark_api(iterations: int = 100):
    print("1. Benchmarking FastAPI REST & Metrics Endpoints...")
    await init_db()
    latencies_health = []
    latencies_missions = []

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Warmup
        for _ in range(5):
            await client.get("/health")
            await client.get("/api/missions")

        # Benchmark /health
        for _ in range(iterations):
            t0 = time.perf_counter()
            res = await client.get("/health")
            t1 = time.perf_counter()
            if res.status_code == 200:
                latencies_health.append((t1 - t0) * 1000.0)

        # Benchmark /api/missions intake
        for i in range(iterations // 2):
            t0 = time.perf_counter()
            res = await client.post("/api/missions/random")
            t1 = time.perf_counter()
            if res.status_code == 200:
                latencies_missions.append((t1 - t0) * 1000.0)

    h_arr = np.array(latencies_health)
    m_arr = np.array(latencies_missions)

    return {
        "benchmark": "REST API Endpoint Latency",
        "health_probe_latency_ms": {
            "iterations": len(latencies_health),
            "mean": round(float(np.mean(h_arr)), 3),
            "p50": round(float(np.percentile(h_arr, 50)), 3),
            "p95": round(float(np.percentile(h_arr, 95)), 3),
            "p99": round(float(np.percentile(h_arr, 99)), 3),
            "throughput_req_per_sec": round(float(1000.0 / np.mean(h_arr)), 1),
        },
        "mission_creation_latency_ms": {
            "iterations": len(latencies_missions),
            "mean": round(float(np.mean(m_arr)), 3),
            "p50": round(float(np.percentile(m_arr, 50)), 3),
            "p95": round(float(np.percentile(m_arr, 95)), 3),
            "p99": round(float(np.percentile(m_arr, 99)), 3),
            "throughput_req_per_sec": round(float(1000.0 / np.mean(m_arr)), 1),
        },
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


async def benchmark_redis(iterations: int = 500):
    print("2. Benchmarking Redis State Caching & Distributed Locks...")
    mgr = AsyncRedisManager()
    await mgr.connect()

    set_latencies = []
    get_latencies = []
    lock_latencies = []

    # Caching benchmark
    sample_data = {"battery": 88.5, "temp": 32.0, "status": "NOMINAL"}
    for i in range(iterations):
        key = f"telemetry:sat:BENCH-{i}"
        t0 = time.perf_counter()
        await mgr.set_json(key, sample_data, expire_seconds=60)
        t1 = time.perf_counter()
        set_latencies.append((t1 - t0) * 1000.0)

        t2 = time.perf_counter()
        _ = await mgr.get_json(key)
        t3 = time.perf_counter()
        get_latencies.append((t3 - t2) * 1000.0)

    # Distributed locking benchmark
    for i in range(iterations // 2):
        res_key = f"satellite:LOCK-BENCH-{i}"
        t0 = time.perf_counter()
        async with mgr.distributed_lock(res_key, timeout_s=1.0, lease_s=5.0):
            pass
        t1 = time.perf_counter()
        lock_latencies.append((t1 - t0) * 1000.0)

    s_arr = np.array(set_latencies)
    g_arr = np.array(get_latencies)
    l_arr = np.array(lock_latencies)

    return {
        "benchmark": "Redis Caching & Distributed Locking",
        "cache_set_latency_ms": {
            "iterations": iterations,
            "mean": round(float(np.mean(s_arr)), 3),
            "p50": round(float(np.percentile(s_arr, 50)), 3),
            "p95": round(float(np.percentile(s_arr, 95)), 3),
            "p99": round(float(np.percentile(s_arr, 99)), 3),
            "throughput_ops_per_sec": round(float(1000.0 / np.mean(s_arr)), 1),
        },
        "cache_get_latency_ms": {
            "iterations": iterations,
            "mean": round(float(np.mean(g_arr)), 3),
            "p50": round(float(np.percentile(g_arr, 50)), 3),
            "p95": round(float(np.percentile(g_arr, 95)), 3),
            "p99": round(float(np.percentile(g_arr, 99)), 3),
            "throughput_ops_per_sec": round(float(1000.0 / np.mean(g_arr)), 1),
        },
        "lock_acquire_release_latency_ms": {
            "iterations": len(lock_latencies),
            "mean": round(float(np.mean(l_arr)), 3),
            "p50": round(float(np.percentile(l_arr, 50)), 3),
            "p95": round(float(np.percentile(l_arr, 95)), 3),
            "p99": round(float(np.percentile(l_arr, 99)), 3),
            "throughput_locks_per_sec": round(float(1000.0 / np.mean(l_arr)), 1),
        },
        "stats": mgr.get_stats(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


async def benchmark_kafka(iterations: int = 500):
    print("3. Benchmarking Kafka Event Backbone & Pipeline...")
    kafka = AsyncKafkaManager()
    await kafka.start()

    received = 0
    async def handler(event):
        nonlocal received
        received += 1

    kafka.register_handler(TOPIC_TELEMETRY, handler, auto_idempotency=False)

    publish_latencies = []
    for i in range(iterations):
        evt = TelemetryReceivedEvent(
            satellite_id=f"SAT-{i:04d}",
            payload={"battery": 90.0, "step": i},
        )
        t0 = time.perf_counter()
        await kafka.publish(TOPIC_TELEMETRY, evt)
        t1 = time.perf_counter()
        publish_latencies.append((t1 - t0) * 1000.0)

    # Let async consumer process all events
    await asyncio.sleep(0.3)

    p_arr = np.array(publish_latencies)

    return {
        "benchmark": "Kafka Event Backbone Pipeline",
        "iterations": iterations,
        "events_dispatched": iterations,
        "events_consumed": received,
        "publish_latency_ms": {
            "mean": round(float(np.mean(p_arr)), 3),
            "p50": round(float(np.percentile(p_arr, 50)), 3),
            "p95": round(float(np.percentile(p_arr, 95)), 3),
            "p99": round(float(np.percentile(p_arr, 99)), 3),
            "throughput_events_per_sec": round(float(1000.0 / np.mean(p_arr)), 1),
        },
        "stats": kafka.get_stats(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def benchmark_scheduler_and_ml():
    print("4. Benchmarking CP-SAT Multi-Mission Optimizer & Neural Surrogate...")
    predictor = get_bid_value_predictor()
    features = np.array([0.80, 0.85, 0.70, 0.10, 1.0, 0.90, 1.0, 0.60, 0.15, 0.25], dtype=np.float32)
    batch = np.tile(features, (64, 1)).astype(np.float32)

    ml_single_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        predictor.predict_single(features)
        t1 = time.perf_counter()
        ml_single_times.append((t1 - t0) * 1000.0)

    ml_batch_times = []
    for _ in range(100):
        t0 = time.perf_counter()
        predictor.predict_batch(batch)
        t1 = time.perf_counter()
        ml_batch_times.append((t1 - t0) * 1000.0)

    sched_times = []
    for i in range(3):
        t0 = time.perf_counter()
        run_benchmark_comparison(seed=500 + i, num_missions=24)
        t1 = time.perf_counter()
        sched_times.append((t1 - t0) * 1000.0)

    s_arr = np.array(sched_times)
    ms_arr = np.array(ml_single_times)
    mb_arr = np.array(ml_batch_times)

    return {
        "benchmark": "CP-SAT Optimizer & PyTorch Neural Surrogate",
        "cpsat_scheduler_latency_ms": {
            "iterations": len(sched_times),
            "missions_per_run": 24,
            "mean": round(float(np.mean(s_arr)), 2),
            "p50": round(float(np.percentile(s_arr, 50)), 2),
            "p95": round(float(np.percentile(s_arr, 95)), 2),
        },
        "neural_surrogate_single_inference_ms": {
            "mean": round(float(np.mean(ms_arr)), 3),
            "p50": round(float(np.percentile(ms_arr, 50)), 3),
            "p95": round(float(np.percentile(ms_arr, 95)), 3),
            "throughput_inferences_per_sec": round(float(1000.0 / np.mean(ms_arr)), 1),
        },
        "neural_surrogate_batch64_inference_ms": {
            "mean": round(float(np.mean(mb_arr)), 3),
            "p50": round(float(np.percentile(mb_arr, 50)), 3),
            "p95": round(float(np.percentile(mb_arr, 95)), 3),
            "effective_throughput_inferences_per_sec": round(float((64 * 1000.0) / np.mean(mb_arr)), 1),
        },
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


async def main():
    benchmarks_dir = ROOT_DIR / "benchmarks"
    for subdir in ("api", "redis", "kafka", "scheduler"):
        (benchmarks_dir / subdir).mkdir(parents=True, exist_ok=True)

    api_res = await benchmark_api(iterations=100)
    with open(benchmarks_dir / "api" / "api_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(api_res, f, indent=2)

    redis_res = await benchmark_redis(iterations=500)
    with open(benchmarks_dir / "redis" / "redis_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(redis_res, f, indent=2)

    kafka_res = await benchmark_kafka(iterations=500)
    with open(benchmarks_dir / "kafka" / "kafka_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(kafka_res, f, indent=2)

    sched_res = benchmark_scheduler_and_ml()
    with open(benchmarks_dir / "scheduler" / "scheduler_benchmark.json", "w", encoding="utf-8") as f:
        json.dump(sched_res, f, indent=2)

    print("\n" + "=" * 65)
    print("   ALL PRODUCTION BENCHMARKS COMPLETED & PERSISTED")
    print("=" * 65)
    print(f"API Latency:        P50 = {api_res['health_probe_latency_ms']['p50']:.2f} ms | Throughput = {api_res['health_probe_latency_ms']['throughput_req_per_sec']:.0f} req/s")
    print(f"Redis Operations:   P50 = {redis_res['cache_set_latency_ms']['p50']:.3f} ms | Throughput = {redis_res['cache_set_latency_ms']['throughput_ops_per_sec']:.0f} ops/s")
    print(f"Kafka Events:       P50 = {kafka_res['publish_latency_ms']['p50']:.3f} ms | Throughput = {kafka_res['publish_latency_ms']['throughput_events_per_sec']:.0f} evt/s")
    print(f"Neural Surrogate:   P50 = {sched_res['neural_surrogate_single_inference_ms']['p50']:.3f} ms | Batch Throughput = {sched_res['neural_surrogate_batch64_inference_ms']['effective_throughput_inferences_per_sec']:.0f} inf/s")


if __name__ == "__main__":
    asyncio.run(main())
