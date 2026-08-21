# ORBIT-X Benchmarks Suite

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
