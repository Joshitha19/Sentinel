"""
Domain Routes:
Provides metadata, feature schemas, and preview data for all registered domain plugins.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.domains import list_domains, get_domain

router = APIRouter(prefix="/api/domains", tags=["domains"])


@router.get("", response_model=List[Dict[str, Any]])
def get_all_domains():
    """Returns overview of all available domains."""
    return list_domains()


@router.get("/{domain_id}")
def get_domain_details(domain_id: str):
    """Retrieves full specification for a domain."""
    try:
        domain = get_domain(domain_id)
        return {
            "id": domain.id,
            "name": domain.name,
            "description": domain.description,
            "feature_names": domain.feature_names,
            "class_labels": domain.class_labels,
            "rare_class_label": domain.rare_class_label,
            "hidden_class_label": domain.hidden_class_label,
            "feature_schema": domain.feature_schema,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{domain_id}/preview")
def get_domain_preview(domain_id: str, n_samples: int = 10):
    """Loads a small sample batch for preview in Mission Control."""
    try:
        domain = get_domain(domain_id)
        df, X, y = domain.load_data(use_offline_sim=True, max_samples=n_samples)
        records = df.head(n_samples).to_dict(orient="records")
        return {
            "domain_id": domain_id,
            "n_samples": len(records),
            "columns": list(df.columns),
            "samples": records
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{domain_id}/map")
def get_domain_map(domain_id: str):
    """Generates baseline 2D PCA projection coordinates for the domain."""
    try:
        domain = get_domain(domain_id)
        df, X, y = domain.load_data(use_offline_sim=True, max_samples=600)
        from app.utils.projection import FeatureProjectionEngine
        projector = FeatureProjectionEngine(random_seed=42)
        projector.fit(X)
        X_nominal = X[y == 0]
        X_known_rare = X[y == domain.rare_class_label] if domain.rare_class_label in y else X[y >= 1]
        
        # Initial sample candidates and archive points for visual richness
        X_archive = X_known_rare[:8] if len(X_known_rare) > 0 else None
        
        payload = projector.prepare_map_payload(
            X_nominal=X_nominal,
            X_known_rare=X_known_rare,
            X_archive=X_archive,
            max_nominal_points=350
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

