"""Conversational manager handling dialogue state, follow-ups, and recommendation handoff."""
from typing import Any
import pandas as pd
from src.query_parser import parse_travel_query, update_preferences_state
from src.recommendation import calculate_content_recommendations
from src.utils import format_currency_inr


def init_conversation_state(stored_profile: dict[str, Any] | None = None) -> dict[str, Any]:
    """Initialize a new conversation session state, optionally bootstrapping from traveler profile.

    Args:
        stored_profile: Optional traveler profile from st.session_state["traveler_profile"].

    Returns:
        dict: Fresh conversational state.
    """
    initial_prefs: dict[str, Any] = {
        "budget": None,
        "duration": None,
        "categories": [],
        "travel_style": None,
        "season": None,
        "activities": [],
    }

    if stored_profile:
        if stored_profile.get("categories"):
            initial_prefs["categories"] = list(stored_profile["categories"])
        if stored_profile.get("persona_type"):
            initial_prefs["travel_style"] = stored_profile["persona_type"]
        if stored_profile.get("preferred_season"):
            initial_prefs["season"] = stored_profile["preferred_season"]
        if stored_profile.get("preferred_activities"):
            initial_prefs["activities"] = [stored_profile["preferred_activities"]]
        if stored_profile.get("budget_tier"):
            # Approximate budget tier baseline if present
            bt = str(stored_profile["budget_tier"]).lower()
            if "budget" in bt:
                initial_prefs["budget"] = 5000
            elif "moderate" in bt:
                initial_prefs["budget"] = 10000
            elif "luxury" in bt:
                initial_prefs["budget"] = 18000

    welcome_msg = (
        "Hello! I am your AI Travel Assistant. ✈️\n\n"
        "Tell me about your travel plans! For instance: *\"I want a peaceful beach trip under ₹15000 for 3 days\"* "
        "or *\"Looking for an adventure in Himachal for a week\"*."
    )

    if stored_profile and stored_profile.get("name"):
        welcome_msg = f"Welcome back, **{stored_profile['name']}**! ✈️\n\n" + welcome_msg

    return {
        "messages": [
            {"role": "assistant", "message": welcome_msg, "recommendations": None}
        ],
        "preferences": initial_prefs,
    }


def process_user_turn(
    user_input: str,
    conv_state: dict[str, Any],
    destinations_df: pd.DataFrame,
) -> dict[str, Any]:
    """Process a single turn of user input: parse query, update state, generate response or recommendations.

    Args:
        user_input: Natural language query entered by user.
        conv_state: Current conversation state dict containing 'messages' and 'preferences'.
        destinations_df: Processed destinations DataFrame.

    Returns:
        dict: Updated conversation state.
    """
    if not user_input or not user_input.strip():
        return conv_state

    # 1. Parse natural language input
    extracted = parse_travel_query(user_input)

    # 2. Update ongoing preferences
    updated_prefs = update_preferences_state(conv_state["preferences"], extracted)
    conv_state["preferences"] = updated_prefs

    # Append user message
    conv_state["messages"].append({
        "role": "user",
        "message": user_input.strip(),
        "recommendations": None,
    })

    # 3. Determine if we have sufficient information to trigger recommendations
    # We consider information sufficient if:
    # - User has at least one category OR travel style/activity, AND an approximate budget OR duration
    # OR user explicitly asked for recommendations / matches
    has_category = bool(updated_prefs.get("categories"))
    has_budget = updated_prefs.get("budget") is not None
    has_duration = updated_prefs.get("duration") is not None
    has_style = bool(updated_prefs.get("travel_style"))
    has_activity = bool(updated_prefs.get("activities"))

    recs_df = pd.DataFrame()
    assistant_response = ""

    # Check for unrelated/out-of-domain input (no travel signal at all)
    travel_keywords = ["trip", "travel", "vacation", "holiday", "tour", "visit", "destination", "place", "places", "go", "where"]
    has_travel_keyword = any(kw in user_input.lower() for kw in travel_keywords)
    
    has_any_signal = has_category or has_budget or has_duration or has_style or has_activity or has_travel_keyword

    if not has_any_signal:
        assistant_response = (
            "I am specialized in travel planning and destination discovery across India. "
            "Could you tell me what kind of trip you have in mind—such as a beach getaway, nature retreat, or heritage exploration?"
        )
    elif not has_category and not has_activity and not has_style:

        # Ask for interest / theme
        assistant_response = (
            "That sounds like a great plan! What kind of experience are you looking for—beach, nature, heritage, adventure, or spiritual?"
        )
    elif not has_budget and not has_duration:
        # Prompt for budget or duration
        cat_str = ", ".join(updated_prefs.get("categories", [])) or "travel"
        assistant_response = (
            f"Wonderful, I noted your interest in **{cat_str}**! "
            "What is your approximate budget or preferred trip duration (e.g. *₹15,000 for 3 days*)?"
        )
    else:
        # We have enough preference attributes to invoke Phase 2 recommendation engine!
        # Convert structured preferences into profile representation expected by recommendation.py
        pref_for_rec = {
            "categories": updated_prefs.get("categories", []),
            "persona_type": updated_prefs.get("travel_style", ""),
            "preferred_season": updated_prefs.get("season", ""),
            "preferred_activities": ", ".join(updated_prefs.get("activities", [])),
        }
        
        # Add budget tier hint to recommendation profile
        budget_val = updated_prefs.get("budget")
        if budget_val:
            if budget_val <= 5000:
                pref_for_rec["budget_tier"] = "Budget"
            elif budget_val <= 10000:
                pref_for_rec["budget_tier"] = "Moderate"
            else:
                pref_for_rec["budget_tier"] = "Luxury"

        # Calculate recommendations via Phase 2 engine
        recs_df = calculate_content_recommendations(
            df=destinations_df,
            profile=pref_for_rec,
            user_query=user_input,
            top_n=3,
        )

        # Formulate conversational narrative
        summary_parts = []
        if updated_prefs.get("categories"):
            summary_parts.append(f"**{', '.join(updated_prefs['categories'])}** themes")
        if updated_prefs.get("budget"):
            summary_parts.append(f"a budget around **{format_currency_inr(updated_prefs['budget'])}**")
        if updated_prefs.get("duration"):
            summary_parts.append(f"a **{updated_prefs['duration']}-day** duration")
        if updated_prefs.get("travel_style"):
            summary_parts.append(f"a **{updated_prefs['travel_style']}** style")

        summary_desc = ", ".join(summary_parts) if summary_parts else "your travel interests"
        assistant_response = (
            f"Based on {summary_desc}, here are top destination recommendations matched from our curated dataset:"
        )

    # Append assistant turn
    conv_state["messages"].append({
        "role": "assistant",
        "message": assistant_response,
        "recommendations": recs_df if not recs_df.empty else None,
    })

    return conv_state
