"""Unit tests for Natural Language Query Parser."""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.query_parser import (
    extract_budget,
    extract_duration,
    extract_categories,
    extract_travel_style,
    extract_season,
    extract_activities,
    parse_travel_query,
    update_preferences_state,
)


def test_budget_extraction():
    """Verify numeric, k-format, and rupee symbol budget extraction."""
    assert extract_budget("under 15000") == 15000
    assert extract_budget("budget is 20k") == 20000
    assert extract_budget("I can spend 10000") == 10000
    assert extract_budget("around 15,000 rupees") == 15000
    assert extract_budget("₹8500 total") == 8500
    assert extract_budget("max 12k for trip") == 12000
    assert extract_budget("no money mentioned") is None
    print("[PASS] test_budget_extraction passed.")


def test_duration_extraction():
    """Verify duration parsing in days, weekends, and weeks."""
    assert extract_duration("for 3 days") == 3
    assert extract_duration("5 day trip") == 5
    assert extract_duration("weekend trip") == 2
    assert extract_duration("long weekend getaway") == 3
    assert extract_duration("spending a week in kerala") == 7
    assert extract_duration("4 nights stay") == 5
    assert extract_duration("just traveling") is None
    print("[PASS] test_duration_extraction passed.")


def test_category_detection():
    """Verify travel interest category mapping to dataset themes."""
    assert "Beach" in extract_categories("I want a peaceful beach vacation")
    assert "Heritage" in extract_categories("Looking to explore historical forts and palaces")
    assert "Nature" in extract_categories("Need a scenic hill station with waterfalls")
    assert "Adventure" in extract_categories("Interested in trekking and river rafting")
    assert "Spiritual" in extract_categories("Visiting ancient temples and ghats")
    assert extract_categories("random text") == []
    print("[PASS] test_category_detection passed.")


def test_travel_style_detection():
    """Verify travel vibe and persona style recognition."""
    assert extract_travel_style("Looking for a peaceful retreat") == "Relaxed"
    assert extract_travel_style("Need an adventurous vacation") == "Adventurous"
    assert extract_travel_style("Romantic honeymoon getaway") == "Romantic"
    assert extract_travel_style("Traveling with kids and family") == "Family"
    assert extract_travel_style("Luxury 5-star experience") == "Luxury"
    assert extract_travel_style("No style") is None
    print("[PASS] test_travel_style_detection passed.")


def test_season_and_activity_detection():
    """Verify seasonality and activity keyword extraction."""
    assert extract_season("planning a winter holiday") == "Winter"
    assert extract_season("trip in december") == "Winter"
    assert extract_season("summer vacation") == "Summer"

    acts = extract_activities("I love scuba diving, trekking and photography")
    assert "scuba diving" in acts or "scuba" in acts
    assert "trekking" in acts
    assert "photography" in acts
    print("[PASS] test_season_and_activity_detection passed.")


def test_combined_query_parsing():
    """Verify comprehensive single-sentence natural language query parsing."""
    query = "I want a peaceful beach trip under 15000 for 3 days in winter with scuba diving"
    parsed = parse_travel_query(query)

    assert parsed["budget"] == 15000
    assert parsed["duration"] == 3
    assert "Beach" in parsed["categories"]
    assert parsed["travel_style"] == "Relaxed"
    assert parsed["season"] == "Winter"
    assert any("scuba" in a for a in parsed["activities"])
    print("[PASS] test_combined_query_parsing passed.")


def test_preference_state_updates():
    """Verify conversation context retention and preference updates."""
    state = {
        "budget": None,
        "duration": None,
        "categories": [],
        "travel_style": None,
        "season": None,
        "activities": [],
    }

    # Turn 1: "I want a beach trip"
    t1 = parse_travel_query("I want a beach trip")
    state = update_preferences_state(state, t1)
    assert state["categories"] == ["Beach"]
    assert state["budget"] is None

    # Turn 2: "Budget is 15k for 4 days"
    t2 = parse_travel_query("Budget is 15k for 4 days")
    state = update_preferences_state(state, t2)
    assert state["categories"] == ["Beach"], "Category should be preserved across turns"
    assert state["budget"] == 15000
    assert state["duration"] == 4

    # Turn 3: Preference update / change of mind ("Actually prefer mountains and nature")
    t3 = parse_travel_query("Actually prefer mountains and nature")
    state = update_preferences_state(state, t3)
    assert "Nature" in state["categories"], "Category should be updated to Nature"
    assert state["budget"] == 15000, "Budget should remain intact"
    assert state["duration"] == 4, "Duration should remain intact"

    print("[PASS] test_preference_state_updates passed.")


def test_edge_cases():
    """Verify handling of empty or unrelated inputs."""
    empty_parsed = parse_travel_query("")
    assert empty_parsed["budget"] is None
    assert empty_parsed["categories"] == []

    random_parsed = parse_travel_query("what is the weather in new york?")
    assert random_parsed["budget"] is None
    assert random_parsed["categories"] == []
    print("[PASS] test_edge_cases passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING QUERY PARSER TEST SUITE")
    print("==================================================")
    test_budget_extraction()
    test_duration_extraction()
    test_category_detection()
    test_travel_style_detection()
    test_season_and_activity_detection()
    test_combined_query_parsing()
    test_preference_state_updates()
    test_edge_cases()
    print("==================================================")
    print("SUCCESS: ALL QUERY PARSER TESTS PASSED!")
    print("==================================================")
