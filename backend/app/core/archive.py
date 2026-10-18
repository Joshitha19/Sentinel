"""
Diversity-Aware Candidate Archive and Human-in-the-Loop Triage Gatekeeper.
Manages candidate lifecycle: Realism Filtering -> Diversity Check -> Human Gate -> Retraining Pool.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import uuid
import time
import numpy as np
from scipy.spatial.distance import cdist


@dataclass
class ArchiveCandidate:
    """Represents a generated synthetic candidate in the archive."""
    id: str
    vector: np.ndarray
    realism_score: float
    novelty_score: float
    hardness_score: float
    reward: float
    round_idx: int
    status: str = "approved"  # "pending", "approved", "rejected"
    created_at: float = field(default_factory=time.time)
    explanation: Dict[str, Any] = field(default_factory=dict)
    synthetic_watermark: str = "FICTIONAL_UNVALIDATED_SYNTHETIC"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "realism_score": round(self.realism_score, 4),
            "novelty_score": round(self.novelty_score, 4),
            "hardness_score": round(self.hardness_score, 4),
            "reward": round(self.reward, 4),
            "round_idx": self.round_idx,
            "status": self.status,
            "created_at": self.created_at,
            "explanation": self.explanation,
            "synthetic_watermark": self.synthetic_watermark,
            "features_preview": [round(float(v), 3) for v in self.vector[:8]]
        }


class CandidateArchive:
    """Archive managing candidate storage, deduplication, and triage."""

    def __init__(
        self,
        max_size: int = 500,
        realism_threshold: float = 0.50,
        diversity_threshold: float = 0.30
    ):
        self.max_size = max_size
        self.realism_threshold = realism_threshold
        self.diversity_threshold = diversity_threshold
        self.candidates: List[ArchiveCandidate] = []

    def __len__(self) -> int:
        return len(self.candidates)

    def get_candidate_matrix(self, status_filter: Optional[str] = "approved") -> np.ndarray:
        """Returns feature matrix of approved (or filtered) candidates."""
        filtered = [
            c for c in self.candidates
            if status_filter is None or c.status == status_filter
        ]
        if not filtered:
            return np.empty((0, 0))
        return np.vstack([c.vector for c in filtered])

    def add_candidate(
        self,
        vector: np.ndarray,
        realism: float,
        novelty: float,
        hardness: float,
        reward: float,
        round_idx: int,
        explanation: Dict[str, Any],
        auto_approve: bool = True
    ) -> Optional[ArchiveCandidate]:
        """
        Inserts candidate if it passes realism threshold and diversity deduplication.
        """
        if realism < self.realism_threshold:
            return None

        # Check diversity against existing archive items
        if len(self.candidates) > 0:
            existing_vectors = np.vstack([c.vector for c in self.candidates])
            dists = cdist(vector.reshape(1, -1), existing_vectors, metric="euclidean")[0]
            min_dist = float(np.min(dists))
            if min_dist < self.diversity_threshold:
                # Near-duplicate of existing candidate, discard to ensure diversity
                return None

        # If archive is full, evict lowest reward candidate
        if len(self.candidates) >= self.max_size:
            # Sort by reward
            self.candidates.sort(key=lambda x: x.reward, reverse=True)
            self.candidates.pop()  # remove lowest reward

        candidate = ArchiveCandidate(
            id=str(uuid.uuid4())[:8],
            vector=vector,
            realism_score=realism,
            novelty_score=novelty,
            hardness_score=hardness,
            reward=reward,
            round_idx=round_idx,
            status="approved" if auto_approve else "pending",
            explanation=explanation
        )
        self.candidates.append(candidate)
        return candidate

    def update_status(self, candidate_id: str, new_status: str) -> bool:
        """Human-in-the-loop triage: approve or reject candidate."""
        for c in self.candidates:
            if c.id == candidate_id:
                c.status = new_status
                return True
        return False

    def list_candidates(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns JSON-serializable list of recent candidates."""
        # Return most recent first
        sorted_cands = sorted(self.candidates, key=lambda x: x.created_at, reverse=True)
        return [c.to_dict() for c in sorted_cands[:limit]]
