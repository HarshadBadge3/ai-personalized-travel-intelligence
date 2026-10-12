"""Unit and pipeline verification tests for Phase 1 Travel Intelligence."""
import sys
from pathlib import Path

# Add project root to sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations, get_project_root
from src.preprocessing import preprocess_destinations, assign_budget_tier
from src.utils import filter_destinations, format_currency_inr


def test_data_loader():
    """Verify that raw destination CSV loads into a non-empty DataFrame."""
    df = load_raw_destinations()
    assert not df.empty, "Dataset should not be empty"
    assert "destination" in df.columns, "Column 'destination' must exist"
    assert "state" in df.columns, "Column 'state' must exist"
    assert "rating" in df.columns, "Column 'rating' must exist"
    assert "estimated_cost" in df.columns, "Column 'estimated_cost' must exist"
    print("[PASS] test_data_loader passed.")


def test_preprocessing():
    """Verify data preprocessing cleans types and assigns budget tiers."""
    df = load_raw_destinations()
    clean_df = preprocess_destinations(df)
    
    assert "budget_tier" in clean_df.columns, "Clean dataframe must have budget_tier"
    assert clean_df["rating"].dtype in ["float64", "float32"], "Rating should be float"
    assert clean_df["estimated_cost"].dtype in ["int64", "float64"], "Estimated cost should be numeric"
    
    # Test helper
    assert assign_budget_tier(3000) == "Budget"
    assert assign_budget_tier(7500) == "Moderate"
    assert assign_budget_tier(15000) == "Luxury"
    print("[PASS] test_preprocessing passed.")


def test_filter_destinations():
    """Verify filtering logic by query, state, category, budget, and rating."""
    df = preprocess_destinations(load_raw_destinations())

    # State filter test
    rajasthan_df = filter_destinations(df, selected_state="Rajasthan")
    assert all(rajasthan_df["state"] == "Rajasthan"), "All records should be Rajasthan"
    assert len(rajasthan_df) >= 1, "Rajasthan should have at least 1 destination"

    # Search query test
    manali_df = filter_destinations(df, search_query="manali")
    assert "Manali" in manali_df["destination"].values, "Manali should be found"

    # Budget filter test
    budget_df = filter_destinations(df, max_budget=4000)
    assert all(budget_df["estimated_cost"] <= 4000), "All records should be <= 4000"

    # Rating filter test
    high_rating = filter_destinations(df, min_rating=4.7)
    assert all(high_rating["rating"] >= 4.7), "All records should have rating >= 4.7"

    print("[PASS] test_filter_destinations passed.")


def test_format_currency_inr():
    """Verify currency string formatting."""
    assert format_currency_inr(5000) == "INR 5,000" or format_currency_inr(5000) == "\u20b95,000"
    print("[PASS] test_format_currency_inr passed.")


if __name__ == "__main__":
    print("Running Phase 1 validation tests...")
    test_data_loader()
    test_preprocessing()
    test_filter_destinations()
    test_format_currency_inr()
    print("SUCCESS: All Phase 1 tests passed successfully!")

