"""
2D Feature Projection Engine:
Projects high-dimensional multi-domain feature vectors to 2D coordinates [-100, 100]^2.
Powers the real-time interactive canvas scatter map in the dashboard.
"""

from typing import Dict, Any, List, Optional
import numpy as np
from sklearn.decomposition import PCA


class FeatureProjectionEngine:
    """Fast, deterministic 2D projection using PCA fitted on training data."""

    def __init__(self, random_seed: int = 42):
        self.pca = PCA(n_components=2, random_state=random_seed)
        self.is_fitted = False
        self._scale_factor = 25.0

    def fit(self, X_reference: np.ndarray):
        """Fits projection on real reference data."""
        self.pca.fit(X_reference)
        self.is_fitted = True

        # Compute scaling so typical points map cleanly inside [-85, 85]
        projected = self.pca.transform(X_reference[:1000])
        max_val = np.percentile(np.abs(projected), 98)
        self._scale_factor = float(max(1.0, max_val))
        return self

    def project(self, X: np.ndarray) -> np.ndarray:
        """
        Projects X (N, D) -> (N, 2) bounded approximately within [-100, 100].
        """
        if not self.is_fitted:
            self.fit(X)

        coords = self.pca.transform(X)
        # Scale to [-80, 80] and clip outliers to [-98, 98]
        norm_coords = (coords / self._scale_factor) * 60.0
        clipped = np.clip(norm_coords, -98.0, 98.0)
        return np.round(clipped, 2)

    def prepare_map_payload(
        self,
        X_nominal: np.ndarray,
        X_known_rare: np.ndarray,
        X_archive: Optional[np.ndarray] = None,
        X_active_batch: Optional[np.ndarray] = None,
        max_nominal_points: int = 400
    ) -> Dict[str, Any]:
        """
        Builds optimized compact payload for the front-end canvas scatter visualizer.
        Categories:
          - 'nominal' (Cyan)
          - 'known_rare' (Amber)
          - 'archive' (Violet)
          - 'candidate' (Pulsing White/Emerald)
        """
        points = []

        # 1. Subsample nominal points for fast smooth canvas rendering
        if len(X_nominal) > max_nominal_points:
            sub_idx = np.random.choice(len(X_nominal), size=max_nominal_points, replace=False)
            nom_sample = X_nominal[sub_idx]
        else:
            nom_sample = X_nominal

        coords_nom = self.project(nom_sample)
        for pt in coords_nom:
            points.append({"x": float(pt[0]), "y": float(pt[1]), "type": "nominal"})

        # 2. Known rare points (all of them)
        if len(X_known_rare) > 0:
            coords_rare = self.project(X_known_rare)
            for pt in coords_rare:
                points.append({"x": float(pt[0]), "y": float(pt[1]), "type": "known_rare"})

        # 3. Archive points
        if X_archive is not None and len(X_archive) > 0:
            coords_arch = self.project(X_archive)
            for pt in coords_arch:
                points.append({"x": float(pt[0]), "y": float(pt[1]), "type": "archive"})

        # 4. Active candidate batch
        if X_active_batch is not None and len(X_active_batch) > 0:
            coords_batch = self.project(X_active_batch)
            for pt in coords_batch:
                points.append({"x": float(pt[0]), "y": float(pt[1]), "type": "candidate"})

        return {
            "total_points": len(points),
            "points": points,
            "bounds": {"min": -100, "max": 100}
        }
