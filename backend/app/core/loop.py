"""
SENTINEL Master Training Loop, Curriculum Scheduler, and Ablation Engine.
Orchestrates adversarial self-play between Generator, Discriminator, and Detector,
emitting structured telemetry events for real-time WebSocket broadcasting.
"""

from typing import Dict, Any, List, Optional, Callable
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from app.domains.base import BaseDomain
from app.core.splits import DataSplits
from app.core.generator import SentinelGenerator
from app.core.discriminator import RealismDiscriminator
from app.core.detector import SentinelDetector
from app.core.rewards import SentinelRewardEngine
from app.core.archive import CandidateArchive
from app.core.conformal import SplitConformalPredictor
from app.utils.projection import FeatureProjectionEngine
from app.utils.metrics import compute_binary_metrics, compute_memorization_metrics


class SentinelTrainingLoop:
    """End-to-End SENTINEL Adversarial Training Engine."""

    def __init__(
        self,
        domain: BaseDomain,
        splits: DataSplits,
        alpha: float = 1.0,
        beta: float = 1.2,
        gamma: float = 1.0,
        curriculum: bool = True,
        n_rounds: int = 15,
        steps_per_round: int = 15,
        batch_size: int = 48,
        latent_dim: int = 32,
        k_neighbors: int = 5,
        random_seed: int = 42
    ):
        self.domain = domain
        self.splits = splits
        self.alpha_base = alpha
        self.beta_base = beta
        self.gamma_base = gamma
        self.curriculum = curriculum
        self.n_rounds = n_rounds
        self.steps_per_round = steps_per_round
        self.batch_size = batch_size
        self.latent_dim = latent_dim
        self.k_neighbors = k_neighbors
        self.random_seed = random_seed
        self.device = torch.device("cpu")

        # Reproducibility
        torch.manual_seed(random_seed)
        np.random.seed(random_seed)

        # Initialize models
        input_dim = len(domain.feature_names)
        self.generator = SentinelGenerator(latent_dim, domain.feature_schema).to(self.device)
        self.discriminator = RealismDiscriminator(input_dim).to(self.device)
        self.detector = SentinelDetector(input_dim, random_seed=random_seed)
        self.reward_engine = SentinelRewardEngine(domain, k_neighbors=k_neighbors)
        self.archive = CandidateArchive(max_size=400, realism_threshold=0.45, diversity_threshold=0.30)
        self.conformal = SplitConformalPredictor(target_coverage=0.90)
        self.projector = FeatureProjectionEngine(random_seed=random_seed).fit(splits.X_train)

        # Reference tensors for novelty computation
        y_train_bin = (splits.y_train >= 1).astype(int)
        rare_train = splits.X_train[y_train_bin == 1]
        self.real_rare_tensor = torch.tensor(rare_train, dtype=torch.float32, device=self.device)
        self.real_all_tensor = torch.tensor(splits.X_train, dtype=torch.float32, device=self.device)

        # Baseline detector initial fit on raw train split
        self.detector.fit(splits.X_train, y_train_bin)

        # Optimizers
        self.opt_g = optim.Adam(self.generator.parameters(), lr=1e-3, betas=(0.5, 0.99))
        self.opt_d = optim.Adam(self.discriminator.parameters(), lr=3e-4, betas=(0.5, 0.99))
        self.criterion_bce = nn.BCEWithLogitsLoss()

    def run(
        self,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes multi-round adversarial loop with live telemetry event streaming.
        """
        history = []
        start_time = time.time()

        for round_idx in range(1, self.n_rounds + 1):
            # Curriculum progression: gradually increase beta (novelty) and gamma (hardness)
            if self.curriculum:
                progress = round_idx / self.n_rounds
                alpha_t = self.alpha_base
                beta_t = self.beta_base * (1.0 + 0.8 * progress)
                gamma_t = self.gamma_base * (0.6 + 0.8 * (progress ** 2))
            else:
                alpha_t = self.alpha_base
                beta_t = self.beta_base
                gamma_t = self.gamma_base

            round_losses_g = []
            round_losses_d = []
            round_realisms = []
            round_novelties = []
            round_hardnesses = []
            round_rewards = []
            new_candidates_added = 0

            # Combined reference for novelty: real rare + archive
            archive_mat = self.archive.get_candidate_matrix(status_filter="approved")
            if archive_mat.size > 0:
                arch_tensor = torch.tensor(archive_mat, dtype=torch.float32, device=self.device)
                ref_novelty = torch.cat([self.real_rare_tensor, arch_tensor], dim=0)
            else:
                ref_novelty = self.real_rare_tensor

            for step in range(self.steps_per_round):
                # 1. Update Discriminator on real data vs generated data
                self.opt_d.zero_grad()
                real_idx = np.random.choice(len(self.splits.X_train), size=self.batch_size)
                batch_real = torch.tensor(self.splits.X_train[real_idx], dtype=torch.float32, device=self.device)

                z_d = torch.randn(self.batch_size, self.latent_dim, device=self.device)
                with torch.no_grad():
                    batch_fake = self.generator(z_d)

                logits_real = self.discriminator(batch_real)
                logits_fake = self.discriminator(batch_fake)

                loss_d_real = self.criterion_bce(logits_real, torch.ones_like(logits_real))
                loss_d_fake = self.criterion_bce(logits_fake, torch.zeros_like(logits_fake))
                loss_d = loss_d_real + loss_d_fake
                loss_d.backward()
                self.opt_d.step()

                # 2. Update Generator via Tripartite Reward: Loss_G = -Reward
                self.opt_g.zero_grad()
                z_g = torch.randn(self.batch_size, self.latent_dim, device=self.device)
                gen_candidates = self.generator(z_g)

                total_reward, breakdown = self.reward_engine.compute_total_reward(
                    gen_candidates,
                    self.discriminator,
                    self.detector,
                    ref_novelty,
                    alpha=alpha_t,
                    beta=beta_t,
                    gamma=gamma_t
                )

                loss_g = -torch.mean(total_reward)
                loss_g.backward()
                self.opt_g.step()

                # Record metrics
                round_losses_g.append(float(loss_g.item()))
                round_losses_d.append(float(loss_d.item()))
                round_realisms.append(float(torch.mean(breakdown["realism"]).item()))
                round_novelties.append(float(torch.mean(breakdown["novelty"]).item()))
                round_hardnesses.append(float(torch.mean(breakdown["hardness"]).item()))
                round_rewards.append(float(torch.mean(total_reward).item()))

            # 3. Archive Screening & Candidate Sampling at end of round
            self.generator.eval()
            with torch.no_grad():
                z_sample = torch.randn(24, self.latent_dim, device=self.device)
                batch_sample = self.generator(z_sample, hard_binary=True)
                sample_rewards, sample_bk = self.reward_engine.compute_total_reward(
                    batch_sample, self.discriminator, self.detector, ref_novelty,
                    alpha=alpha_t, beta=beta_t, gamma=gamma_t
                )

                sample_np = batch_sample.cpu().numpy()
                realisms_np = sample_bk["realism"].cpu().numpy()
                novelties_np = sample_bk["novelty"].cpu().numpy()
                hardnesses_np = sample_bk["hardness"].cpu().numpy()
                rewards_np = sample_rewards.cpu().numpy()

                for i in range(len(sample_np)):
                    cand_vec = sample_np[i]
                    expl = self.domain.explain_candidate(cand_vec)
                    added = self.archive.add_candidate(
                        vector=cand_vec,
                        realism=float(realisms_np[i]),
                        novelty=float(novelties_np[i]),
                        hardness=float(hardnesses_np[i]),
                        reward=float(rewards_np[i]),
                        round_idx=round_idx,
                        explanation=expl,
                        auto_approve=True
                    )
                    if added:
                        new_candidates_added += 1

            # 4. Retrain Detector on Real Data + Approved Archive Items every 3 rounds
            if round_idx % 3 == 0 or round_idx == self.n_rounds:
                archive_approved = self.archive.get_candidate_matrix(status_filter="approved")
                if archive_approved.size > 0:
                    y_train_bin = (self.splits.y_train >= 1).astype(int)
                    X_aug = np.vstack([self.splits.X_train, archive_approved])
                    # Archive items labeled 1 (rare/unusual)
                    y_aug = np.concatenate([y_train_bin, np.ones(len(archive_approved), dtype=int)])
                    self.detector.fit(X_aug, y_aug)

            # Evaluate on Validation set
            val_bin = (self.splits.y_val >= 1).astype(int)
            val_probs = self.detector.predict_proba(self.splits.X_val)
            val_metrics = compute_binary_metrics(val_bin, val_probs)

            # Prepare 2D scatter payload
            active_batch_sample = sample_np[:12]
            map_payload = self.projector.prepare_map_payload(
                X_nominal=self.splits.X_train[y_train_bin == 0],
                X_known_rare=self.splits.X_train[y_train_bin == 1],
                X_archive=self.archive.get_candidate_matrix(status_filter="approved"),
                X_active_batch=active_batch_sample,
                max_nominal_points=350
            )

            round_summary = {
                "round": round_idx,
                "total_rounds": self.n_rounds,
                "weights": {"alpha": round(alpha_t, 3), "beta": round(beta_t, 3), "gamma": round(gamma_t, 3)},
                "loss_g": round(float(np.mean(round_losses_g)), 4),
                "loss_d": round(float(np.mean(round_losses_d)), 4),
                "realism": round(float(np.mean(round_realisms)), 4),
                "novelty": round(float(np.mean(round_novelties)), 4),
                "hardness": round(float(np.mean(round_hardnesses)), 4),
                "reward": round(float(np.mean(round_rewards)), 4),
                "archive_size": len(self.archive),
                "new_candidates_added": new_candidates_added,
                "val_pr_auc": val_metrics["pr_auc"],
                "val_roc_auc": val_metrics["roc_auc"],
                "val_recall": val_metrics["recall_at_target_fpr"],
                "map_payload": map_payload,
                "recent_candidates": self.archive.list_candidates(limit=6)
            }
            history.append(round_summary)

            if event_callback:
                event_callback({
                    "event": "training_round",
                    "data": round_summary
                })

        # 5. Final Conformal Calibration and Test Evaluation
        calib_bin = (self.splits.y_calib >= 1).astype(int)
        calib_probs = self.detector.predict_proba(self.splits.X_calib)
        self.conformal.calibrate(calib_probs, calib_bin)

        test_bin = (self.splits.y_test >= 1).astype(int)
        test_probs = self.detector.predict_proba(self.splits.X_test)
        test_metrics = compute_binary_metrics(
            test_bin,
            test_probs,
            hidden_test_mask=self.splits.hidden_test_mask
        )
        conformal_eval = self.conformal.evaluate_coverage(test_probs, test_bin)

        # Memorization check on approved archive
        archive_matrix = self.archive.get_candidate_matrix(status_filter="approved")
        mem_check = compute_memorization_metrics(
            generated_candidates=archive_matrix,
            real_training_data=self.splits.X_train
        )

        final_report = {
            "elapsed_seconds": round(time.time() - start_time, 2),
            "history": history,
            "test_metrics": test_metrics,
            "conformal_evaluation": conformal_eval,
            "memorization_check": mem_check,
            "archive_candidates_total": len(self.archive)
        }

        if event_callback:
            event_callback({
                "event": "training_complete",
                "data": final_report
            })

        return final_report
