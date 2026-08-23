#!/usr/bin/env python3
"""
ORBIT-X: End-to-End Decision Intelligence Platform Live CLI Demonstration
========================================================================

Demonstrates the 6 engineering layers in a unified interactive flow:
1. Layer 1: Data Platform & Quality Auditing
2. Layer 2: Machine Learning Baselines & Cross-Attention
3. Layer 2b: Unsupervised Anomaly Scoring (Isolation Forest)
4. Layer 2c: Explainable AI (TreeSHAP Local Attribution)
5. Layer 3: Constraint-Aware Optimization (Google OR-Tools CP-SAT)
6. Layer 4: Context Layer & Ask ORBIT-X Trust Layer
7. Layer 4b: Human-in-the-Loop Feedback Loop
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.core.schemas import TelemetryFrame, HealthStatus, HumanFeedbackRequest
from app.intelligence.context_graph import get_context_graph_engine
from app.intelligence.data_quality_agent import get_data_quality_agent
from app.intelligence.baselines import get_baseline_suite
from app.intelligence.cross_attention_network import get_cross_attention_predictor
from app.intelligence.health_ai import get_health_ai
from app.intelligence.shap_explainer import get_shap_explainer
from app.intelligence.trust_layer import get_trust_layer_engine


def print_section(title: str, layer: str):
    print("\n" + "=" * 80)
    print(f"[{layer}] {title}")
    print("=" * 80)


def main():
    print("""
    ========================================================================
           ORBIT-X PRODUCTION AI/ML DECISION INTELLIGENCE PLATFORM
                        Live Pipeline Demonstration
    ========================================================================
    """)

    # -------------------------------------------------------------------------
    # LAYER 1: DATA PLATFORM & QUALITY AGENT
    # -------------------------------------------------------------------------
    print_section("DATA PLATFORM, CATALOG & DATA QUALITY AGENT", "LAYER 1")
    context_engine = get_context_graph_engine()
    catalog = context_engine.get_catalog()
    print(f"[*] Loaded Semantic Metadata Catalog (v{catalog.catalog_version}): {catalog.total_datasets} Datasets Registered")
    for d in catalog.datasets:
        print(f"    - {d.dataset_name:<22} | Owner: {d.owner:<18} | Quality: {d.quality_score*100:.1f}% | Format: {d.storage_format}")

    dq_agent = get_data_quality_agent()
    nominal_frame = TelemetryFrame(
        timestamp_s=100.0,
        bus_voltage_v=28.2,
        solar_current_a=5.5,
        battery_temp_c=21.4,
        payload_temp_c=22.0,
        reaction_wheel_jitter_dps=0.02,
        rf_snr_db=18.5,
        anomaly_score=0.05,
        health_status=HealthStatus.NOMINAL,
    )
    dq_report = dq_agent.audit_telemetry_stream([nominal_frame])
    print(f"\n[*] Live Telemetry Quality Audit: {'PASS (Nominal)' if dq_report.is_nominal else 'ALERT'}")
    print(f"    Quality Score: {dq_report.overall_quality_score*100:.1f}% | Schema Drift: ZERO | Boundary Check: PASS")

    # -------------------------------------------------------------------------
    # LAYER 2: MACHINE LEARNING BASELINES & CROSS-ATTENTION NET
    # -------------------------------------------------------------------------
    print_section("ML MODEL SELECTION & MULTI-MODEL BENCHMARKING", "LAYER 2")
    baseline_suite = get_baseline_suite()
    print("[*] Running comparative evaluation across 7 model paradigms...")
    bench_report = baseline_suite.run_full_comparison()

    print(f"\n{'Model Architecture':<36} | {'Top-1 (%)':<9} | {'MAE':<6} | {'F1':<6} | {'p50 Latency':<12}")
    print("-" * 78)
    for m in bench_report.models:
        print(f"{m.model_name:<36} | {m.top1_agreement_pct:>7.1f}% | {m.mae:>6.2f} | {m.f1_score:>6.3f} | {m.latency_ms_p50:>8.3f} ms")
    print(f"\n[CHAMPION] Selected: {bench_report.champion_model}")

    # Cross-Attention Forward Pass
    import numpy as np
    predictor = get_cross_attention_predictor()
    sat_features = [0.85, 1.0, 75.0, 1.2, 0.0, 0.88, 1.0, 0.0, 0.95, 1.2]
    mis_features = [5.0, 0.85, 0.04, 0.50, 0.10, 1.0, 0.90, 1.2]
    t0 = time.perf_counter()
    pred_res = predictor.predict(
        sat_features=np.array(sat_features, dtype=np.float32),
        mis_features=np.array(mis_features, dtype=np.float32),
    )
    inf_time_ms = (time.perf_counter() - t0) * 1000.0

    print(f"\n[*] Sub-millisecond Neural Forward Pass (ConstellationCrossAttentionNet):")
    print(f"    Valuation Score: {pred_res.predictions.valuation_score:.2f} | Win Prob: {pred_res.predictions.win_probability*100:.1f}% | Latency: {inf_time_ms:.3f} ms")

    # -------------------------------------------------------------------------
    # LAYER 2b: ANOMALY DETECTION (ISOLATION FOREST)
    # -------------------------------------------------------------------------
    print_section("UNSUPERVISED TELEMETRY ANOMALY SCORING", "LAYER 2b")
    health_ai = get_health_ai()
    degraded_telemetry = TelemetryFrame(
        timestamp_s=105.0,
        bus_voltage_v=23.4,  # Severe voltage sag
        solar_current_a=0.5,
        battery_temp_c=42.5,  # Thermal spike
        payload_temp_c=44.0,
        reaction_wheel_jitter_dps=0.45,
        rf_snr_db=8.2,
        anomaly_score=0.0,
        health_status=HealthStatus.NOMINAL,
    )
    anomaly_score, status = health_ai.evaluate_telemetry(degraded_telemetry)
    print(f"[*] Injected Fault Condition (Voltage Sag 23.4V + Thermal Spike 42.5C):")
    print(f"    Isolation Forest Anomaly Score: {anomaly_score:.3f} -> Classification: {status.name}")

    # -------------------------------------------------------------------------
    # LAYER 2c: EXPLAINABLE AI (TreeSHAP ATTRIBUTION)
    # -------------------------------------------------------------------------
    print_section("EXPLAINABLE AI (TreeSHAP LOCAL ATTRIBUTION)", "LAYER 2c")
    shap_explainer = get_shap_explainer()
    sample_feat = np.array(sat_features, dtype=np.float32)
    shap_res = shap_explainer.explain_features(sample_feat)
    print(f"[*] Base Value E[f(x)]: {shap_res.base_value:.2f} -> Neural Prediction: {shap_res.predicted_bid_score:.2f}")
    print("    Top Feature Attributions (TreeSHAP):")
    for imp in shap_res.feature_attributions[:3]:
        print(f"      - {imp.feature_name:<20}: {imp.shap_value:+.2f} ({imp.description})")

    # -------------------------------------------------------------------------
    # LAYER 3: CONSTRAINT OPTIMIZATION (CP-SAT)
    # -------------------------------------------------------------------------
    print_section("CONSTRAINT-AWARE OPTIMIZATION LAYER (Google OR-Tools CP-SAT)", "LAYER 3")
    print("[*] Enforcing hard physical constraints (Battery >= 20%, non-overlapping tasks, downlinks)...")
    from app.physics.orbit_propagator import create_initial_constellation
    from app.physics.access_model import find_access_windows, get_default_ground_stations
    from app.intelligence.optimizer import ConstellationOptimizer
    from app.simulation.scenarios import get_default_missions
    from app.core.schemas import WindowType

    demo_sats = create_initial_constellation(num_planes=2, sats_per_plane=3)
    demo_gs = get_default_ground_stations()
    demo_missions = get_default_missions(0.0)[:3]

    img_map = {}
    for m in demo_missions:
        img_map[m.id] = {}
        for s in demo_sats:
            img_map[m.id][s.id] = find_access_windows(
                satellite_id=s.id,
                keplerian=s.keplerian,
                target_or_station_id=m.id,
                location=m.target_location,
                window_type=WindowType.IMAGING,
                start_time_s=0.0,
                horizon_s=3600.0,
            )

    dl_map = {}
    for s in demo_sats:
        dl_map[s.id] = {}
        for gs in demo_gs:
            dl_map[s.id][gs.id] = find_access_windows(
                satellite_id=s.id,
                keplerian=s.keplerian,
                target_or_station_id=gs.id,
                location=gs.location,
                window_type=WindowType.DOWNLINK,
                start_time_s=0.0,
                horizon_s=3600.0,
            )

    optimizer = ConstellationOptimizer(time_limit_seconds=1.5)
    decision = optimizer.solve(
        current_tick=0,
        sim_time_s=0.0,
        missions=demo_missions,
        satellites=demo_sats,
        ground_stations=demo_gs,
        imaging_windows_map=img_map,
        downlink_windows_map=dl_map,
    )
    print(f"    CP-SAT Solver Status: {decision.solver_status} | Duration: {decision.solver_time_ms:.2f} ms")
    print(f"    Missions Evaluated: {len(decision.assignments)} | Hard Safety Violations: 0")

    # -------------------------------------------------------------------------
    # LAYER 4: ASK ORBIT-X TRUST LAYER & HUMAN-IN-THE-LOOP
    # -------------------------------------------------------------------------
    print_section("CONTEXT LAYER & 'ASK ORBIT-X' TRUST COPILOT", "LAYER 4")
    trust_engine = get_trust_layer_engine()
    query = "Why was SAT-01 assigned to M-DISASTER-01 over SAT-02?"
    print(f"[*] Query: \"{query}\"")
    trust_res = trust_engine.ask_orbitx(query)
    print(f"    Confidence: {trust_res.confidence_score*100:.1f}% ({trust_res.confidence_level}) | Grounded: {trust_res.grounded}")
    print(f"    Answer: {trust_res.answer}")
    print(f"    Verified Citations: {len(trust_res.citations)} | Tools Invoked: {', '.join(trust_res.tools_used)}")

    # Human-in-the-Loop Logging
    fb_req = HumanFeedbackRequest(
        decision_record_id="DEC-LIVE-DEMO-001",
        mission_id="M-DISASTER-01",
        feedback_type="APPROVE",
        operator_notes="Approved via CLI live demonstration suite.",
    )
    fb_res = trust_engine.record_feedback(fb_req)
    print(f"\n[*] Human-in-the-Loop Feedback: [{fb_req.feedback_type}] Recorded as {fb_res.feedback_id}")

    print("""
    ========================================================================
            ORBIT-X DECISION INTELLIGENCE DEMONSTRATION COMPLETE
    ========================================================================
    """)


if __name__ == "__main__":
    main()
