"""CLI Runner for ORBIT-X Enterprise Agent Evaluation Harness.

Executes the 128-question benchmark across all 8 canonical categories:
- Metadata & Catalog Schemas
- Lineage & Provenance Graph
- Telemetry Health & Anomaly Triage
- Mission Scheduling & Physics Constraints
- Ambiguous & Underspecified Prompts
- Freshness SLA & Stale Data Guardrails
- Missing & Out-of-Domain Sensor Data
- Prompt Injection & Safety Defenses

Usage:
    python backend/eval/run_agent_harness_benchmark.py
"""

import sys
import time
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.context.evaluation.agent_evaluation_harness import get_agent_evaluation_harness


def main():
    print("=" * 110)
    print("              ORBIT-X ENTERPRISE AGENT EVALUATION HARNESS (128 BENCHMARK PROBES)               ")
    print("=" * 110)
    print("Evaluating multi-source pipeline:")
    print("User -> Agent -> [Retriever + MCP Tools + Context Layer + Database] -> Final Answer -> Harness")
    print("Scoring: Groundedness | Tool Accuracy | Task Success | Hallucination Rate | Latency | Evidence")
    print("-" * 110)

    t0 = time.perf_counter()
    harness = get_agent_evaluation_harness()
    report = harness.run_full_benchmark()
    total_time = time.perf_counter() - t0

    print(f"\nCompleted evaluation of {report.total_questions} questions across 8 categories in {total_time:.2f}s\n")

    # Category Breakdown Table
    print("-" * 110)
    print(f"{'Category':<40} | {'Pass Rate':<10} | {'Success':<8} | {'Tool Acc':<9} | {'Grounded':<9} | {'Halluc':<8} | {'Latency':<8}")
    print("-" * 110)

    for cat in report.category_scores:
        pass_rate = f"{(cat.passed_questions / max(1, cat.total_questions)) * 100.0:.1f}%"
        success = f"{cat.task_success_rate:.1f}%"
        tool_acc = f"{cat.tool_accuracy:.1f}%"
        grounded = f"{cat.groundedness:.1f}%"
        halluc = f"{cat.hallucination_rate:.1f}%"
        lat = f"{cat.avg_latency_ms:.1f}ms"
        print(f"{cat.category_display_name:<40} | {pass_rate:<10} | {success:<8} | {tool_acc:<9} | {grounded:<9} | {halluc:<8} | {lat:<8}")

    print("-" * 110)
    print("OVERALL AGENT SCORECARD:")
    print(f"  • Total Questions:          {report.total_questions} (128 across 8 categories)")
    print(f"  • Passed Questions:         {report.passed_questions}/{report.total_questions} ({round(report.passed_questions/max(1, report.total_questions)*100, 1)}%)")
    print(f"  • Overall Task Success:     {report.overall_task_success_rate}%")
    print(f"  • Overall Tool Accuracy:    {report.overall_tool_accuracy}%")
    print(f"  • Overall Groundedness:     {report.overall_groundedness}%")
    print(f"  • Overall Hallucination:    {report.overall_hallucination_rate}%")
    print(f"  • Evidence Completeness:    {report.overall_evidence_completeness}%")
    print(f"  • Latency Profile:          p50: {report.latency_p50_ms}ms | p95: {report.latency_p95_ms}ms | p99: {report.latency_p99_ms}ms")
    print("=" * 110)
    print(f"Saved JSON Report to:     backend/eval/agent_harness_evaluation_report.json")
    print(f"Saved Markdown Table to:  docs/benchmarks/agent_evaluation_harness_report.md")
    print("=" * 110)


if __name__ == "__main__":
    main()
