"""Smart Day-by-Day Trip Planner & Itinerary Generator."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.itinerary import generate_itinerary
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Smart Trip Planner | Travel Intelligence",
    page_icon="🗺️",
    layout="wide",
)

apply_custom_css()

# Header
st.title("🗺️ Smart Day-by-Day Trip Planner")
st.markdown(
    "Generate a realistic, paced daily travel schedule tailored to your destination, trip length, and travel style."
)

# 2. Load Dataset
@st.cache_data
def get_destinations_data():
    raw = load_raw_destinations()
    return preprocess_destinations(raw)

try:
    df = get_destinations_data()
except Exception as e:
    st.error(f"Failed to load destination dataset: {e}")
    st.stop()

# 3. Retrieve Context from Session State (Profile & Conversation)
profile = st.session_state.get("traveler_profile", {})
conv_state = st.session_state.get("conversation_state", {})
conv_prefs = conv_state.get("preferences", {})

# Determine defaults from existing session states
all_destinations = sorted(df["destination"].unique().tolist())

# Default destination from conversation or fallback to first
default_dest = "Jaipur"
if conv_prefs.get("categories"):
    # Find matching destination for category
    matching_dest = df[df["category"].isin(conv_prefs["categories"])]
    if not matching_dest.empty:
        default_dest = matching_dest.iloc[0]["destination"]

dest_index = all_destinations.index(default_dest) if default_dest in all_destinations else 0

# Default duration (from conversation or fallback 3)
default_duration = int(conv_prefs.get("duration", 3)) if conv_prefs.get("duration") else 3
default_duration = max(1, min(default_duration, 10))

# Default travel style
style_options = ["Balanced", "Relaxed", "Adventurous", "Cultural", "Romantic", "Family", "Budget", "Luxury"]
default_style = conv_prefs.get("travel_style") or profile.get("persona_type", "Balanced")

# Normalize style option to matching list item
selected_style_idx = 0
for idx, opt in enumerate(style_options):
    if opt.lower() in str(default_style).lower():
        selected_style_idx = idx
        break

# Default user interests
default_interests = []
if conv_prefs.get("activities"):
    default_interests.extend(conv_prefs["activities"])
if profile.get("categories"):
    default_interests.extend(profile["categories"])

# 4. Interactive Configuration Controls
with st.container():
    st.subheader("Configure Your Trip Parameters")
    
    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        chosen_destination = st.selectbox(
            "Select Destination",
            options=all_destinations,
            index=dest_index,
            help="Choose any indexed Indian travel destination from our dataset.",
        )

    with col2:
        chosen_duration = st.number_input(
            "Trip Duration (Days)",
            min_value=1,
            max_value=10,
            value=default_duration,
            step=1,
            help="Supports 1 to 10 day multi-day itineraries.",
        )

    with col3:
        chosen_style = st.selectbox(
            "Travel Pace & Style",
            options=style_options,
            index=selected_style_idx,
            help="Calibrates the pacing and intensity of daily scheduled activities.",
        )

    col4, col5 = st.columns([2, 1])
    with col4:
        user_interests_input = st.text_input(
            "Specific Focus / Activities (Optional)",
            value=", ".join(default_interests[:3]) if default_interests else "Sightseeing, culture, nature",
            help="Keywords used to prioritize matching activities into daily slots.",
        )
    with col5:
        st.write("")
        st.write("")
        generate_clicked = st.button("🚀 Generate Itinerary", use_container_width=True, type="primary")

st.divider()

# 5. Itinerary Computation
if generate_clicked or "current_itinerary" not in st.session_state:
    parsed_interests = [i.strip() for i in user_interests_input.split(",") if i.strip()]
    itinerary_result = generate_itinerary(
        df=df,
        destination_name=chosen_destination,
        duration_days=chosen_duration,
        travel_style=chosen_style,
        user_interests=parsed_interests,
    )
    st.session_state["current_itinerary"] = itinerary_result

itinerary = st.session_state.get("current_itinerary")

if not itinerary or "error" in itinerary:
    st.error(itinerary.get("error", "Unable to generate itinerary. Please verify input settings."))
    st.stop()

# 6. Render Itinerary Overview
st.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 1.5rem 2rem; border-radius: 12px; color: #ffffff; margin-bottom: 1.5rem;">
        <span style="background: rgba(255, 255, 255, 0.2); padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: 700;">
            {itinerary['duration_days']}-DAY TRIP PLAN
        </span>
        <h2 style="color: #ffffff; margin: 0.4rem 0 0.2rem 0; font-size: 1.8rem;">
            {itinerary['destination']}, {itinerary.get('state', '')}
        </h2>
        <div style="font-size: 0.9rem; color: #93c5fd;">
            Category: <strong>{itinerary['category']}</strong> • 
            Pacing: <strong>{itinerary['travel_style']}</strong> • 
            Est. Base: <strong>{format_currency_inr(itinerary['estimated_cost'])}</strong> • 
            Best Season: <strong>{itinerary.get('best_season', 'All Year')}</strong>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 7. Render Day-by-Day Schedule Cards
for day_obj in itinerary.get("days", []):
    day_num = day_obj["day"]
    theme_title = day_obj.get("theme_focus", f"Day {day_num}")
    slots = day_obj["slots"]

    with st.expander(f"📅 **Day {day_num}: {theme_title}**", expanded=True):
        m_col, a_col, e_col = st.columns(3)

        # Morning slot
        with m_col:
            m_data = slots.get("Morning", {})
            st.markdown(
                f"""
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 10px; padding: 1rem; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #166534; text-transform: uppercase;">🌅 Morning</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.3rem 0;">{m_data.get('title', 'Morning Activity')}</div>
                    <div style="font-size: 0.85rem; color: #334155; line-height: 1.4;">{m_data.get('description', '')}</div>
                    <div style="font-size: 0.75rem; color: #15803d; font-weight: 600; margin-top: 0.5rem;">Pace: {m_data.get('pace', 'Standard')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Afternoon slot
        with a_col:
            a_data = slots.get("Afternoon", {})
            st.markdown(
                f"""
                <div style="background: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 1rem; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #92400e; text-transform: uppercase;">☀️ Afternoon</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.3rem 0;">{a_data.get('title', 'Afternoon Activity')}</div>
                    <div style="font-size: 0.85rem; color: #334155; line-height: 1.4;">{a_data.get('description', '')}</div>
                    <div style="font-size: 0.75rem; color: #b45309; font-weight: 600; margin-top: 0.5rem;">Pace: {a_data.get('pace', 'Moderate')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Evening slot
        with e_col:
            e_data = slots.get("Evening", {})
            st.markdown(
                f"""
                <div style="background: #f5f3ff; border: 1px solid #ddd6fe; border-radius: 10px; padding: 1rem; height: 100%;">
                    <div style="font-size: 0.8rem; font-weight: 800; color: #5b21b6; text-transform: uppercase;">🌆 Evening</div>
                    <div style="font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0.3rem 0;">{e_data.get('title', 'Evening Activity')}</div>
                    <div style="font-size: 0.85rem; color: #334155; line-height: 1.4;">{e_data.get('description', '')}</div>
                    <div style="font-size: 0.75rem; color: #6d28d9; font-weight: 600; margin-top: 0.5rem;">Pace: {e_data.get('pace', 'Leisure')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# Save Trip action hook
st.divider()
action_col1, action_col2 = st.columns([1, 1])
with action_col1:
    if st.button("💾 Save Itinerary to My Trips", use_container_width=True):
        from src.saved_trips import save_trip
        current_saved = st.session_state.get("saved_trips", [])
        updated_saved, ok, msg = save_trip(current_saved, itinerary, prevent_duplicates=True)
        st.session_state["saved_trips"] = updated_saved
        if ok:
            st.success(msg)
        else:
            st.info(msg)


with action_col2:
    st.info("💡 **Planning Tip:** Switch back to **2_AI_Travel_Assistant** to ask follow-up questions about this destination!")
