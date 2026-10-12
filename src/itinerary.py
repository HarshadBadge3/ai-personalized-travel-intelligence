"""Smart Day-by-Day Itinerary Generator module.

Generates realistic, paced daily schedules (Morning, Afternoon, Evening)
tailored to destination, trip duration, travel style/pacing, and interests.
"""
from typing import Any
import pandas as pd


# Time-of-day classification heuristics for activity categories
SLOT_PREFERENCES: dict[str, list[str]] = {
    "Morning": [
        "sunrise", "temple", "aarti", "trek", "trekking", "monument", "fort",
        "heritage walk", "morning walk", "yoga", "nature walk", "plantation", "cycling", "safari"
    ],
    "Afternoon": [
        "museum", "palace", "scuba", "snorkeling", "rafting", "waterfall",
        "beach hopping", "paragliding", "indoor", "shopping", "tea tasting",
        "tasting", "cafe", "boat ride", "boating", "sightseeing"
    ],
    "Evening": [
        "sunset", "sunset cruise", "aarti", "stargazing", "street food",
        "nightlife", "promenade", "folk music", "folk shows", "campfire",
        "camping", "dinner", "rooftop dining", "seafood", "cafes", "leisure"
    ],
}

# General fallback contextual activities per theme to enrich variety across days
THEME_FALLBACK_ACTIVITIES: dict[str, list[dict[str, str]]] = {
    "Heritage": [
        {"slot": "Morning", "title": "Historical Monument Walk", "desc": "Visit local architectural landmarks early to beat crowds and enjoy photography."},
        {"slot": "Afternoon", "title": "Traditional Craft & Artisan Bazaar", "desc": "Explore regional handicraft shops and historic textile/spice markets."},
        {"slot": "Evening", "title": "Cultural Heritage & Folk Show", "desc": "Attend an evening traditional performance, light-and-sound show, or heritage dining."},
    ],
    "Beach": [
        {"slot": "Morning", "title": "Coastline Stroll & Coastal Breeze", "desc": "Relax with an early morning walk along quieter beaches and shoreline viewpoints."},
        {"slot": "Afternoon", "title": "Coastal Water Adventures & Beachside Shacks", "desc": "Enjoy swimming, water sports, and local seaside cuisine."},
        {"slot": "Evening", "title": "Sunset Viewpoint & Promenade Walk", "desc": "Unwind with sunset views over the ocean followed by vibrant coastal dining."},
    ],
    "Nature": [
        {"slot": "Morning", "title": "Misty Viewpoint & Nature Walk", "desc": "Hike to scenic outlooks for sunrise panoramic mountain vistas."},
        {"slot": "Afternoon", "title": "Valley & Waterfall Discovery", "desc": "Visit tranquil waterfalls, local botanical reserves, or tea/spice estates."},
        {"slot": "Evening", "title": "Relaxed Mountain Cafe & Local Stroll", "desc": "Enjoy a peaceful evening in cozy cafes sipping hot beverages amidst mountain mist."},
    ],
    "Adventure": [
        {"slot": "Morning", "title": "High-Energy Mountain Activity", "desc": "Embark on guided trekking, river crossings, or rugged trail excursions."},
        {"slot": "Afternoon", "title": "Action Sports & Outdoor Exploration", "desc": "Engage in thrilling water sports, rock climbing, or high-altitude exploration."},
        {"slot": "Evening", "title": "Campfire & Stargazing Session", "desc": "Gather around an evening bonfire, share stories, and observe clear night skies."},
    ],
    "Spiritual": [
        {"slot": "Morning", "title": "Sacred Rituals & Morning Meditations", "desc": "Participate in peaceful morning prayers, temple rituals, or riverside yoga."},
        {"slot": "Afternoon", "title": "Heritage Ashrams & Spiritual Discourse", "desc": "Visit historical ashrams, ancient libraries, and serene meditation halls."},
        {"slot": "Evening", "title": "Evening Aarti & Riverbank Illumination", "desc": "Witness atmospheric evening prayer ceremonies and illuminated sacred ghats."},
    ],
}


def parse_activities(activities_str: str | None) -> list[str]:
    """Parse comma-separated activity string from dataset into a clean list of activities.

    Args:
        activities_str: Comma-separated activities string from dataset.

    Returns:
        list[str]: Clean list of activity names.
    """
    if not activities_str or not isinstance(activities_str, str):
        return []

    tokens = [act.strip() for act in activities_str.split(",") if act.strip()]
    return tokens


def get_destination_activities(df: pd.DataFrame, destination_name: str) -> dict[str, Any]:
    """Retrieve destination details and parsed activities from DataFrame.

    Args:
        df: Processed destinations DataFrame.
        destination_name: Name of destination.

    Returns:
        dict: Destination metadata and parsed activity list.
    """
    match = df[df["destination"].str.lower() == destination_name.strip().lower()]
    if match.empty:
        return {
            "destination": destination_name,
            "category": "Heritage",
            "state": "Unknown",
            "rating": 4.5,
            "estimated_cost": 5000,
            "activities": [],
        }

    row = match.iloc[0]
    acts = parse_activities(str(row.get("activities", "")))
    return {
        "destination": row["destination"],
        "category": row.get("category", "Heritage"),
        "state": row.get("state", ""),
        "rating": float(row.get("rating", 4.5)),
        "estimated_cost": float(row.get("estimated_cost", 5000)),
        "best_season": str(row.get("best_season", "All Year")),
        "activities": acts,
    }


def classify_activity_slot(activity_name: str) -> str:
    """Determine best suited time slot (Morning, Afternoon, Evening) for an activity.

    Args:
        activity_name: Activity title or description.

    Returns:
        str: 'Morning', 'Afternoon', or 'Evening'.
    """
    act_lower = activity_name.lower()

    for slot, kws in SLOT_PREFERENCES.items():
        if any(kw in act_lower for kw in kws):
            return slot

    # Sensible default
    return "Afternoon"


def generate_day_plan(
    day_num: int,
    primary_activity: str | None,
    secondary_activity: str | None,
    destination_theme: str,
    travel_style: str = "Balanced",
) -> dict[str, Any]:
    """Construct morning, afternoon, and evening slots for a single day.

    Args:
        day_num: Day sequence number (1, 2, ...).
        primary_activity: Primary featured activity from dataset.
        secondary_activity: Secondary activity from dataset.
        destination_theme: Category (Heritage, Beach, Nature, Adventure, Spiritual).
        travel_style: Pacing style (Relaxed, Adventurous, Cultural, etc.).

    Returns:
        dict: Single day itinerary structure.
    """
    fallbacks = THEME_FALLBACK_ACTIVITIES.get(
        destination_theme,
        THEME_FALLBACK_ACTIVITIES["Heritage"],
    )

    style_lower = travel_style.lower()

    # Determine morning slot
    if primary_activity and classify_activity_slot(primary_activity) == "Morning":
        morning = {
            "title": primary_activity,
            "description": f"Featured morning activity in {destination_theme.lower()} setting.",
            "pace": "Active" if "adventur" in style_lower else "Standard",
        }
    else:
        m_item = fallbacks[0]
        morning = {
            "title": primary_activity if primary_activity else m_item["title"],
            "description": m_item["desc"],
            "pace": "Gentle" if "relax" in style_lower else "Standard",
        }

    # Determine afternoon slot
    if secondary_activity and classify_activity_slot(secondary_activity) == "Afternoon":
        afternoon = {
            "title": secondary_activity,
            "description": f"Afternoon exploration embracing {destination_theme.lower()} highlights.",
            "pace": "Moderate",
        }
    elif primary_activity and classify_activity_slot(primary_activity) == "Afternoon":
        afternoon = {
            "title": primary_activity,
            "description": f"Midday highlight centered around {destination_theme.lower()}.",
            "pace": "Moderate",
        }
    else:
        a_item = fallbacks[1]
        afternoon = {
            "title": secondary_activity if secondary_activity else a_item["title"],
            "description": a_item["desc"],
            "pace": "Relaxed" if "relax" in style_lower else "Moderate",
        }

    # Determine evening slot
    if secondary_activity and classify_activity_slot(secondary_activity) == "Evening":
        evening = {
            "title": secondary_activity,
            "description": "Evening recreation and dinner experience.",
            "pace": "Leisure",
        }
    elif primary_activity and classify_activity_slot(primary_activity) == "Evening":
        evening = {
            "title": primary_activity,
            "description": "Evening ambiance and local culinary experience.",
            "pace": "Leisure",
        }
    else:
        e_item = fallbacks[2]
        evening = {
            "title": e_item["title"],
            "description": e_item["desc"],
            "pace": "Leisure",
        }

    # Adjust for Relaxed style: Keep afternoon/evening lighter
    if "relax" in style_lower or "peace" in style_lower:
        afternoon["description"] += " (Unrushed pace with ample cafe and rest intervals)."
        evening["description"] += " (Slow-paced evening with relaxed dining)."

    return {
        "day": day_num,
        "theme_focus": f"Day {day_num}: {destination_theme} Immersion",
        "slots": {
            "Morning": morning,
            "Afternoon": afternoon,
            "Evening": evening,
        },
    }


def generate_itinerary(
    df: pd.DataFrame,
    destination_name: str,
    duration_days: int = 3,
    travel_style: str = "Balanced",
    user_interests: list[str] | None = None,
) -> dict[str, Any]:
    """Generate a multi-day day-by-day itinerary for a chosen destination.

    Args:
        df: Processed destinations DataFrame.
        destination_name: Name of destination.
        duration_days: Length of trip (capped safely between 1 and 10 days).
        travel_style: Travel vibe (Relaxed, Adventurous, Cultural, Romantic, Family, Budget, Luxury).
        user_interests: Optional user interest keywords for prioritization.

    Returns:
        dict: Full multi-day itinerary object with metadata and day plans.
    """
    # 1. Validation & bounds clamping
    if not isinstance(duration_days, (int, float)) or duration_days <= 0:
        return {
            "error": "Trip duration must be at least 1 day.",
            "days": [],
            "destination": destination_name,
        }

    # Safe capping to avoid UI abuse (1 to 10 days)
    total_days = max(1, min(int(duration_days), 10))

    # 2. Retrieve destination information
    dest_info = get_destination_activities(df, destination_name)
    raw_activities = dest_info["activities"]
    theme = dest_info["category"]

    # 3. Prioritize activities based on user interests
    prioritized: list[str] = []
    regular: list[str] = []

    if user_interests:
        interests_lower = [str(i).lower() for i in user_interests]
        for act in raw_activities:
            if any(interest in act.lower() for interest in interests_lower):
                prioritized.append(act)
            else:
                regular.append(act)
    else:
        regular = list(raw_activities)

    # Combined ordered activity queue
    activity_pool = prioritized + regular

    # 4. Day-by-day distribution
    days_list = []
    pool_len = len(activity_pool)

    for d in range(1, total_days + 1):
        # Pick 1-2 distinct activities from pool if available
        act1 = activity_pool[(d * 2 - 2) % pool_len] if pool_len > 0 else None
        act2 = activity_pool[(d * 2 - 1) % pool_len] if pool_len > 1 else None

        # Avoid exact duplicate in same day
        if act1 == act2 and pool_len > 2:
            act2 = activity_pool[(d * 2) % pool_len]

        day_plan = generate_day_plan(
            day_num=d,
            primary_activity=act1,
            secondary_activity=act2,
            destination_theme=theme,
            travel_style=travel_style,
        )
        days_list.append(day_plan)

    return {
        "destination": dest_info["destination"],
        "state": dest_info["state"],
        "category": theme,
        "rating": dest_info["rating"],
        "estimated_cost": dest_info["estimated_cost"],
        "best_season": dest_info.get("best_season", "All Year"),
        "duration_days": total_days,
        "travel_style": travel_style,
        "days": days_list,
    }
