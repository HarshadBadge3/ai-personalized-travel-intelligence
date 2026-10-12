"""Smart Travel Budget Intelligence & Optimizer module.

Provides deterministic planning expense breakdowns across:
- Accommodation
- Food
- Transportation
- Activities
- Miscellaneous

Calculates variance against user budget and generates actionable cost-saving optimizations.
"""
from typing import Any
import pandas as pd


# Style-dependent percentage allocation models (Sum of all 5 categories strictly = 100%)
STYLE_ALLOCATIONS: dict[str, dict[str, float]] = {
    "Balanced": {
        "Accommodation": 0.35,
        "Food": 0.20,
        "Transportation": 0.20,
        "Activities": 0.15,
        "Miscellaneous": 0.10,
    },
    "Relaxed": {
        "Accommodation": 0.40,
        "Food": 0.25,
        "Transportation": 0.15,
        "Activities": 0.10,
        "Miscellaneous": 0.10,
    },
    "Adventurous": {
        "Accommodation": 0.25,
        "Food": 0.20,
        "Transportation": 0.20,
        "Activities": 0.25,
        "Miscellaneous": 0.10,
    },
    "Cultural": {
        "Accommodation": 0.30,
        "Food": 0.20,
        "Transportation": 0.20,
        "Activities": 0.20,
        "Miscellaneous": 0.10,
    },
    "Romantic": {
        "Accommodation": 0.40,
        "Food": 0.25,
        "Transportation": 0.15,
        "Activities": 0.12,
        "Miscellaneous": 0.08,
    },
    "Family": {
        "Accommodation": 0.38,
        "Food": 0.24,
        "Transportation": 0.18,
        "Activities": 0.12,
        "Miscellaneous": 0.08,
    },
    "Budget": {
        "Accommodation": 0.28,
        "Food": 0.22,
        "Transportation": 0.25,
        "Activities": 0.15,
        "Miscellaneous": 0.10,
    },
    "Luxury": {
        "Accommodation": 0.45,
        "Food": 0.20,
        "Transportation": 0.15,
        "Activities": 0.12,
        "Miscellaneous": 0.08,
    },
}

# Style cost multipliers reflecting baseline per-day expenditure intensity
STYLE_COST_MULTIPLIERS: dict[str, float] = {
    "Balanced": 1.0,
    "Relaxed": 0.95,
    "Adventurous": 1.10,
    "Cultural": 0.90,
    "Romantic": 1.25,
    "Family": 1.30,
    "Budget": 0.70,
    "Luxury": 1.80,
}


def validate_budget(budget_amount: Any) -> int | None:
    """Validate user budget input and ensure it is a positive integer.

    Args:
        budget_amount: Number, float or string budget value.

    Returns:
        int | None: Clean integer amount or None if invalid.
    """
    if budget_amount is None:
        return None

    try:
        val = int(float(budget_amount))
        if val <= 0:
            return None
        return val
    except (ValueError, TypeError):
        return None


def get_style_allocations(travel_style: str) -> dict[str, float]:
    """Retrieve normalized percentage breakdown for a given travel style.

    Args:
        travel_style: Travel style name (Balanced, Relaxed, Adventurous, etc.).

    Returns:
        dict[str, float]: Allocation mapping totaling 1.0 (100%).
    """
    style_key = "Balanced"
    for k in STYLE_ALLOCATIONS:
        if k.lower() == str(travel_style).strip().lower():
            style_key = k
            break

    return STYLE_ALLOCATIONS[style_key].copy()


def calculate_base_daily_cost(
    df: pd.DataFrame,
    destination_name: str,
    travel_style: str = "Balanced",
) -> float:
    """Calculate daily baseline cost for a destination calibrated by travel style.

    In this development dataset, 'estimated_cost' represents a typical 3-day trip.
    We convert this into a standardized daily rate: (estimated_cost / 3.0) * style_multiplier.

    Args:
        df: Processed destinations DataFrame.
        destination_name: Destination name.
        travel_style: Selected travel style.

    Returns:
        float: Estimated daily cost per person in INR.
    """
    base_trip_cost = 5000.0  # Dataset median fallback

    if df is not None and not df.empty:
        match = df[df["destination"].str.lower() == destination_name.strip().lower()]
        if not match.empty:
            cost_val = match.iloc[0].get("estimated_cost", 5000.0)
            try:
                base_trip_cost = float(cost_val)
            except (ValueError, TypeError):
                base_trip_cost = 5000.0

    # Convert 3-day dataset anchor to daily baseline
    daily_anchor = base_trip_cost / 3.0

    # Apply style multiplier
    style_key = "Balanced"
    for k in STYLE_COST_MULTIPLIERS:
        if k.lower() == str(travel_style).strip().lower():
            style_key = k
            break

    multiplier = STYLE_COST_MULTIPLIERS.get(style_key, 1.0)
    return round(daily_anchor * multiplier, 2)


def estimate_expenses(
    total_cost: float,
    travel_style: str = "Balanced",
) -> dict[str, int]:
    """Breakdown total estimated cost into 5 granular expenditure categories.

    Categories: Accommodation, Food, Transportation, Activities, Miscellaneous.
    Ensures sum of categories equals total_cost exactly (handling rounding differences).

    Args:
        total_cost: Overall estimated trip expense.
        travel_style: Selected travel style.

    Returns:
        dict[str, int]: Integer expense allocations in INR.
    """
    allocations = get_style_allocations(travel_style)
    breakdown: dict[str, int] = {}
    accumulated = 0

    categories = list(allocations.keys())
    for cat in categories[:-1]:
        share = allocations[cat]
        amt = int(round(total_cost * share))
        breakdown[cat] = amt
        accumulated += amt

    # Last category absorbs any rounding discrepancy
    last_cat = categories[-1]
    breakdown[last_cat] = max(0, int(round(total_cost)) - accumulated)

    return breakdown


def calculate_total_budget(
    df: pd.DataFrame,
    destination_name: str,
    duration_days: int = 3,
    travel_style: str = "Balanced",
) -> dict[str, Any]:
    """Calculate comprehensive trip budget estimation.

    Args:
        df: Destination DataFrame.
        destination_name: Destination name.
        duration_days: Length of stay in days (1 to 10).
        travel_style: Travel style name.

    Returns:
        dict: Detailed budget breakdown, total, and daily average.
    """
    # Clamp duration safely between 1 and 10 days
    days = max(1, min(int(duration_days), 10))

    daily_cost = calculate_base_daily_cost(df, destination_name, travel_style)
    total_estimated = round(daily_cost * days)

    expenses = estimate_expenses(total_estimated, travel_style)

    return {
        "destination": destination_name,
        "duration_days": days,
        "travel_style": travel_style,
        "daily_average": int(round(daily_cost)),
        "total_estimated": int(total_estimated),
        "expenses": expenses,
    }


def compare_with_user_budget(
    estimated_total: int,
    user_budget: int | None,
) -> dict[str, Any]:
    """Compare total estimated trip cost against user's target budget.

    Args:
        estimated_total: Estimated trip total in INR.
        user_budget: User's planned budget in INR.

    Returns:
        dict: Status ('Within Budget', 'Exact Match', 'Over Budget', 'No Budget Set'),
              variance amount, and utilization percentage.
    """
    if user_budget is None or user_budget <= 0:
        return {
            "status": "No Budget Set",
            "difference": 0,
            "utilization_pct": 0.0,
            "user_budget": None,
            "estimated_total": estimated_total,
        }

    diff = user_budget - estimated_total
    utilization = round((estimated_total / user_budget) * 100, 1)

    if diff > 0:
        status = "Within Budget"
    elif diff == 0:
        status = "Budget Fully Utilized"
    else:
        status = "Over Budget"

    return {
        "status": status,
        "difference": abs(diff),
        "is_over_budget": diff < 0,
        "utilization_pct": utilization,
        "user_budget": user_budget,
        "estimated_total": estimated_total,
    }


def generate_budget_suggestions(
    df: pd.DataFrame,
    destination_name: str,
    duration_days: int,
    travel_style: str,
    user_budget: int | None,
    current_estimated_total: int,
) -> list[dict[str, Any]]:
    """Generate practical, deterministic cost-saving adjustments if over budget or optimizing.

    Args:
        df: Destination DataFrame.
        destination_name: Name of destination.
        duration_days: Trip duration in days.
        travel_style: Current style.
        user_budget: Target budget.
        current_estimated_total: Current projected total.

    Returns:
        list[dict]: Ranked list of potential optimizations with estimated savings.
    """
    suggestions = []

    # If within budget, return optimization tips
    if user_budget is not None and current_estimated_total <= user_budget:
        savings_surplus = user_budget - current_estimated_total
        suggestions.append({
            "title": "Comfort Upgrade / Experience Buffer",
            "description": f"You have approximately ₹{savings_surplus:,} remaining in your budget. You can upgrade accommodation or reserve funds for artisanal souvenirs.",
            "estimated_savings": 0,
            "new_total": current_estimated_total,
        })
        return suggestions

    # Over budget scenario -> Generate ranked savings levers

    # Lever 1: Switch travel style to 'Budget' if not already Budget
    if travel_style.lower() != "budget":
        budget_plan = calculate_total_budget(df, destination_name, duration_days, "Budget")
        savings = current_estimated_total - budget_plan["total_estimated"]
        if savings > 0:
            suggestions.append({
                "title": "Switch Travel Style to 'Budget'",
                "description": f"Opting for economical homestays, public transit, and standard dining reduces projected expenditure to approximately ₹{budget_plan['total_estimated']:,}.",
                "estimated_savings": savings,
                "new_total": budget_plan["total_estimated"],
            })

    # Lever 2: Reduce duration by 1 day (if duration > 1)
    if duration_days > 1:
        shorter_plan = calculate_total_budget(df, destination_name, duration_days - 1, travel_style)
        savings = current_estimated_total - shorter_plan["total_estimated"]
        if savings > 0:
            suggestions.append({
                "title": f"Reduce Trip Length to {duration_days - 1} Days",
                "description": f"Trimming your trip duration by 1 day saves 1 full day of lodging, dining, and intra-city travel, bringing cost to ~₹{shorter_plan['total_estimated']:,}.",
                "estimated_savings": savings,
                "new_total": shorter_plan["total_estimated"],
            })

    # Lever 3: Reduce accommodation allocation (Economy Stay Strategy)
    current_expenses = estimate_expenses(current_estimated_total, travel_style)
    current_stay = current_expenses.get("Accommodation", 0)
    economy_stay_savings = int(round(current_stay * 0.25))
    if economy_stay_savings > 0:
        new_total_stay = current_estimated_total - economy_stay_savings
        suggestions.append({
            "title": "Choose Alternative / Boutique Guesthouses",
            "description": f"Selecting comfortable guesthouses or verified B&Bs over full-service resorts can save ~25% on lodging (~₹{economy_stay_savings:,}).",
            "estimated_savings": economy_stay_savings,
            "new_total": new_total_stay,
        })

    # Lever 4: Off-Peak / Shoulder Season Dining & Self-Paced Sightseeing
    activity_savings = int(round(current_expenses.get("Activities", 0) * 0.30))
    if activity_savings > 0:
        new_total_act = current_estimated_total - activity_savings
        suggestions.append({
            "title": "Prioritize Self-Guided & Nature Activities",
            "description": f"Focusing on natural viewpoints, heritage walks, and public monuments rather than premium guided packages saves ~₹{activity_savings:,}.",
            "estimated_savings": activity_savings,
            "new_total": new_total_act,
        })

    # Sort suggestions by estimated savings descending
    suggestions.sort(key=lambda s: s["estimated_savings"], reverse=True)
    return suggestions
