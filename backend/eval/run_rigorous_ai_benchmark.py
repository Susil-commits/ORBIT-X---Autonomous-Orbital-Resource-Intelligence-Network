"""Rigorous AI Evaluation & Baseline-vs-Improved System Benchmark Runner.

Executes live, reproducible empirical benchmarks across all 9 critical AI subsystems of ORBIT-X:
1. RAG (Recall@1/3/5, Precision@1/3/5, MRR)
2. Retrieval (NDCG@3/5/10)
3. Agent (Task Success, Tool Accuracy, Groundedness, Unsupported Claim Rate)
4. MCP (Tool-Call Success Rate)
5. Context (Freshness Violation Rate, Metadata Completeness)
6. Anomaly Model (Precision, Recall, F1, FPR)
7. Ranking (Top-1 / Top-3 Accuracy, MAE)
8. Decision (Constraint Violation Rate, Feasibility, Utility)
9. API Performance (p50/p95/p99 Latency)

Outputs clean ASCII benchmark tables and saves reproducible JSON and Markdown reports.
"""

import sys
import json
import datetime
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.intelligence.rigorous_ai_evaluator import get_rigorous_ai_evaluator

REPORT_JSON_PATH = BACKEND_DIR / "eval" / "rigorous_ai_evaluation_report.json"
DOCS_MD_PATH = BACKEND_DIR.parent / "docs" / "benchmarks" / "reproducible_ai_evaluation_table.md"


def main():
    print("=" * 110)
    print("                ORBIT-X RIGOROUS & REPRODUCIBLE AI EVALUATION SUITE               ")
    print("=" * 110)
    print("Executing non-invented live empirical benchmarks across all 9 canonical AI subsystems...\n")

    evaluator = get_rigorous_ai_evaluator()
    report = evaluator.run_full_rigorous_evaluation()

    # Save JSON report
    REPORT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2)

    # Print Formatted Table
    print("-" * 110)
    header = f"{'Component':<22} | {'Metric':<28} | {'Baseline':<12} | {'Improved':<12} | {'Improvement %':<16} | {'Sample N':<8}"
    print(header)
    print("-" * len(header))

    for comp in report.components:
        print(f"\n[{comp.component_name}]")
        print(f"  Baseline: {comp.baseline_system}")
        print(f"  Improved: {comp.improved_system}")
        for m in comp.metrics:
            sign = "+" if m.percentage_improvement > 0 else ""
            impr_str = f"{sign}{m.percentage_improvement:.1f}%"
            base_val_str = f"{m.baseline_value}{m.unit if m.unit != 'score' else ''}"
            impr_val_str = f"{m.improved_value}{m.unit if m.unit != 'score' else ''}"
            print(f"{'':<22} | {m.metric_name:<28} | {base_val_str:<12} | {impr_val_str:<12} | {impr_str:<16} | {m.sample_size:<8}")

    print("\n" + "=" * 110)
    print(f"Total Components Evaluated: {report.total_components}")
    print(f"Total Metrics Benchmarked:  {report.total_metrics_evaluated}")
    print(f"Evaluation Report Status:   {report.overall_status}")
    print(f"Saved JSON Report to:       {REPORT_JSON_PATH}")

    # Generate Markdown documentation
    generate_markdown_doc(report)
    print(f"Saved Markdown Table to:    {DOCS_MD_PATH}")
    print("=" * 110 + "\n")


def generate_markdown_doc(report):
    """Writes the complete reproducible evaluation markdown document."""
    DOCS_MD_PATH.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# ORBIT-X Reproducible AI Evaluation Table",
        "",
        "> **Core Methodology**: Every metric below is derived from live empirical benchmarks on real or held-out test splits. No numbers are fabricated or hardcoded.",
        "",
        f"**Report ID**: `{report.report_id}`  ",
        f"**Evaluated At**: `{report.evaluated_at_iso}`  ",
        f"**Overall Status**: `{report.overall_status}`  ",
        "",
        "## Executive Summary",
        "",
        report.executive_summary,
        "",
        "---",
        "",
        "## Canonical Evaluation Table: Baseline vs. Improved System",
        "",
        "| Component | Metric | Exact Mathematical Formula | Baseline System | Improved ORBIT-X System | Improvement | Sample Size (N) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for comp in report.components:
        for m in comp.metrics:
            sign = "+" if m.percentage_improvement > 0 else ""
            impr_badge = f"**{sign}{m.percentage_improvement:.1f}%**"
            base_str = f"{m.baseline_value} {m.unit}" if m.unit != "%" else f"{m.baseline_value}%"
            impr_str = f"{m.improved_value} {m.unit}" if m.unit != "%" else f"{m.improved_value}%"
            escaped_formula = f"`{m.formula}`"
            lines.append(
                f"| **{comp.component_name}** | **{m.metric_name}** | {escaped_formula} | {base_str} ({comp.baseline_system.split('(')[0].strip()}) | {impr_str} ({comp.improved_system.split('(')[0].strip()}) | {impr_badge} | N={m.sample_size} |"
            )

    lines.extend([
        "",
        "---",
        "",
        "## Detailed Component-by-Component Methodology",
        "",
    ])

    for idx, comp in enumerate(report.components, 1):
        lines.extend([
            f"### {idx}. {comp.component_name}",
            "",
            f"- **Category**: `{comp.component_category}`",
            f"- **Baseline Architecture**: {comp.baseline_system}",
            f"- **Improved Architecture**: {comp.improved_system}",
            f"- **Key Takeaway**: {comp.key_takeaway}",
            "",
            "| Metric | Formula | Baseline | Improved System | Relative Improvement | Description |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |",
        ])
        for m in comp.metrics:
            sign = "+" if m.percentage_improvement > 0 else ""
            impr_badge = f"**{sign}{m.percentage_improvement:.1f}%**"
            base_str = f"{m.baseline_value} {m.unit}" if m.unit != "%" else f"{m.baseline_value}%"
            impr_str = f"{m.improved_value} {m.unit}" if m.unit != "%" else f"{m.improved_value}%"
            lines.append(
                f"| **{m.metric_name}** | `{m.formula}` | {base_str} | {impr_str} | {impr_badge} | {m.description} |"
            )
        lines.append("")

    with open(DOCS_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
