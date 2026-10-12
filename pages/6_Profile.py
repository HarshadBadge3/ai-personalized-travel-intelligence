"""Traveler Profile - Configuration module for travel preferences."""
import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ui_components import apply_custom_css

st.set_page_config(page_title="Traveler Profile | Travel Intelligence", page_icon="👤", layout="wide")

apply_custom_css()

st.title("👤 Traveler Persona & Preferences")
st.markdown("Set your travel profile settings. In later phases, this profile will calibrate the recommendation engine.")

col1, col2 = st.columns([1.2, 0.8])

with col1:
    with st.form("profile_form"):
        st.subheader("Your Travel Persona")
        name = st.text_input("Traveler Name", value="Explorer")
        persona_type = st.selectbox(
            "Primary Travel Style",
            ["Solo Backpacker", "Couple / Romantic", "Family with Kids", "Adventure Group", "Luxury Seeker", "Cultural & Heritage Enthusiast"],
        )
        preferred_pace = st.select_slider(
            "Preferred Pacing",
            options=["Relaxed (1-2 spots/day)", "Moderate (3-4 spots/day)", "Fast-paced (5+ spots/day)"],
            value="Moderate (3-4 spots/day)",
        )
        fav_categories = st.multiselect(
            "Favorite Categories",
            ["Heritage", "Nature", "Adventure", "Beach", "Spiritual", "Culinary"],
            default=["Heritage", "Nature"],
        )
        pref_season = st.selectbox(
            "Preferred Season",
            ["Any Season", "Winter", "Summer", "Monsoon", "Spring"],
            index=0,
        )
        standard_budget = st.selectbox(
            "Default Budget Tier",
            ["Budget (Under ₹5,000/trip)", "Moderate (₹5,000 - ₹10,000/trip)", "Luxury (Above ₹10,000/trip)"],
            index=1,
        )
        pref_activities = st.text_input(
            "Specific Activity Interests (Optional)",
            value="Sightseeing, local food, culture",
            placeholder="e.g. trekking, scuba diving, temples, photography",
        )
        
        submitted = st.form_submit_button("Save Profile Settings")
        if submitted:
            st.session_state["traveler_profile"] = {
                "name": name,
                "persona_type": persona_type,
                "pace": preferred_pace,
                "categories": fav_categories,
                "preferred_season": "" if pref_season == "Any Season" else pref_season,
                "budget_tier": standard_budget,
                "preferred_activities": pref_activities,
            }
            st.success(f"Profile saved for **{name}**! Click **7_Recommendations** in the sidebar to view personalized suggestions.")

with col2:
    st.subheader("Profile State Preview")
    current_profile = st.session_state.get(
        "traveler_profile",
        {
            "name": "Explorer (Default)",
            "persona_type": "Cultural & Heritage Enthusiast",
            "pace": "Moderate (3-4 spots/day)",
            "categories": ["Heritage", "Nature"],
            "budget_tier": "Moderate",
        },
    )
    st.json(current_profile)
    st.info("💡 **Session Scope:** Preferences saved here persist across the current session and provide context for multi-page personalization.")
