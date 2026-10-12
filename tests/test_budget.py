"""Unit tests for Smart Travel Budget Intelligence & Optimizer module."""
import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.budget import (
    validate_budget,
    get_style_allocations,
    calculate_base_daily_cost,
    estimate_expenses,
    calculate_total_budget,
    compare_with_user_budget,
    generate_budget_suggestions,
    STYLE_ALLOCATIONS,
)


def test_validate_budget():
    """Verify numeric validation, string parsing, and negative/zero rejection."""
    assert validate_budget(15000) == 15000
    assert validate_budget("20000") == 20000
    assert validate_budget(12500.50) == 12500
    assert validate_budget(0) is None
    assert validate_budget(-5000) is None
    assert validate_budget("invalid_number") is None
    assert validate_budget(None) is None
    print("[PASS] test_validate_budget passed.")


def test_expense_allocations_sum_100():
    """Verify that all style allocation mappings sum to strictly 1.0 (100%)."""
    for style, mapping in STYLE_ALLOCATIONS.items():
        total_share = sum(mapping.values())
        assert abs(total_share - 1.0) < 1e-6, f"Allocation for {style} must equal 1.0, got {total_share}"
        assert "Accommodation" in mapping
        assert "Food" in mapping
        assert "Transportation" in mapping
        assert "Activities" in mapping
        assert "Miscellaneous" in mapping
    print("[PASS] test_expense_allocations_sum_100 passed.")


def test_estimate_expenses_integrity():
    """Verify expense breakdown sums exactly to total cost with zero discrepancy."""
    for test_cost in [5000, 12345, 27891, 50000]:
        expenses = estimate_expenses(test_cost, "Balanced")
        assert sum(expenses.values()) == test_cost, f"Sum of expenses must equal {test_cost}"

    # Style sensitivity
    luxury_expenses = estimate_expenses(20000, "Luxury")
    budget_expenses = estimate_expenses(20000, "Budget")
    assert luxury_expenses["Accommodation"] > budget_expenses["Accommodation"]
    print("[PASS] test_estimate_expenses_integrity passed.")


def test_calculate_total_budget_and_daily_average():
    """Verify total budget calculation and daily cost averages."""
    df = preprocess_destinations(load_raw_destinations())

    # 3-day trip in Jaipur
    res3 = calculate_total_budget(df, "Jaipur", duration_days=3, travel_style="Balanced")
    assert res3["duration_days"] == 3
    assert res3["destination"] == "Jaipur"
    assert res3["total_estimated"] > 0
    assert res3["daily_average"] > 0
    assert abs(res3["total_estimated"] - (res3["daily_average"] * 3)) <= 3

    # Clamping bounds: 0 days clamped to 1, >10 days clamped to 10
    res_min = calculate_total_budget(df, "Jaipur", duration_days=0)
    assert res_min["duration_days"] == 1

    res_max = calculate_total_budget(df, "Jaipur", duration_days=25)
    assert res_max["duration_days"] == 10

    print("[PASS] test_calculate_total_budget_and_daily_average passed.")


def test_compare_with_user_budget():
    """Verify within budget, exact match, and over budget classifications."""
    # Case 1: Within budget
    wb = compare_with_user_budget(estimated_total=12000, user_budget=15000)
    assert wb["status"] == "Within Budget"
    assert wb["difference"] == 3000
    assert wb["is_over_budget"] is False
    assert wb["utilization_pct"] == 80.0

    # Case 2: Exact match
    em = compare_with_user_budget(estimated_total=15000, user_budget=15000)
    assert em["status"] == "Budget Fully Utilized"
    assert em["difference"] == 0
    assert em["is_over_budget"] is False

    # Case 3: Over budget
    ob = compare_with_user_budget(estimated_total=18500, user_budget=15000)
    assert ob["status"] == "Over Budget"
    assert ob["difference"] == 3500
    assert ob["is_over_budget"] is True
    assert ob["utilization_pct"] > 100.0

    # Case 4: No budget set
    nb = compare_with_user_budget(estimated_total=12000, user_budget=None)
    assert nb["status"] == "No Budget Set"

    print("[PASS] test_compare_with_user_budget passed.")


def test_generate_budget_suggestions():
    """Verify practical optimization suggestions when over budget."""
    df = preprocess_destinations(load_raw_destinations())

    # Over budget situation
    suggs = generate_budget_suggestions(
        df=df,
        destination_name="Goa",
        duration_days=4,
        travel_style="Luxury",
        user_budget=10000,
        current_estimated_total=20000,
    )

    assert len(suggs) >= 2, "Should provide multiple actionable suggestions"
    assert all("estimated_savings" in s for s in suggs)
    assert all("new_total" in s for s in suggs)
    # Suggestions should be ranked descending by savings
    savings_list = [s["estimated_savings"] for s in suggs]
    assert savings_list == sorted(savings_list, reverse=True)

    # Within budget situation
    wb_suggs = generate_budget_suggestions(
        df=df,
        destination_name="Goa",
        duration_days=2,
        travel_style="Budget",
        user_budget=15000,
        current_estimated_total=5000,
    )
    assert len(wb_suggs) >= 1
    assert "Comfort Upgrade" in wb_suggs[0]["title"]

    print("[PASS] test_generate_budget_suggestions passed.")


def test_destination_integration_and_edge_cases():
    """Verify fallback handling for unknown destinations and empty DataFrames."""
    df = preprocess_destinations(load_raw_destinations())

    # Unknown destination uses clean fallback without crashing
    unknown_res = calculate_total_budget(df, "Atlantis", duration_days=3)
    assert unknown_res["total_estimated"] > 0
    assert "Accommodation" in unknown_res["expenses"]

    # None DataFrame
    none_res = calculate_total_budget(None, "Goa", duration_days=3)
    assert none_res["total_estimated"] > 0

    print("[PASS] test_destination_integration_and_edge_cases passed.")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING BUDGET PLANNER TEST SUITE")
    print("==================================================")
    test_validate_budget()
    test_expense_allocations_sum_100()
    test_estimate_expenses_integrity()
    test_calculate_total_budget_and_daily_average()
    test_compare_with_user_budget()
    test_generate_budget_suggestions()
    test_destination_integration_and_edge_cases()
    print("==================================================")
    print("SUCCESS: ALL BUDGET PLANNER TESTS PASSED!")
    print("==================================================")
