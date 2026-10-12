"""Saved Trips and Itinerary Bookmark Management module.

Provides:
- Normalization of saved trip payloads (including budget and itinerary information)
- Duplicate-safe saving
- Retrieval, deletion, and clearing of saved trips
- Multi-trip side-by-side comparison matrix
- Structured JSON and formatted plain-text exports
"""
from datetime import datetime
import json
from typing import Any
import pandas as pd


def normalize_saved_trip(trip: dict[str, Any] | None) -> dict[str, Any] | None:
    """Normalize and validate a saved trip object into a consistent schema.

    Schema:
    - id: Unique string identifier
    - destination: Destination name (str)
    - state: State or territory (str)
    - category: Theme/category (str)
    - duration_days: Number of days (int)
    - travel_style: Travel style/pacing (str)
    - estimated_cost: Base or estimated cost (int/float)
    - rating: Rating score (float)
    - best_season: Best season for travel (str)
    - interests: User interests/keywords (list of str)
    - days: List of day plans with slots (Morning, Afternoon, Evening)
    - budget: Budget breakdown dictionary (optional, if available)
    - saved_at: ISO timestamp of when trip was saved (str)

    Args:
        trip: Dictionary representing trip plan or itinerary.

    Returns:
        dict[str, Any] | None: Standardized dictionary or None if invalid.
    """
    if not trip or not isinstance(trip, dict):
        return None

    dest = str(trip.get("destination", "")).strip()
    if not dest or dest.lower() == "none":
        return None

    duration = trip.get("duration_days", 1)
    try:
        duration_int = max(1, int(duration))
    except (ValueError, TypeError):
        duration_int = 1

    # Extract or generate stable trip ID
    trip_id = trip.get("id")
    if not trip_id:
        timestamp_slug = datetime.now().strftime("%Y%m%d%H%M%S")
        dest_slug = dest.lower().replace(" ", "_")
        trip_id = f"{dest_slug}_{duration_int}d_{timestamp_slug}"

    # Extract days list
    days_data = trip.get("days", [])
    if not isinstance(days_data, list):
        days_data = []

    # Clean interests
    interests_raw = trip.get("user_interests", trip.get("interests", []))
    if isinstance(interests_raw, list):
        clean_interests = [str(i).strip() for i in interests_raw if str(i).strip()]
    elif isinstance(interests_raw, str) and interests_raw.strip():
        clean_interests = [i.strip() for i in interests_raw.split(",") if i.strip()]
    else:
        clean_interests = []

    # Estimated cost
    cost_val = trip.get("estimated_cost", 0)
    try:
        cost_num = float(cost_val)
    except (ValueError, TypeError):
        cost_num = 0.0

    return {
        "id": str(trip_id),
        "destination": dest,
        "state": str(trip.get("state", "")).strip(),
        "category": str(trip.get("category", "General")).strip(),
        "duration_days": duration_int,
        "travel_style": str(trip.get("travel_style", "Balanced")).strip(),
        "estimated_cost": int(round(cost_num)),
        "rating": float(trip.get("rating", 4.5)),
        "best_season": str(trip.get("best_season", "All Year")).strip(),
        "interests": clean_interests,
        "days": days_data,
        "budget": trip.get("budget"),
        "saved_at": trip.get("saved_at", datetime.now().strftime("%Y-%m-%d %H:%M")),
    }


def is_duplicate_trip(existing_trips: list[dict[str, Any]], new_trip: dict[str, Any]) -> bool:
    """Check if an identical trip (matching destination, duration, and style) already exists.

    Args:
        existing_trips: List of currently saved trips.
        new_trip: Normalized trip to check.

    Returns:
        bool: True if duplicate exists, False otherwise.
    """
    for t in existing_trips:
        norm_t = normalize_saved_trip(t)
        if norm_t:
            if (
                norm_t["destination"].lower() == new_trip["destination"].lower()
                and norm_t["duration_days"] == new_trip["duration_days"]
                and norm_t["travel_style"].lower() == new_trip["travel_style"].lower()
            ):
                return True
    return False


def save_trip(
    saved_trips_list: list[dict[str, Any]],
    trip_to_save: dict[str, Any],
    prevent_duplicates: bool = True,
) -> tuple[list[dict[str, Any]], bool, str]:
    """Save an itinerary into the saved trips list safely.

    Args:
        saved_trips_list: Current list of saved trips from session state.
        trip_to_save: Itinerary dictionary.
        prevent_duplicates: Whether to reject identical trip saves.

    Returns:
        tuple[list[dict], bool, str]: (Updated trips list, success boolean, status message).
    """
    normalized = normalize_saved_trip(trip_to_save)
    if not normalized:
        return saved_trips_list, False, "Cannot save invalid or empty itinerary."

    current_list = list(saved_trips_list) if saved_trips_list else []

    if prevent_duplicates and is_duplicate_trip(current_list, normalized):
        return (
            current_list,
            False,
            f"Trip to {normalized['destination']} ({normalized['duration_days']} days, {normalized['travel_style']} style) is already saved in your bookmarks.",
        )

    current_list.append(normalized)
    return current_list, True, f"Successfully saved trip to {normalized['destination']}!"


def delete_trip(
    saved_trips_list: list[dict[str, Any]],
    trip_identifier: str | int,
) -> tuple[list[dict[str, Any]], bool]:
    """Delete an individual saved trip by its ID or list index.

    Args:
        saved_trips_list: Current list of saved trips.
        trip_identifier: String ID or integer index.

    Returns:
        tuple[list[dict], bool]: (Updated list, success boolean).
    """
    if not saved_trips_list:
        return [], False

    # Check index-based deletion
    if isinstance(trip_identifier, int) and 0 <= trip_identifier < len(saved_trips_list):
        new_list = list(saved_trips_list)
        new_list.pop(trip_identifier)
        return new_list, True

    # ID-based deletion
    str_id = str(trip_identifier).strip()
    filtered = [t for t in saved_trips_list if str(t.get("id", "")).strip() != str_id]

    if len(filtered) < len(saved_trips_list):
        return filtered, True

    return saved_trips_list, False


def clear_saved_trips() -> list[dict[str, Any]]:
    """Return an empty list to clear all saved trips."""
    return []


def get_saved_trips(session_saved: Any) -> list[dict[str, Any]]:
    """Retrieve and normalize all saved trips from session storage.

    Args:
        session_saved: Value from st.session_state.get('saved_trips').

    Returns:
        list[dict]: List of normalized trip dictionaries.
    """
    if not session_saved or not isinstance(session_saved, list):
        return []

    normalized_all = []
    for item in session_saved:
        norm = normalize_saved_trip(item)
        if norm:
            normalized_all.append(norm)

    return normalized_all


def compare_trips(trips: list[dict[str, Any]]) -> pd.DataFrame:
    """Construct a clean comparison DataFrame across multiple selected trips.

    Args:
        trips: List of trip dictionaries to compare.

    Returns:
        pd.DataFrame: Tabular comparison with attributes as rows or columns.
    """
    if not trips:
        return pd.DataFrame()

    records = []
    for t in trips:
        norm = normalize_saved_trip(t)
        if not norm:
            continue

        records.append({
            "Destination": norm["destination"],
            "State": norm.get("state", "N/A"),
            "Theme": norm.get("category", "N/A"),
            "Duration (Days)": norm["duration_days"],
            "Travel Style": norm["travel_style"],
            "Estimated Cost (INR)": f"₹{norm['estimated_cost']:,}",
            "Rating": f"⭐ {norm.get('rating', 4.5)}",
            "Best Season": norm.get("best_season", "All Year"),
            "Key Focus": ", ".join(norm.get("interests", [])) or "General Exploration",
        })

    return pd.DataFrame(records)


def export_trip_json(trip: dict[str, Any]) -> str:
    """Export a saved trip into clean formatted JSON string.

    Args:
        trip: Saved trip dictionary.

    Returns:
        str: Indented JSON string.
    """
    norm = normalize_saved_trip(trip)
    if not norm:
        return json.dumps({"error": "Invalid trip data"}, indent=2)

    return json.dumps(norm, indent=2, ensure_ascii=False)


def export_trip_text(trip: dict[str, Any]) -> str:
    """Export a saved trip into a readable, comprehensive plain-text itinerary document.

    Args:
        trip: Saved trip dictionary.

    Returns:
        str: Formatted plain-text itinerary.
    """
    norm = normalize_saved_trip(trip)
    if not norm:
        return "Error: Invalid trip data."

    lines = []
    lines.append("=" * 60)
    lines.append(" TRAVEL INTELLIGENCE — PERSONALIZED ITINERARY")
    lines.append("=" * 60)
    lines.append(f"Destination:     {norm['destination']}, {norm.get('state', '')}")
    lines.append(f"Trip Duration:   {norm['duration_days']} Days")
    lines.append(f"Travel Style:    {norm['travel_style']}")
    lines.append(f"Theme / Category:{norm.get('category', 'General')}")
    lines.append(f"Estimated Cost:  ₹{norm['estimated_cost']:,}")
    lines.append(f"Best Season:     {norm.get('best_season', 'All Year')}")
    lines.append(f"Visitor Rating:  ⭐ {norm.get('rating', 4.5)} / 5.0")
    if norm.get("interests"):
        lines.append(f"Focus Interests: {', '.join(norm['interests'])}")
    lines.append(f"Bookmarked On:   {norm.get('saved_at', 'N/A')}")
    lines.append("-" * 60)

    # Budget Breakdown if available
    budget_info = norm.get("budget")
    if budget_info and isinstance(budget_info, dict):
        lines.append("\nESTIMATED BUDGET BREAKDOWN:")
        expenses = budget_info.get("expenses", {})
        for cat, amt in expenses.items():
            lines.append(f"  • {cat:15}: ₹{amt:,}")
        lines.append("-" * 60)

    # Day-by-Day schedule
    lines.append("\nDAY-BY-DAY SCHEDULE:\n")
    days = norm.get("days", [])
    if not days:
        lines.append("  (No daily slots recorded for this itinerary.)")
    else:
        for day_obj in days:
            day_num = day_obj.get("day", 1)
            theme_focus = day_obj.get("theme_focus", f"Day {day_num}")
            slots = day_obj.get("slots", {})

            lines.append(f"--- {theme_focus.upper()} ---")
            for slot_name in ["Morning", "Afternoon", "Evening"]:
                slot_data = slots.get(slot_name, {})
                title = slot_data.get("title", f"{slot_name} Activity")
                desc = slot_data.get("description", "")
                pace = slot_data.get("pace", "Standard")
                lines.append(f"  [{slot_name}] {title} (Pace: {pace})")
                if desc:
                    lines.append(f"    Details: {desc}")
            lines.append("")

    lines.append("=" * 60)
    lines.append("Generated by AI-Powered Travel Intelligence & Trip Planning System")
    lines.append("=" * 60)
    return "\n".join(lines)
