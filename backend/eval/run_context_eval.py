"""Formal Context Evaluation & Governance Quality Harness for ORBIT-X.

Evaluates deterministic, empirical context quality across all 5 authoritative dimensions:
1. Metadata Completeness: Ratio of populated required schema & governance fields.
2. Lineage Coverage: Fraction of canonical 10-node context graph entities connected via active provenance DAG edges.
3. Freshness SLA Compliance: Ratio of assets satisfying latency and real-time freshness thresholds.
4. Retrieval Groundedness: Proportion of discovery queries returning certified VERIFIED schema-matched assets.
5. Stale Context Rate: Rate of deprecated, uncalibrated, or out-of-SLA assets across the catalog.
6. Composite Quality Index: Weighted multi-dimensional context trust score.

Outputs detailed results and saves 'backend/eval/context_evaluation_report.json'.
"""

import sys
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple

# Ensure backend and root directories are in sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


from context.evaluation import (
    evaluate_metadata_completeness,
    evaluate_lineage_coverage,
    evaluate_freshness,
    evaluate_retrieval_groundedness,
    evaluate_stale_context_rate,
    evaluate_all_context_metrics,
    ComprehensiveContextEvaluationReport,
)

EVAL_DIR = Path(__file__).resolve().parent
REPORT_FILE = EVAL_DIR / "context_evaluation_report.json"

# Authoritative Quality Acceptance Gates
QUALITY_GATES = {
    "min_metadata_completeness_pct": 90.0,
    "min_lineage_coverage_pct": 90.0,
    "min_freshness_sla_compliance_pct": 75.0,
    "min_retrieval_groundedness_pct": 80.0,
    "max_stale_context_rate_pct": 25.0,
    "min_composite_quality_score_pct": 85.0,
}


def run_formal_context_evaluation() -> Tuple[ComprehensiveContextEvaluationReport, Dict[str, Any], bool]:
    """
    Executes the formal context evaluation suite, compares against quality gates,
    and returns (report, gate_results, has_failures).
    """
    print("=" * 72)
    print("       ORBIT-X FORMAL CONTEXT EVALUATION & GOVERNANCE HARNESS       ")
    print("=" * 72)

    report = evaluate_all_context_metrics()

    meta_pct = report.metadata_completeness.score_pct
    lineage_pct = report.lineage_coverage.score_pct
    fresh_pct = report.freshness.score_pct
    ground_pct = report.retrieval_groundedness.score_pct
    stale_pct = report.stale_context_rate.rate_pct
    comp_pct = report.composite_quality_score_pct

    gate_checks = [
        ("Metadata Completeness", meta_pct, ">=", QUALITY_GATES["min_metadata_completeness_pct"], meta_pct >= QUALITY_GATES["min_metadata_completeness_pct"]),
        ("Lineage Coverage", lineage_pct, ">=", QUALITY_GATES["min_lineage_coverage_pct"], lineage_pct >= QUALITY_GATES["min_lineage_coverage_pct"]),
        ("Freshness SLA Compliance", fresh_pct, ">=", QUALITY_GATES["min_freshness_sla_compliance_pct"], fresh_pct >= QUALITY_GATES["min_freshness_sla_compliance_pct"]),
        ("Retrieval Groundedness", ground_pct, ">=", QUALITY_GATES["min_retrieval_groundedness_pct"], ground_pct >= QUALITY_GATES["min_retrieval_groundedness_pct"]),
        ("Stale Context Rate", stale_pct, "<=", QUALITY_GATES["max_stale_context_rate_pct"], stale_pct <= QUALITY_GATES["max_stale_context_rate_pct"]),
        ("Composite Quality Index", comp_pct, ">=", QUALITY_GATES["min_composite_quality_score_pct"], comp_pct >= QUALITY_GATES["min_composite_quality_score_pct"]),
    ]

    print("\n" + "-" * 72)
    print(f"{'Context Quality Dimension':<28} | {'Measured':<10} | {'Gate / SLA':<12} | {'Status':<8}")
    print("-" * 72)

    has_failures = False
    gate_summary = {}

    for name, val, op, threshold, passed in gate_checks:
        status_str = "PASS" if passed else "FAIL"
        if not passed:
            has_failures = True
        gate_summary[name] = {
            "measured_pct": val,
            "operator": op,
            "threshold_pct": threshold,
            "passed": passed,
        }
        print(f"{name:<28} | {val:>7.1f}%   | {op} {threshold:>5.1f}%    | {status_str:<8}")

    print("-" * 72)

    # Detailed Summary Breakdown
    print("\n[Detailed Dimension Evidence]")
    print(f"  • Metadata Fields Populated: {report.metadata_completeness.populated_fields} / {report.metadata_completeness.total_expected_fields} ({report.metadata_completeness.evaluated_assets_count} assets)")
    print(f"  • Lineage DAG Connectivity:  {report.lineage_coverage.connected_nodes} / {report.lineage_coverage.total_canonical_nodes} canonical nodes connected ({report.lineage_coverage.total_edges} edges)")
    print(f"  • SLA Compliant Entities:    {report.freshness.compliant_entities_count} / {report.freshness.total_evaluated_entities} entities within max latency SLA")
    print(f"  • Grounded Retrieval Probes:  {report.retrieval_groundedness.grounded_hits} / {report.retrieval_groundedness.total_probes} probes verified")
    print(f"  • Stale / Deprecated Assets: {report.stale_context_rate.stale_entities_count} / {report.stale_context_rate.total_evaluated_entities} flagged for safe exclusion")

    report_payload = {
        "evaluation_title": "ORBIT-X Formal Context Evaluation Report",
        "evaluated_at_iso": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "overall_status": "PASSED" if not has_failures else "FAILED_GATES",
        "quality_gates": QUALITY_GATES,
        "summary_scores": {
            "metadata_completeness_pct": meta_pct,
            "lineage_coverage_pct": lineage_pct,
            "freshness_sla_compliance_pct": fresh_pct,
            "retrieval_groundedness_pct": ground_pct,
            "stale_context_rate_pct": stale_pct,
            "composite_quality_score_pct": comp_pct,
        },
        "gate_results": gate_summary,
        "detailed_metrics": report.model_dump(),
    }

    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report_payload, f, indent=2)

    print("\n" + "=" * 72)
    final_status_msg = "ALL CONTEXT QUALITY GATES PASSED (100% COMPLIANT)" if not has_failures else "CONTEXT QUALITY GATES FAILED"
    print(f"RESULT: {final_status_msg}")
    print(f"Report saved to: {REPORT_FILE}")
    print("=" * 72 + "\n")

    return report, gate_summary, has_failures


if __name__ == "__main__":
    _, _, failed = run_formal_context_evaluation()
    sys.exit(1 if failed else 0)
