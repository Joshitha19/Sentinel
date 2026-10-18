"""
Differentiable Reward Formulation for SENTINEL.
Combines Realism, Novelty (k-NN distance over real data & archive), and Hardness.
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
from app.domains.base import BaseDomain


class SentinelRewardEngine:
    """
    Computes tripartite reward and generator loss:
    Reward = alpha * Realism + beta * Novelty + gamma * Hardness
    Loss = -Reward
    """

    def __init__(
        self,
        domain: BaseDomain,
        k_neighbors: int = 5,
        realism_scale: float = 1.0,
        novelty_norm: float = 5.0
    ):
        self.domain = domain
        self.k_neighbors = k_neighbors
        self.realism_scale = realism_scale
        self.novelty_norm = novelty_norm

    def compute_novelty(
        self,
        candidates: torch.Tensor,
        reference_data: torch.Tensor
    ) -> torch.Tensor:
        """
        Differentiable Novelty:
        Mean Euclidean distance to the k-nearest neighbors among reference points
        (combined real rare data + accumulated archive items).
        
        Args:
            candidates: Tensor (B, D)
            reference_data: Tensor (M, D) where M >= k
            
        Returns:
            novelty_scores: Tensor (B,) >= 0
        """
        if reference_data.size(0) == 0:
            return torch.ones(candidates.size(0), device=candidates.device)

        k = min(self.k_neighbors, reference_data.size(0))
        # Differentiable pairwise distance matrix (B, M)
        dist_matrix = torch.cdist(candidates, reference_data, p=2.0)

        # topk with largest=False extracts k smallest distances
        topk_dists, _ = torch.topk(dist_matrix, k=k, dim=1, largest=False)
        mean_knn_dist = torch.mean(topk_dists, dim=1)

        # Normalize into smooth scale approx [0, 2]
        return mean_knn_dist / self.novelty_norm

    def compute_hardness(
        self,
        candidates: torch.Tensor,
        detector
    ) -> torch.Tensor:
        """
        Hardness:
        1.0 - P_detector(rare | candidate).
        High when detector thinks the candidate is nominal / safe,
        thus actively finding detector blindspots.
        """
        prob_rare = detector.predict_rare_prob(candidates)
        hardness = 1.0 - prob_rare
        return hardness

    def compute_realism(
        self,
        candidates: torch.Tensor,
        discriminator: nn.Module
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Realism:
        Discriminator probability minus domain rule violation soft penalty.
        """
        disc_score = discriminator.score(candidates)
        valid_mask, domain_penalty = self.domain.realism_rules(candidates)

        # Realism combines statistical likelihood with domain rules
        realism = disc_score - 0.4 * domain_penalty
        return realism, disc_score, domain_penalty

    def compute_total_reward(
        self,
        candidates: torch.Tensor,
        discriminator: nn.Module,
        detector,
        reference_data: torch.Tensor,
        alpha: float = 1.0,
        beta: float = 1.2,
        gamma: float = 1.0
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Computes weighted total reward and detailed component breakdowns.
        Returns:
            total_reward: Tensor (B,)
            breakdown: Dict of component tensors
        """
        realism, disc_prob, domain_penalty = self.compute_realism(candidates, discriminator)
        novelty = self.compute_novelty(candidates, reference_data)
        hardness = self.compute_hardness(candidates, detector)

        total_reward = (
            alpha * realism +
            beta * novelty +
            gamma * hardness
        )

        breakdown = {
            "total_reward": total_reward,
            "realism": realism,
            "disc_prob": disc_prob,
            "domain_penalty": domain_penalty,
            "novelty": novelty,
            "hardness": hardness
        }
        return total_reward, breakdown
