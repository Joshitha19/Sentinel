"""
Domain Plugin Registry for SENTINEL.
Adding a new domain requires creating one file and registering it here.
"""

from typing import Dict, List, Any
from app.domains.base import BaseDomain
from app.domains.transactions import TransactionsDomain
from app.domains.health import HealthDomain
from app.domains.sensors import SensorsDomain

DOMAINS: Dict[str, BaseDomain] = {
    "transactions": TransactionsDomain(),
    "health": HealthDomain(),
    "sensors": SensorsDomain(),
}


def get_domain(domain_id: str) -> BaseDomain:
    """Retrieves an instantiated domain plugin by ID."""
    if domain_id not in DOMAINS:
        raise ValueError(
            f"Domain '{domain_id}' not found. Available domains: {list(DOMAINS.keys())}"
        )
    return DOMAINS[domain_id]


def list_domains() -> List[Dict[str, Any]]:
    """Returns overview metadata for all registered domain plugins."""
    items = []
    for d_id, dom in DOMAINS.items():
        items.append({
            "id": dom.id,
            "name": dom.name,
            "description": dom.description,
            "num_features": len(dom.feature_names),
            "class_labels": dom.class_labels,
            "rare_class_label": dom.rare_class_label,
            "hidden_class_label": dom.hidden_class_label,
            "feature_names": dom.feature_names,
            "feature_schema": dom.feature_schema,
        })
    return items
