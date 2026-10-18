"""
Candidate Explorer & Human-in-the-Loop Triage Routes.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import numpy as np
from app.api.routes_train import TRAINING_STATE
from app.domains import get_domain

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


class UpdateStatusRequest(BaseModel):
    status: str  # "approved", "rejected", "pending"


@router.get("", response_model=List[Dict[str, Any]])
def get_candidates(limit: int = 40):
    """Retrieves candidates from active archive, or generates sample candidates if archive is empty."""
    active_loop = TRAINING_STATE.get("active_loop")
    if active_loop and len(active_loop.archive) > 0:
        return active_loop.archive.list_candidates(limit=limit)

    # If no live training has run yet, generate a high-quality sample batch from the current domain
    domain_id = TRAINING_STATE.get("domain_id", "transactions")
    domain = get_domain(domain_id)
    df, X, y = domain.load_data(use_offline_sim=True, max_samples=400)
    rare_samples = X[y >= 1]

    synthetic_candidates = []
    np.random.seed(42)

    for i in range(min(12, len(rare_samples))):
        vec = rare_samples[i] + np.random.normal(0, 0.25, size=rare_samples[i].shape)
        expl = domain.explain_candidate(vec)
        synthetic_candidates.append({
            "id": f"cand_{i+1:03d}",
            "realism_score": round(float(np.random.uniform(0.72, 0.94)), 3),
            "novelty_score": round(float(np.random.uniform(0.65, 0.88)), 3),
            "hardness_score": round(float(np.random.uniform(0.60, 0.85)), 3),
            "reward": round(float(np.random.uniform(1.8, 2.5)), 3),
            "round_idx": 1,
            "status": "pending" if i % 2 == 0 else "approved",
            "created_at": 1729270000 + i * 60,
            "explanation": expl,
            "synthetic_watermark": "FICTIONAL_UNVALIDATED_SYNTHETIC",
            "features_preview": [round(float(v), 2) for v in vec[:8]]
        })

    return synthetic_candidates


@router.post("/{candidate_id}/status")
def update_candidate_status(candidate_id: str, req: UpdateStatusRequest):
    """Human-in-the-loop triage: approves or rejects a candidate."""
    if req.status not in ["approved", "rejected", "pending"]:
        raise HTTPException(status_code=400, detail="Status must be 'approved', 'rejected', or 'pending'")

    active_loop = TRAINING_STATE.get("active_loop")
    if active_loop:
        updated = active_loop.archive.update_status(candidate_id, req.status)
        if updated:
            return {"message": f"Candidate {candidate_id} marked as {req.status}"}

    return {"message": f"Candidate {candidate_id} status updated to {req.status} (mock mode)"}
