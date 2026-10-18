"""
Evaluation and Empirical Benchmark Routes.
Exposes comparative baselines, ablations, conformal prediction coverage,
and the dedicated Hidden-Class Proof Experiment.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List, Optional
from app.domains import get_domain
from app.core.experiments import ExperimentRunner
from app.api.routes_train import load_stored_runs, save_stored_run

router = APIRouter(prefix="/api/eval", tags=["evaluation"])


@router.get("/leaderboard")
def get_leaderboard(
    domain_id: str = "transactions",
    force_fresh: bool = False
):
    """
    Returns comparative leaderboard: Baselines vs SENTINEL vs Ablations.
    Uses stored runs if available, or executes deterministic benchmark.
    """
    stored = load_stored_runs()
    cache_key = f"benchmark_{domain_id}"

    if not force_fresh and cache_key in stored:
        return stored[cache_key]

    try:
        domain = get_domain(domain_id)
        runner = ExperimentRunner(domain=domain, random_seed=42)
        results = runner.run_full_benchmark(
            use_offline_sim=True,
            max_samples=2500,
            n_rounds=6
        )
        save_stored_run(cache_key, results)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmark execution failed: {str(e)}")


@router.post("/hidden_class")
def run_hidden_class_proof(domain_id: str = "transactions"):
    """
    Executes the Hidden-Class Generalization Experiment.
    Compares Zero-Shot Recall on completely unobserved rare event class.
    """
    try:
        domain = get_domain(domain_id)
        runner = ExperimentRunner(domain=domain, random_seed=42)
        proof_results = runner.run_hidden_class_experiment(
            use_offline_sim=True,
            max_samples=2500,
            n_rounds=6
        )
        return proof_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hidden-class experiment failed: {str(e)}")


@router.get("/conformal")
def get_conformal_calibration(domain_id: str = "transactions"):
    """
    Returns conformal prediction coverage curve and ambiguity analysis.
    """
    benchmark_data = get_leaderboard(domain_id=domain_id, force_fresh=False)
    conformal_details = benchmark_data.get("conformal_details", {})
    return conformal_details
