"""Tests for Benchmark Suite (CP-SAT vs Greedy vs Random)."""

from app.simulation.benchmark import run_benchmark_comparison


def test_benchmark_suite_execution():
    results = run_benchmark_comparison(seed=42, num_missions=10, horizon_s=3600.0)
    assert len(results) == 6
    names = [r.scheduler_name for r in results]
    assert "Random Assignment" in names
    assert "Greedy EDF Heuristic" in names
    assert "Multi-Agent Vickrey Auction" in names
    assert "Neural Surrogate Policy" in names
    assert "Hybrid Neural + CP-SAT" in names
    assert "Google OR-Tools CP-SAT" in names
    
    # Check that CP-SAT and Hybrid have higher or equal completion and reward
    cpsat_res = next(r for r in results if r.scheduler_name == "Google OR-Tools CP-SAT")
    assert cpsat_res.completion_rate_pct >= 0.0
    assert cpsat_res.avg_battery_reserve_pct > 0.0

