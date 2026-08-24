# ORBIT-X Agent Evaluation Harness Report

> **Multi-Source Autonomous Agent Evaluation**: Measures Groundedness, Tool Accuracy, Task Success, Hallucination Rate, Latency, and Evidence Completeness across 128 curated operational benchmark questions.

**Benchmark ID**: `HARNESS-20260824-171347`  
**Evaluated At**: `2026-08-24T17:13:47.128867+00:00`  
**Total Questions**: `128` (128 across 8 categories)  
**Passed Questions**: `128/128` (**100.0%**)  

## 1. Multi-Source Pipeline Architecture

```
                    ┌── Retriever (Hybrid Dense MiniLM-L6 + BM25 RRF)
                    ├── MCP Tools (FastMCP Tool Catalog)
User → Agent →──────┤
                    ├── Context Layer (Governed Context Graph & SLAs)
                    └── Database / Simulator (Telemetry & Decision Ledger)
                         ↓
                    Final Answer
                         ↓
                 Evaluation Harness
                         ↓
       ┌─────────────────┼─────────────────┐
       ↓                 ↓                 ↓
   Groundedness      Tool accuracy     Task success
       ↓                 ↓                 ↓
   Hallucination       Latency         Evidence
```

## 2. Overall Agent Scorecard

| Evaluation Dimension | Overall Score | Target Production SLA | Status |
| :--- | :--- | :--- | :--- |
| **Task Success Rate** | **100.0%** | $\ge 95.0\%$ | PASSED |
| **Tool-Selection Accuracy** | **100.0%** | $\ge 95.0\%$ | PASSED |
| **Groundedness** | **98.8%** | $\ge 95.0\%$ | PASSED |
| **Hallucination / Unsupported-Claim Rate** | **0.0%** | $\le 1.0\%$ | PASSED |
| **Evidence Completeness** | **90.3%** | $\ge 90.0\%$ | PASSED |
| **Pipeline Latency (p50)** | **0.01 ms** | $\le 20.0\text{ ms}$ | PASSED |
| **Pipeline Latency (p95)** | **0.01 ms** | $\le 50.0\text{ ms}$ | PASSED |
| **Pipeline Latency (p99)** | **0.03 ms** | $\le 120.0\text{ ms}$ | PASSED |

---

## 3. Category-by-Category Benchmark Breakdown (128 Questions)

| Question Category | Questions | Pass Rate | Task Success | Tool Accuracy | Groundedness | Hallucination Rate | Evidence Comp | Avg Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Metadata & Catalog Schemas** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 0.01 ms |
| **Lineage & Provenance Graph** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 87.5% | 0.01 ms |
| **Telemetry Health & Anomaly Triage** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 87.5% | 0.01 ms |
| **Mission Scheduling & Physics Constraints** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 87.5% | 0.01 ms |
| **Ambiguous & Underspecified Prompts** | N=16 | 100.0% | 100.0% | 100.0% | 90.0% | 0.0% | 65.6% | 0.0 ms |
| **Freshness SLA & Stale Data Guardrails** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 96.9% | 0.01 ms |
| **Missing & Out-of-Domain Sensor Data** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 97.5% | 0.01 ms |
| **Prompt Injection & Safety Defenses** | N=16 | 100.0% | 100.0% | 100.0% | 100.0% | 0.0% | 100.0% | 0.01 ms |

---

## 4. How Each Evaluation Metric is Calculated

### A. Groundedness
$$\text{Groundedness} = \frac{\text{Count of verifiable assertions backed by citations / telemetry}}{\text{Total factual assertions in agent response}}$$
- **Why it matters**: In flight critical space systems, ungrounded speculation can cause mission loss. The agent must cite active telemetry frames, catalog metadata, or lineage nodes for every fact.

### B. Tool Selection Accuracy
$$\text{Tool Accuracy} = \frac{|\text{Invoked Tools} \cap \text{Expected Expert Tools}|}{|\text{Expected Expert Tools}|}$$
- **Why it matters**: Evaluates whether the agent dispatches diagnostics to `get_anomaly`, optimization to `run_optimizer`, provenance to `get_lineage`, and metadata to `get_dataset_metadata` without inappropriate tool calls.

### C. Task Success Rate
$$\text{Task Success Rate} = \frac{\text{Correct, policy-compliant, safety-verified responses}}{\text{Total evaluated questions}}$$
- **Includes safety refusals**: For adversarial prompt injections and stale data violations, refusing the dangerous task is counted as a **success**.

### D. Hallucination / Unsupported-Claim Rate
$$\text{Hallucination Rate} = \frac{\text{Responses with fabricated satellite IDs or ungrounded statistics}}{\text{Total evaluated questions}}$$
- Evaluated through strict entity extraction against active constellation registry (`SAT-01` to `SAT-12`).

### E. Evidence Completeness
$$\text{Evidence Completeness} = \frac{\text{Matched 5-Pillar Evidence Types}}{\text{Required Evidence Types}}$$
- Covers the 5 pillars: **Telemetry Context**, **Lineage Trace**, **Physics Invariant**, **SHAP Attribution**, and **Governance Audit**.

---

## 5. How to Reproduce via CLI and API

```powershell
# Run the complete 128-question harness via CLI:
backend\.venv\Scripts\python.exe backend/eval/run_agent_harness_benchmark.py

# Run the automated PyTest test suite:
backend\.venv\Scripts\python.exe -m pytest backend/tests/test_agent_evaluation_harness.py -v

# Trigger via REST API:
curl -X POST http://localhost:8000/api/benchmarks/agent-harness/run
```