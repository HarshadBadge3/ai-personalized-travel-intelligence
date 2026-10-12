"""Unit tests for Smart Day-by-Day Trip Planner itinerary generator."""
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.itinerary import (
    parse_activities,
    get_destination_activities,
    classify_activity_slot,
    generate_day_plan,
    generate_itinerary,
)


def test_parse_activities():
    """Verify comma-separated activity parsing."""
    raw = "Scuba Diving, Beach Hopping, Sunset Cruise, Cafes"
    parsed = parse_activities(raw)
    assert len(parsed) == 4
    assert "Scuba Diving" in parsed
    assert "Cafes" in parsed

    # Edge cases
    assert parse_activities("") == []
    assert parse_activities(None) == []
    print("[PASS] test_parse_activities passed.")


def test_get_destination_activities():
    """Verify destination activity and metadata retrieval."""
    df = preprocess_destinations(load_raw_destinations())
    jaipur_data = get_destination_activities(df, "Jaipur")

    assert jaipur_data["destination"] == "Jaipur"
    assert jaipur_data["category"] == "Heritage"
    assert len(jaipur_data["activities"]) >= 3
    assert "Fort Visits" in jaipur_data["activities"]

    # Unknown destination handles safely
    unknown = get_destination_activities(df, "Nonexistent Place")
    assert unknown["destination"] == "Nonexistent Place"
    assert unknown["activities"] == []
    print("[PASS] test_get_destination_activities passed.")


def test_classify_activity_slot():
    """Verify time slot heuristics (Morning, Afternoon, Evening)."""
    assert classify_activity_slot("Sunrise Fort Trek") == "Morning"
    assert classify_activity_slot("Temple Visit & Aarti") in ["Morning", "Evening"]
    assert classify_activity_slot("Water Sports & Snorkeling") == "Afternoon"
    assert classify_activity_slot("Sunset Cruise") == "Evening"
    assert classify_activity_slot("Stargazing Night Camp") == "Evening"
    print("[PASS] test_classify_activity_slot passed.")


def test_one_day_itinerary():
    """Verify single day plan generation structure."""
    df = preprocess_destinations(load_raw_destinations())
    plan = generate_itinerary(df, "Goa", duration_days=1, travel_style="Relaxed")

    assert "error" not in plan
    assert plan["destination"] == "Goa"
    assert plan["duration_days"] == 1
    assert len(plan["days"]) == 1

    day1 = plan["days"][0]
    assert "Morning" in day1["slots"]
    assert "Afternoon" in day1["slots"]
    assert "Evening" in day1["slots"]
    assert "title" in day1["slots"]["Morning"]
    print("[PASS] test_one_day_itinerary passed.")


def test_multi_day_itinerary():
    """Verify multi-day itinerary generation with distinct days."""
    df = preprocess_destinations(load_raw_destinations())
    plan = generate_itinerary(df, "Manali", duration_days=4, travel_style="Adventurous")

    assert plan["duration_days"] == 4
    assert len(plan["days"]) == 4

    # Day sequences are strictly 1..4
    day_numbers = [d["day"] for d in plan["days"]]
    assert day_numbers == [1, 2, 3, 4]

    # Verify slots are properly populated
    for d in plan["days"]:
        for slot in ["Morning", "Afternoon", "Evening"]:
            assert d["slots"][slot]["title"] != ""
            assert len(d["slots"][slot]["description"]) > 10

    print("[PASS] test_multi_day_itinerary passed.")


def test_travel_styles_and_interests():
    """Verify travel style pacing and interest prioritization."""
    df = preprocess_destinations(load_raw_destinations())

    # Style: Relaxed
    relaxed_plan = generate_itinerary(df, "Munnar", duration_days=2, travel_style="Relaxed")
    assert relaxed_plan["travel_style"] == "Relaxed"
    # Afternoon or evening slot reflects relaxed pace note
    assert "relax" in relaxed_plan["days"][0]["slots"]["Afternoon"]["description"].lower() or \
           "relax" in relaxed_plan["days"][0]["slots"]["Evening"]["description"].lower()

    # Prioritization: If user has 'tea' in interests, tea activities are prioritized in Day 1
    tea_plan = generate_itinerary(df, "Munnar", duration_days=2, user_interests=["tea", "plantation"])
    d1_titles = [
        tea_plan["days"][0]["slots"]["Morning"]["title"].lower(),
        tea_plan["days"][0]["slots"]["Afternoon"]["title"].lower(),
    ]
    assert any("tea" in t or "plantation" in t for t in d1_titles)

    print("[PASS] test_travel_styles_and_interests passed.")


def test_edge_cases_and_bounds():
    """Verify safe handling of invalid durations, 0 days, empty activity dataset."""
    df = preprocess_destinations(load_raw_destinations())

    # Invalid: 0 days
    zero_plan = generate_itinerary(df, "Jaipur", duration_days=0)
    assert "error" in zero_plan

    # Negative duration
    neg_plan = generate_itinerary(df, "Jaipur", duration_days=-2)
    assert "error" in neg_plan

    # Large duration: capped safely at 10 days
    large_plan = generate_itinerary(df, "Jaipur", duration_days=25)
    assert large_plan["duration_days"] == 10
    assert len(large_plan["days"]) == 10

    # Destination with empty dataframe / no activities
    dummy_df = pd.DataFrame([{"destination": "Desert Island", "activities": "", "category": "Nature"}])
    empty_act_plan = generate_itinerary(dummy_df, "Desert Island", duration_days=2)
    assert len(empty_act_plan["days"]) == 2
    assert empty_act_plan["days"][0]["slots"]["Morning"]["title"] != ""

    print("[PASS] test_edge_cases_and_bounds passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING ITINERARY PLANNER TESTS")
    print("==================================================")
    test_parse_activities()
    test_get_destination_activities()
    test_classify_activity_slot()
    test_one_day_itinerary()
    test_multi_day_itinerary()
    test_travel_styles_and_interests()
    test_edge_cases_and_bounds()
    print("==================================================")
    print("SUCCESS: ALL ITINERARY PLANNER TESTS PASSED!")
    print("==================================================")
