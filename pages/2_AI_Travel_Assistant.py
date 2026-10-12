"""AI Travel Assistant - Interactive conversational planning assistant."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.conversation_manager import init_conversation_state, process_user_turn
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="AI Travel Assistant | Travel Intelligence",
    page_icon="🤖",
    layout="wide",
)

apply_custom_css()

# Header
st.title("🤖 Conversational AI Travel Assistant")
st.markdown(
    "Chat naturally with the assistant to discover destinations matching your travel style, budget, and duration constraints."
)

# 2. Load Dataset
@st.cache_data
def get_destinations_data():
    raw = load_raw_destinations()
    return preprocess_destinations(raw)

try:
    df = get_destinations_data()
except Exception as e:
    st.error(f"Failed to load destinations: {e}")
    st.stop()

# 3. Conversation Session State Initialization
stored_profile = st.session_state.get("traveler_profile")

if "conversation_state" not in st.session_state:
    st.session_state["conversation_state"] = init_conversation_state(stored_profile)

conv_state = st.session_state["conversation_state"]

# 4. Top Panel: Preference Status & Reset
col_meta1, col_meta2 = st.columns([1.5, 0.5])
with col_meta1:
    prefs = conv_state.get("preferences", {})
    p_tags = []
    if prefs.get("categories"):
        p_tags.append(f"🏷️ Themes: **{', '.join(prefs['categories'])}**")
    if prefs.get("budget"):
        p_tags.append(f"💰 Budget: **{format_currency_inr(prefs['budget'])}**")
    if prefs.get("duration"):
        p_tags.append(f"⏱️ Duration: **{prefs['duration']} Days**")
    if prefs.get("travel_style"):
        p_tags.append(f"🌟 Style: **{prefs['travel_style']}**")
    if prefs.get("season"):
        p_tags.append(f"☀️ Season: **{prefs['season']}**")
    if prefs.get("activities"):
        p_tags.append(f"🎯 Activities: **{', '.join(prefs['activities'][:2])}**")

    if p_tags:
        st.markdown(f"**Current Conversation Context:** {' • '.join(p_tags)}")
    else:
        st.caption("No preferences established yet. Begin chatting below!")

with col_meta2:
    if st.button("🔄 Reset Conversation", use_container_width=True):
        st.session_state["conversation_state"] = init_conversation_state(stored_profile)
        st.rerun()

st.divider()

# 5. Render Chat Dialogue History
for msg in conv_state["messages"]:
    role = msg["role"]
    content = msg["message"]
    recs = msg.get("recommendations")

    with st.chat_message(role):
        st.markdown(content)

        # If this turn produced recommendations from the Phase 2 engine, render cards
        if recs is not None and not recs.empty:
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            card_cols = st.columns(len(recs))
            for idx, (_, row) in enumerate(recs.iterrows()):
                sim_pct = row.get("match_score_pct", 0.0)
                with card_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="dest-card">
                            <div class="dest-header">
                                <span class="dest-title">#{idx + 1} {row['destination']}</span>
                                <span class="dest-badge">{row['category']}</span>
                            </div>
                            <div class="dest-meta">📍 {row['state']} • ☀️ {row['best_season']}</div>
                            <div class="dest-desc">{row['description']}</div>
                            <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.5rem;">
                                <strong>Activities:</strong> {row['activities']}
                            </div>
                            <div style="background: #f8fafc; border-radius: 6px; padding: 0.35rem 0.5rem; margin-bottom: 0.5rem; border: 1px dashed #cbd5e1;">
                                <span style="font-size: 0.75rem; font-weight: 700; color: #1e3a8a;">
                                    🤖 Content Match: {sim_pct}%
                                </span>
                            </div>
                            <div class="dest-footer">
                                <span class="dest-cost">Est. {format_currency_inr(row['estimated_cost'])}</span>
                                <span class="dest-rating">⭐ {row['rating']} / 5.0</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            st.info("💡 Ready to generate a day-by-day itinerary? Head over to **3_Trip_Planner** in the sidebar to schedule your trip!")


# 6. Chat Input Handler
user_prompt = st.chat_input("Ask for travel recommendations (e.g., 'Plan a 3-day beach trip under 15k')...")

if user_prompt:
    # Process turn through conversation manager
    updated_state = process_user_turn(user_prompt, conv_state, df)
    st.session_state["conversation_state"] = updated_state
    st.rerun()
