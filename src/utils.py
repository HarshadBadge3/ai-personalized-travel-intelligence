"""Utility helpers for filtering, formatting, and UI presentation."""
import pandas as pd


def filter_destinations(
    df: pd.DataFrame,
    search_query: str = "",
    selected_state: str = "All",
    selected_category: str = "All",
    max_budget: int | float | None = None,
    min_rating: float = 0.0,
) -> pd.DataFrame:
    """Filter destination dataframe based on user criteria.

    Args:
        df: Input DataFrame containing destination records.
        search_query: Free text substring to match in destination name or activities.
        selected_state: State filter ("All" ignores filter).
        selected_category: Category filter ("All" ignores filter).
        max_budget: Upper limit for estimated cost.
        min_rating: Minimum required rating.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """
    filtered = df.copy()

    # Search query filter (matches destination or description or activities)
    if search_query and search_query.strip():
        q = search_query.strip().lower()
        query_mask = (
            filtered["destination"].str.lower().str.contains(q, na=False)
            | filtered["description"].str.lower().str.contains(q, na=False)
            | filtered["activities"].str.lower().str.contains(q, na=False)
        )
        filtered = filtered[query_mask]

    # State filter
    if selected_state and selected_state != "All":
        filtered = filtered[filtered["state"] == selected_state]

    # Category filter
    if selected_category and selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category]

    # Budget filter
    if max_budget is not None:
        filtered = filtered[filtered["estimated_cost"] <= max_budget]

    # Rating filter
    if min_rating > 0.0:
        filtered = filtered[filtered["rating"] >= min_rating]

    return filtered


def format_currency_inr(amount: float | int) -> str:
    """Format an integer/float amount as Indian Rupee string."""
    try:
        return f"₹{int(amount):,}"
    except (ValueError, TypeError):
        return f"₹{amount}"
