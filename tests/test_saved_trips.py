"""Unit tests for Saved Trips and Bookmark Management module."""
import json
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.saved_trips import (
    normalize_saved_trip,
    save_trip,
    delete_trip,
    clear_saved_trips,
    get_saved_trips,
    compare_trips,
    export_trip_json,
    export_trip_text,
)


def _sample_trip(destination="Goa", days_count=3, style="Relaxed"):
    """Helper creating a sample trip itinerary dictionary."""
    return {
        "destination": destination,
        "state": "Goa",
        "category": "Beach",
        "duration_days": days_count,
        "travel_style": style,
        "estimated_cost": 8500,
        "rating": 4.6,
        "best_season": "Winter",
        "user_interests": ["Scuba", "Cafes"],
        "days": [
            {
                "day": 1,
                "theme_focus": "Day 1: Beach Immersion",
                "slots": {
                    "Morning": {"title": "Beach Walk", "description": "Early morning coastal stroll.", "pace": "Gentle"},
                    "Afternoon": {"title": "Scuba Diving", "description": "Explore coral reefs.", "pace": "Moderate"},
                    "Evening": {"title": "Sunset Cruise", "description": "Dinner on cruise.", "pace": "Leisure"},
                },
            }
        ],
        "budget": {
            "expenses": {
                "Accommodation": 3400,
                "Food": 2125,
                "Transportation": 1275,
                "Activities": 850,
                "Miscellaneous": 850,
            }
        },
    }


def test_empty_saved_trips_state():
    """Verify clean handling of empty or None saved trips state."""
    assert get_saved_trips([]) == []
    assert get_saved_trips(None) == []
    assert clear_saved_trips() == []
    print("[PASS] test_empty_saved_trips_state passed.")


def test_normalize_saved_trip():
    """Verify normalization of trip dictionaries and handling of missing fields."""
    sample = _sample_trip("Jaipur", 2, "Cultural")
    norm = normalize_saved_trip(sample)
    assert norm is not None
    assert norm["destination"] == "Jaipur"
    assert norm["duration_days"] == 2
    assert norm["travel_style"] == "Cultural"
    assert norm["estimated_cost"] == 8500
    assert "id" in norm
    assert len(norm["interests"]) == 2

    # Invalid input
    assert normalize_saved_trip(None) is None
    assert normalize_saved_trip({}) is None
    assert normalize_saved_trip({"destination": ""}) is None
    print("[PASS] test_normalize_saved_trip passed.")


def test_save_valid_trip_and_duplicate_prevention():
    """Verify adding trips and preventing accidental duplicates."""
    trips_list = []
    t1 = _sample_trip("Manali", 3, "Adventurous")

    # First save succeeds
    trips_list, success, msg = save_trip(trips_list, t1, prevent_duplicates=True)
    assert success is True
    assert len(trips_list) == 1
    assert "Successfully saved" in msg

    # Duplicate save is prevented
    trips_list, success2, msg2 = save_trip(trips_list, t1, prevent_duplicates=True)
    assert success2 is False
    assert len(trips_list) == 1
    assert "already saved" in msg2

    # Different duration or destination succeeds
    t2 = _sample_trip("Manali", 5, "Adventurous")
    trips_list, success3, msg3 = save_trip(trips_list, t2, prevent_duplicates=True)
    assert success3 is True
    assert len(trips_list) == 2

    print("[PASS] test_save_valid_trip_and_duplicate_prevention passed.")


def test_delete_trip_by_id_and_index():
    """Verify single trip deletion by ID or index."""
    t1 = _sample_trip("Goa", 3, "Relaxed")
    t2 = _sample_trip("Udaipur", 2, "Cultural")

    lst, _, _ = save_trip([], t1)
    lst, _, _ = save_trip(lst, t2)
    assert len(lst) == 2

    trip2_id = lst[1]["id"]

    # Delete by ID
    updated_lst, del_ok = delete_trip(lst, trip2_id)
    assert del_ok is True
    assert len(updated_lst) == 1
    assert updated_lst[0]["destination"] == "Goa"

    # Delete by index
    final_lst, idx_ok = delete_trip(updated_lst, 0)
    assert idx_ok is True
    assert len(final_lst) == 0

    print("[PASS] test_delete_trip_by_id_and_index passed.")


def test_compare_trips():
    """Verify multi-trip side-by-side comparison table."""
    t1 = _sample_trip("Goa", 3, "Relaxed")
    t2 = _sample_trip("Munnar", 4, "Nature")

    df_comp = compare_trips([t1, t2])
    assert isinstance(df_comp, pd.DataFrame)
    assert len(df_comp) == 2
    assert "Destination" in df_comp.columns
    assert "Estimated Cost (INR)" in df_comp.columns
    assert "Duration (Days)" in df_comp.columns

    # Empty comparison
    assert compare_trips([]).empty
    print("[PASS] test_compare_trips passed.")


def test_export_trip_json():
    """Verify JSON export creates parseable and complete JSON strings."""
    t = _sample_trip("Varanasi", 2, "Spiritual")
    json_str = export_trip_json(t)

    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["destination"] == "Varanasi"
    assert parsed["duration_days"] == 2
    assert "days" in parsed
    print("[PASS] test_export_trip_json passed.")


def test_export_trip_text():
    """Verify plain-text export formats itinerary, days, slots, and budget."""
    t = _sample_trip("Goa", 3, "Relaxed")
    text_doc = export_trip_text(t)

    assert "TRAVEL INTELLIGENCE — PERSONALIZED ITINERARY" in text_doc
    assert "Destination:     Goa" in text_doc
    assert "Trip Duration:   3 Days" in text_doc
    assert "DAY-BY-DAY SCHEDULE:" in text_doc
    assert "[Morning]" in text_doc
    assert "[Afternoon]" in text_doc
    assert "[Evening]" in text_doc
    assert "ESTIMATED BUDGET BREAKDOWN:" in text_doc
    assert "Accommodation" in text_doc
    print("[PASS] test_export_trip_text passed.")


def test_edge_cases():
    """Verify robustness on invalid/corrupted payloads."""
    # Corrupted dictionary
    corrupted = {"destination": "Coorg", "duration_days": "not_a_number", "estimated_cost": "free"}
    norm = normalize_saved_trip(corrupted)
    assert norm["destination"] == "Coorg"
    assert norm["duration_days"] == 1
    assert norm["estimated_cost"] == 0

    # JSON export of invalid trip
    err_json = export_trip_json({})
    assert "error" in json.loads(err_json)

    # Text export of invalid trip
    err_text = export_trip_text(None)
    assert "Error" in err_text
    print("[PASS] test_edge_cases passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING SAVED TRIPS TEST SUITE")
    print("==================================================")
    test_empty_saved_trips_state()
    test_normalize_saved_trip()
    test_save_valid_trip_and_duplicate_prevention()
    test_delete_trip_by_id_and_index()
    test_compare_trips()
    test_export_trip_json()
    test_export_trip_text()
    test_edge_cases()
    print("==================================================")
    print("SUCCESS: ALL SAVED TRIPS TESTS PASSED!")
    print("==================================================")
