"""Natural language query parser for extracting travel parameters.

Extracts:
- Budget (numeric, k-format, INR/₹ symbols)
- Duration (number of days)
- Travel Categories/Interests (mapped to dataset themes)
- Travel Style/Vibe
- Season / Months
- Activity keywords
"""
import re
from typing import Any


# Dataset theme taxonomy mapping
CATEGORY_MAP: dict[str, list[str]] = {
    "Beach": ["beach", "beaches", "coast", "coastal", "sea", "ocean", "island", "islands", "shores"],
    "Heritage": ["heritage", "culture", "cultural", "history", "historical", "palace", "palaces", "fort", "forts", "monument", "monuments", "ruins", "royal"],
    "Nature": ["nature", "hill station", "hills", "mountain", "mountains", "tea", "estate", "waterfall", "waterfalls", "scenic", "greenery", "backwaters", "forest"],
    "Adventure": ["adventure", "trekking", "trek", "hiking", "hike", "rafting", "river rafting", "paragliding", "skiing", "bouldering", "camping", "scuba", "bungee"],
    "Spiritual": ["spiritual", "temple", "temples", "ghat", "ghats", "aarti", "pilgrimage", "ashram", "holy", "yoga"],
}

# Travel style keywords
STYLE_KEYWORDS: dict[str, list[str]] = {
    "Relaxed": ["peaceful", "relaxed", "relaxing", "calm", "serene", "chill", "leisure", "slow"],
    "Adventurous": ["adventurous", "thrilling", "action", "exciting", "wild", "intense"],
    "Cultural": ["cultural", "traditional", "historic", "heritage", "folklore"],
    "Romantic": ["romantic", "couple", "honeymoon"],
    "Family": ["family", "kids", "parents", "children"],
    "Budget": ["budget", "cheap", "affordable", "economical", "backpacking", "backpacker"],
    "Luxury": ["luxury", "lavish", "premium", "deluxe", "5-star", "royal"],
}

# Seasons & common travel months
SEASONS_MAP: dict[str, list[str]] = {
    "Winter": ["winter", "december", "january", "february", "cold"],
    "Summer": ["summer", "may", "june", "july", "sunny"],
    "Monsoon": ["monsoon", "rainy", "rains", "august", "september"],
    "Spring": ["spring", "march", "april"],
}

# Activity keywords
ACTIVITY_KEYWORDS = [
    "trekking", "hiking", "scuba diving", "scuba", "snorkeling", "rafting",
    "paragliding", "skiing", "camping", "photography", "sightseeing", "boating",
    "coracle", "bungee jumping", "yoga", "temple visit", "boat ride",
    "tea tasting", "safari", "desert safari", "bouldering", "houseboat"
]


def extract_budget(text: str) -> int | None:
    """Extract budget amount from user text.

    Supports:
    - k format: '15k', '20K', '8.5k'
    - rupee currency: '₹15000', '15,000 rupees', 'inr 15000'
    - preposition patterns: 'under 15000', 'around 20000', 'budget 10000'

    Args:
        text: Input natural language string.

    Returns:
        int | None: Extracted budget in INR or None.
    """
    if not text:
        return None

    clean_text = text.lower().replace(",", "")

    # 1. Look for 'k' format: e.g. 15k, 20.5k, ₹15k, 10 k
    k_match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*k\b', clean_text)
    if k_match:
        try:
            val = float(k_match.group(1))
            return int(val * 1000)
        except (ValueError, TypeError):
            pass

    # 2. Look for explicit currency with numbers: e.g. ₹15000, 15000 rupees, inr 12000
    currency_match = re.search(r'(?:₹|rs\.?|inr)\s*(\d{3,7})', clean_text)
    if currency_match:
        return int(currency_match.group(1))

    currency_after = re.search(r'(\d{3,7})\s*(?:rs|rupees|inr|bucks)', clean_text)
    if currency_after:
        return int(currency_after.group(1))

    # 3. Contextual indicators: 'budget 15000', 'under 20000', 'spend 8000', 'max 12000'
    ctx_match = re.search(r'(?:budget|under|below|around|within|upto|up to|spend|spending|max)\s*(?:of|is|around)?\s*(\d{3,7})', clean_text)
    if ctx_match:
        return int(ctx_match.group(1))

    # 4. Standalone 4-6 digit number if reasonable budget range (1000 to 500000)
    standalone_numbers = re.findall(r'\b(\d{4,6})\b', clean_text)
    if standalone_numbers:
        # Return first reasonable amount
        for num_str in standalone_numbers:
            val = int(num_str)
            if 1000 <= val <= 200000:
                return val

    return None


def extract_duration(text: str) -> int | None:
    """Extract trip duration in days.

    Supports:
    - '3 days', 'for 5 days', '4-day trip', '2 nights'
    - 'weekend' -> 2 days, 'long weekend' -> 3 days, 'a week' -> 7 days

    Args:
        text: User query.

    Returns:
        int | None: Number of days or None.
    """
    if not text:
        return None

    clean_text = text.lower()

    if "long weekend" in clean_text:
        return 3
    if "weekend" in clean_text:
        return 2
    if "a week" in clean_text or "one week" in clean_text or "1 week" in clean_text:
        return 7
    if "two weeks" in clean_text or "2 weeks" in clean_text:
        return 14

    # Direct day match: '3 days', '5-day', '4 day'
    day_match = re.search(r'\b(\d{1,2})\s*(?:-| )?(?:day|days)\b', clean_text)
    if day_match:
        return int(day_match.group(1))

    # Night match: '3 nights' -> 4 days
    night_match = re.search(r'\b(\d{1,2})\s*(?:-| )?(?:night|nights)\b', clean_text)
    if night_match:
        return int(night_match.group(1)) + 1

    return None


def extract_categories(text: str) -> list[str]:
    """Recognize travel themes/categories represented in dataset."""
    if not text:
        return []

    clean_text = text.lower()
    found = []

    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            # Word boundary matching
            if re.search(rf'\b{re.escape(kw)}\b', clean_text):
                if category not in found:
                    found.append(category)
                break

    return found


def extract_travel_style(text: str) -> str | None:
    """Extract travel style / vibe (e.g. Relaxed, Adventurous, Romantic, Family, Budget, Luxury)."""
    if not text:
        return None

    clean_text = text.lower()
    for style, keywords in STYLE_KEYWORDS.items():
        for kw in keywords:
            if re.search(rf'\b{re.escape(kw)}\b', clean_text):
                return style

    return None


def extract_season(text: str) -> str | None:
    """Recognize season or month."""
    if not text:
        return None

    clean_text = text.lower()
    for season, keywords in SEASONS_MAP.items():
        for kw in keywords:
            if re.search(rf'\b{re.escape(kw)}\b', clean_text):
                return season

    return None


def extract_activities(text: str) -> list[str]:
    """Extract recognized activity keywords from user text."""
    if not text:
        return []

    clean_text = text.lower()
    found = []
    for act in ACTIVITY_KEYWORDS:
        if re.search(rf'\b{re.escape(act)}\b', clean_text):
            found.append(act)

    return found


def parse_travel_query(text: str) -> dict[str, Any]:
    """Parse a natural language travel query into a structured preference dictionary.

    Args:
        text: User query string.

    Returns:
        dict[str, Any]: Extracted attributes.
    """
    if not text or not text.strip():
        return {
            "budget": None,
            "duration": None,
            "categories": [],
            "travel_style": None,
            "season": None,
            "activities": [],
            "raw_query": "",
        }

    return {
        "budget": extract_budget(text),
        "duration": extract_duration(text),
        "categories": extract_categories(text),
        "travel_style": extract_travel_style(text),
        "season": extract_season(text),
        "activities": extract_activities(text),
        "raw_query": text.strip(),
    }


def update_preferences_state(
    current_state: dict[str, Any],
    new_extracted: dict[str, Any],
) -> dict[str, Any]:
    """Merge newly extracted preferences into ongoing conversation state.

    Allows user preference updates/corrections while preserving earlier context.
    """
    updated = current_state.copy()

    # Update budget if found
    if new_extracted.get("budget") is not None:
        updated["budget"] = new_extracted["budget"]

    # Update duration if found
    if new_extracted.get("duration") is not None:
        updated["duration"] = new_extracted["duration"]

    # Categories: If new categories specified, update or replace
    new_cats = new_extracted.get("categories", [])
    if new_cats:
        updated["categories"] = new_cats

    # Travel style
    if new_extracted.get("travel_style") is not None:
        updated["travel_style"] = new_extracted["travel_style"]

    # Season
    if new_extracted.get("season") is not None:
        updated["season"] = new_extracted["season"]

    # Activities: accumulate unique
    new_acts = new_extracted.get("activities", [])
    if new_acts:
        existing_acts = updated.get("activities", [])
        combined = list(set(existing_acts + new_acts))
        updated["activities"] = combined

    return updated
