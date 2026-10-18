"""
Direct python test runner for Phase 1 tests.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tests.test_splits import test_stratified_splits_standard, test_hidden_class_holdout
from tests.test_domains import test_domain_lifecycle, test_list_domains
from tests.test_baselines import test_baseline_models


def run():
    print("=== Running SENTINEL Phase 1 Tests ===")
    
    print("Testing standard stratified splits...")
    test_stratified_splits_standard()
    print("  PASS: test_stratified_splits_standard")

    print("Testing hidden class holdout...")
    test_hidden_class_holdout()
    print("  PASS: test_hidden_class_holdout")

    print("Testing domain list...")
    test_list_domains()
    print("  PASS: test_list_domains")

    for dom in ["transactions", "health", "sensors"]:
        print(f"Testing domain lifecycle: {dom}...")
        test_domain_lifecycle(dom)
        print(f"  PASS: domain {dom}")

    print("Testing baselines...")
    test_baseline_models()
    print("  PASS: test_baseline_models")

    print("\nALL PHASE 1 TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    run()
