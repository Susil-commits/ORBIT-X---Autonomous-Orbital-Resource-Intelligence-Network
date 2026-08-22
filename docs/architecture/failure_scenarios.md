# System Resilience & Chaos Engineering: 15 Failure Scenarios

## 1. Overview
This document specifies the failure recovery and resilience matrix for ORBIT-X across 15 critical operational and infrastructure failure scenarios. Every scenario details the input trigger, failure manifestation, automated detection mechanism, fallback strategy, self-healing recovery, and final operational outcome.

---

## 2. Failure Matrix

| # | Scenario | Trigger / Input | Failure Mode | Automated Detection | Fallback Strategy | Self-Healing / Recovery | Final Result |
|---|---|---|---|---|---|---|---|
| **1** | **Normal Operation** | Continuous telemetry stream | None | Health probes return 200 OK | N/A (Standard Hybrid ML+CP-SAT) | Nominal pipeline | Zero violations; <1ms inference |
| **2** | **Missing Telemetry** | Drop in sensor feed for node S-04 | Null/NaN feature inputs | Pydantic validator & DataQualityAgent | Impute with last known valid state + uncertainty penalty | Re-query sensor stream on next tick | Request processed with lowered confidence flag |
| **3** | **Stale Telemetry** | Telemetry timestamp >15 min old | Outdated power/thermal estimates | `freshness_seconds > 900` check | Down-weight node bid score; prefer fresh nodes | Trigger telemetry poll over ISL link | Avoids deep-discharge during eclipse |
| **4** | **Schema Change** | Upstream type drift (float -> string) | Parsing exception on ingestion | Schema validation exception gate | Log alert, isolate corrupt field, use fallback schema | Trigger Data Quality Alert to operator | Ingestion continues without pipeline crash |
| **5** | **Neural Model Failure** | Out-of-memory or CUDA error | Inference exception | Try/catch wrapper around PyTorch runtime | Fall back to Greedy EDF or Ridge Linear baseline | Restart PyTorch worker pool asynchronously | Decisions delivered at heuristic accuracy |
| **6** | **Agent Tool Failure** | Downstream API timeout on `get_anomalies` | Tool execution exception | Tool error handler in agent loop | Return structured error payload; prompt LLM to replan | Retry tool with exponential backoff (max 2 retries) | Agent informs user of partial data with caveat |
| **7** | **PostgreSQL Unavailable** | Database connection drop | Persistence failure on decision write | SQLAlchemy connection pool error | Write decision record to Redis append-only buffer | Background worker flushes Redis queue upon DB reconnect | Zero data loss; audit trail preserved |
| **8** | **Redis Unavailable** | Redis service restart | Cache misses & pub/sub disruption | Redis connection timeout | Fall back to in-memory local Python cache / direct DB query | Auto-reconnect with circuit breaker pattern | Minor latency increase (+5ms); zero downtime |
| **9** | **Optimizer Timeout** | NP-hard multi-target constraint conflict | CP-SAT solver exceeds 2000ms limit | Solver wall-clock timeout interrupt | Return best feasible incumbent solution found so far | Adjust solver search parameter limits | Feasible schedule returned without hard violations |
| **10**| **High Request Load** | Burst of 2,500 simultaneous requests | Queue buildup & latency spike | Rate limiter & queue depth metric alert | Enable candidate pruning; prioritize Priority-1 tasks | Horizontal pod autoscaler triggers replica scale-up | High-priority missions served within SLA |
| **11**| **Conflicting Constraints**| 2 priority-1 tasks at identical coordinates | Unsolvable mutual exclusion | CP-SAT returns `INFEASIBLE` | Soften lower-priority soft objectives; alert operator | Re-run solver with relaxed look-angle bounds | High-value task scheduled; 2nd task queued |
| **12**| **Invalid User Query** | Gibberish or adversarial prompt injection | Intent classification failure | Intent classifier confidence < 0.40 | Return clarification prompt with suggested queries | Guide user with structured quick-action chips | Prevent prompt injection & hallucination |
| **13**| **LLM Unavailable** | External LLM API rate-limit / outage | RAG commentary generation fails | API timeout / 503 response | Fall back to deterministic template commentary generator | Local Ollama fallback or wait for API recovery | Operator receives structured text explanation |
| **14**| **Retrieval Failure** | Vector DB index miss or empty search | Context builder receives 0 docs | `len(retrieved_docs) == 0` | Fall back to structured SQL metadata query | Rebuild vector embedding index in background | Accurate grounded answer from SQL catalog |
| **15**| **Tool Loop Hang** | Circular tool calling pattern | Agent loop exceeds max steps | `step_count >= MAX_STEPS (5)` guard | Terminate loop; synthesize answer from gathered evidence | Log trace for agent evaluation | Prevents runaway latency and token spend |
