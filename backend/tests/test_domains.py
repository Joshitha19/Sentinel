"""
Unit tests for the Domain Plugin system.
"""

import numpy as np
import torch
from app.domains import get_domain, list_domains


@pytest.mark.parametrize("domain_id", ["transactions", "health", "sensors"])
def test_domain_lifecycle(domain_id):
    domain = get_domain(domain_id)
    assert domain.id == domain_id
    assert len(domain.name) > 0
    assert len(domain.feature_names) > 0
    assert domain.rare_class_label is not None

    # Test data loading via offline simulator
    df, X, y = domain.load_data(use_offline_sim=True, max_samples=500)
    assert len(df) == 500
    assert X.shape == (500, len(domain.feature_names))
    assert len(y) == 500
    assert set(np.unique(y)).issubset(set(domain.class_labels.keys()))

    # Test realism rules
    cand_tensor = torch.tensor(X[:10], dtype=torch.float32)
    valid_mask, penalty = domain.realism_rules(cand_tensor)
    assert valid_mask.shape == (10,)
    assert penalty.shape == (10,)
    assert (penalty >= 0.0).all()

    # Test explain candidate
    sample_candidate = X[0]
    explanation = domain.explain_candidate(sample_candidate)
    assert "summary" in explanation
    assert "key_anomalies" in explanation
    assert "risk_level" in explanation
    assert isinstance(explanation["key_anomalies"], list)


def test_list_domains():
    all_domains = list_domains()
    assert len(all_domains) == 3
    ids = [d["id"] for d in all_domains]
    assert "transactions" in ids
    assert "health" in ids
    assert "sensors" in ids
