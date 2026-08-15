"""FastAPI Router for Benchmarking & Policy Evaluation."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from app.core.schemas import BenchmarkResult
from app.simulation.benchmark import run_benchmark_comparison

router = APIRouter(prefix="/api/benchmarks", tags=["Benchmarks"])


class BenchmarkRunRequest(BaseModel):
    seed: int = 42
    num_missions: int = 24
    horizon_s: float = 5400.0


@router.post("/run", response_model=List[BenchmarkResult])
async def run_benchmark(req: BenchmarkRunRequest):
    """Executes comparative evaluation across Random, Greedy EDF, and CP-SAT."""
    results = run_benchmark_comparison(
        seed=req.seed,
        num_missions=req.num_missions,
        horizon_s=req.horizon_s,
    )
    return results
