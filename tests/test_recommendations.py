"""Unit and integration tests for Phase 2 Recommendation Engine and Phase 1 regression verification."""
import sys
from pathlib import Path
import pandas as pd

# Ensure project root is in sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TEST_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Phase 1 modules
from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations, assign_budget_tier
from src.utils import filter_destinations, format_currency_inr

# Phase 2 modules
from src.recommendation import (
    build_destination_content_text,
    build_user_preference_text,
    calculate_content_recommendations,
)


# ==============================================================
# PHASE 1 REGRESSION TESTS
# ==============================================================

def test_phase1_data_loader():
    """Verify that raw destination CSV loads into a non-empty DataFrame."""
    df = load_raw_destinations()
    assert not df.empty, "Dataset should not be empty"
    assert "destination" in df.columns, "Column 'destination' must exist"
    assert "state" in df.columns, "Column 'state' must exist"
    assert "rating" in df.columns, "Column 'rating' must exist"
    assert "estimated_cost" in df.columns, "Column 'estimated_cost' must exist"
    print("[PASS] Phase 1: test_phase1_data_loader passed.")


def test_phase1_preprocessing():
    """Verify data preprocessing cleans types and assigns budget tiers."""
    df = load_raw_destinations()
    clean_df = preprocess_destinations(df)
    
    assert "budget_tier" in clean_df.columns, "Clean dataframe must have budget_tier"
    assert clean_df["rating"].dtype in ["float64", "float32"], "Rating should be float"
    assert clean_df["estimated_cost"].dtype in ["int64", "float64"], "Estimated cost should be numeric"
    
    assert assign_budget_tier(3000) == "Budget"
    assert assign_budget_tier(7500) == "Moderate"
    assert assign_budget_tier(15000) == "Luxury"
    print("[PASS] Phase 1: test_phase1_preprocessing passed.")


def test_phase1_filter_destinations():
    """Verify filtering logic by query, state, category, budget, and rating."""
    df = preprocess_destinations(load_raw_destinations())

    rajasthan_df = filter_destinations(df, selected_state="Rajasthan")
    assert all(rajasthan_df["state"] == "Rajasthan"), "All records should be Rajasthan"
    assert len(rajasthan_df) >= 1, "Rajasthan should have at least 1 destination"

    manali_df = filter_destinations(df, search_query="manali")
    assert "Manali" in manali_df["destination"].values, "Manali should be found"

    budget_df = filter_destinations(df, max_budget=4000)
    assert all(budget_df["estimated_cost"] <= 4000), "All records should be <= 4000"

    high_rating = filter_destinations(df, min_rating=4.7)
    assert all(high_rating["rating"] >= 4.7), "All records should have rating >= 4.7"
    print("[PASS] Phase 1: test_phase1_filter_destinations passed.")


def test_phase1_format_currency_inr():
    """Verify currency string formatting."""
    assert format_currency_inr(5000) in ["INR 5,000", "\u20b95,000"]
    print("[PASS] Phase 1: test_phase1_format_currency_inr passed.")


# ==============================================================
# PHASE 2 RECOMMENDATION ENGINE TESTS
# ==============================================================

def test_recommendation_imports():
    """Verify recommendation module functions can be imported."""
    from src.recommendation import (
        build_destination_content_text,
        build_user_preference_text,
        calculate_content_recommendations,
    )
    assert callable(build_destination_content_text)
    assert callable(build_user_preference_text)
    assert callable(calculate_content_recommendations)
    print("[PASS] Phase 2: test_recommendation_imports passed.")


def test_build_destination_content_text():
    """Verify that destination content string includes key tokens and handles missing values."""
    df = preprocess_destinations(load_raw_destinations())
    content_series = build_destination_content_text(df)

    assert len(content_series) == len(df), "Content series length should match dataframe"
    assert all(isinstance(s, str) and len(s) > 10 for s in content_series), "All strings should be descriptive"

    # Specific sample check (Jaipur)
    jaipur_idx = df[df["destination"] == "Jaipur"].index[0]
    jaipur_text = content_series[jaipur_idx]
    assert "jaipur" in jaipur_text
    assert "rajasthan" in jaipur_text
    assert "heritage" in jaipur_text

    # Edge case: Empty DataFrame
    empty_series = build_destination_content_text(pd.DataFrame())
    assert empty_series.empty
    print("[PASS] Phase 2: test_build_destination_content_text passed.")


def test_build_user_preference_text():
    """Verify user preference string consolidation across attributes."""
    profile = {
        "name": "Aarav",
        "persona_type": "Solo Backpacker",
        "pace": "Moderate",
        "categories": ["Adventure", "Nature"],
        "budget_tier": "Budget (Under ₹5,000/trip)",
        "preferred_season": "Summer",
        "preferred_activities": "trekking, rafting",
    }
    pref_text = build_user_preference_text(profile)
    assert "adventure" in pref_text
    assert "nature" in pref_text
    assert "solo backpacker" in pref_text
    assert "budget" in pref_text
    assert "summer" in pref_text
    assert "trekking" in pref_text

    # Edge case: None or empty profile
    assert build_user_preference_text(None) == ""
    assert build_user_preference_text({}) == ""
    print("[PASS] Phase 2: test_build_user_preference_text passed.")


def test_calculate_content_recommendations_ranking():
    """Verify that relevant destinations receive higher cosine similarity scores."""
    df = preprocess_destinations(load_raw_destinations())

    # Adventure profile: expect Manali or Leh-Ladakh to rank high
    adventure_profile = {
        "categories": ["Adventure"],
        "persona_type": "Adventure Group",
        "budget_tier": "Moderate",
        "preferred_activities": "Paragliding, Trekking, Skiing",
    }

    recs = calculate_content_recommendations(df, profile=adventure_profile, top_n=5)
    assert not recs.empty, "Recommendations should not be empty"
    assert len(recs) == 5, "Should return top 5 recommendations"
    assert "similarity_score" in recs.columns, "similarity_score column must exist"
    assert "match_score_pct" in recs.columns, "match_score_pct column must exist"

    # Monotonically descending ranking
    scores = recs["similarity_score"].tolist()
    assert scores == sorted(scores, reverse=True), "Recommendations must be sorted descending"

    # Top destination should match category
    top_categories = recs.head(2)["category"].tolist()
    assert "Adventure" in top_categories, f"Adventure destination should rank in top 2, got: {top_categories}"

    print("[PASS] Phase 2: test_calculate_content_recommendations_ranking passed.")


def test_recommendation_edge_cases():
    """Verify safe handling of edge cases without exceptions."""
    df = preprocess_destinations(load_raw_destinations())

    # Case 1: Empty profile and empty query -> returns empty DataFrame
    res_empty = calculate_content_recommendations(df, profile=None, user_query="", top_n=5)
    assert res_empty.empty, "Empty profile and query should return empty DataFrame"

    # Case 2: Requesting top_n greater than dataset length -> caps safely
    res_large = calculate_content_recommendations(df, profile={"categories": ["Heritage"]}, top_n=50)
    assert len(res_large) == len(df), f"Should return capped {len(df)} results, got {len(res_large)}"

    # Case 3: Dataset with single row -> succeeds without crashing
    single_row_df = df.head(1)
    res_single = calculate_content_recommendations(single_row_df, profile={"categories": ["Heritage"]}, top_n=3)
    assert len(res_single) == 1

    # Case 4: Query only with no profile
    res_query_only = calculate_content_recommendations(df, profile=None, user_query="scuba diving beach", top_n=3)
    assert not res_query_only.empty
    assert "Goa" in res_query_only["destination"].values or "Andaman Islands" in res_query_only["destination"].values

    print("[PASS] Phase 2: test_recommendation_edge_cases passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING ALL PHASE 1 & PHASE 2 VERIFICATION TESTS")
    print("==================================================")
    test_phase1_data_loader()
    test_phase1_preprocessing()
    test_phase1_filter_destinations()
    test_phase1_format_currency_inr()
    print("--------------------------------------------------")
    test_recommendation_imports()
    test_build_destination_content_text()
    test_build_user_preference_text()
    test_calculate_content_recommendations_ranking()
    test_recommendation_edge_cases()
    print("==================================================")
    print("SUCCESS: ALL PHASE 1 & PHASE 2 TESTS PASSED!")
    print("==================================================")
