# ORBIT-X Pre-Production Baseline Benchmarks

These benchmarks capture the empirical performance profile of the ORBIT-X intelligence engine before architectural upgrades (Kafka, Redis, BullMQ, Observability, Kubernetes).

## Summary Snapshot

| Subsystem | Metric | Baseline Value |
|---|---|---|
| **CP-SAT Scheduler** | P50 Latency | `21734.88 ms` |
| **CP-SAT Scheduler** | P95 Latency | `21914.98 ms` |
| **CP-SAT Scheduler** | Success Rate | `100.0%` |
| **Orbital Propagation** | 1,000 Sats Step Time | `21.84 ms` |
| **Orbital Propagation** | Throughput | `45791.4 sats/sec` |
| **Neural Bid Surrogate** | Single Inference P50 | `0.075 ms` |
| **Neural Bid Surrogate** | Batch-64 Inference P50 | `0.109 ms` |
| **Neural Bid Surrogate** | Batch Throughput | `432929.7 inf/sec` |

## Files
- `scheduler.json`: CP-SAT multi-mission optimization latency and memory.
- `propagation.json`: SGP4 propagation throughput across constellation scale (12 to 1,000 satellites).
- `ml_inference.json`: BidValueMLP single-item and batch-64 inference latency distributions.
