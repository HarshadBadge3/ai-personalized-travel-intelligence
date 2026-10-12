"""Recommendations Page - Content-Based Travel Recommendation Engine."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.recommendation import (
    build_user_preference_text,
    calculate_content_recommendations,
)
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Personalized Recommendations | Travel Intelligence",
    page_icon="🎯",
    layout="wide",
)

apply_custom_css()

# Header
st.title("🎯 Personalized Destination Recommendations")
st.markdown(
    "Discover destinations tailored to your travel persona and preferences using our **TF-IDF & Cosine Similarity** content-based recommendation model."
)

# 2. Load Data
@st.cache_data
def get_destinations_data():
    raw = load_raw_destinations()
    return preprocess_destinations(raw)

try:
    df = get_destinations_data()
except Exception as e:
    st.error(f"Failed to load destination dataset: {e}")
    st.stop()

# 3. Retrieve User Profile from Session State
profile = st.session_state.get("traveler_profile")

# Top controls and profile summary
col_ctrl1, col_ctrl2 = st.columns([1.3, 0.7])

with col_ctrl1:
    st.markdown("### 📋 Active Traveler Persona")
    if profile:
        st.markdown(
            f"""
            - **Traveler:** `{profile.get('name', 'Explorer')}`
            - **Style:** `{profile.get('persona_type', 'Not specified')}`
            - **Favorite Categories:** `{', '.join(profile.get('categories', [])) if profile.get('categories') else 'None'}`
            - **Budget Preference:** `{profile.get('budget_tier', 'Not specified')}`
            - **Pacing:** `{profile.get('pace', 'Not specified')}`
            """
        )
    else:
        st.info("ℹ️ No profile saved yet in this session. Default travel preferences can be used or customized below.")

with col_ctrl2:
    st.markdown("### ⚙️ Recommendation Settings")
    top_n = st.selectbox("Number of Recommendations", options=[3, 5, 10], index=1)
    extra_keywords = st.text_input(
        "Refine with Extra Interests",
        placeholder="e.g. trekking, temples, beach, fort",
        help="Appends search keywords to your preference vector for real-time recalibration.",
    )

st.divider()

# 4. Handle Empty Preferences Safely
user_pref_text = build_user_preference_text(profile)
if not user_pref_text and not extra_keywords.strip():
    st.warning("⚠️ No travel preferences detected. Please configure your persona on the **Profile** page or enter keywords above.")
    st.markdown("👉 Go to **6_Profile** in the sidebar to configure your travel preferences.")
    st.stop()

# 5. Model Computation
recommendations = calculate_content_recommendations(
    df,
    profile=profile,
    user_query=extra_keywords,
    top_n=top_n,
)

if recommendations.empty:
    st.info("No matching destinations found for the specified criteria. Try expanding your categories or keywords.")
    st.stop()

# 6. Display Recommendations
st.subheader(f"Top {len(recommendations)} Personalized Matches")
st.caption(
    "💡 **Model Explanation:** Destinations are ranked by Cosine Similarity comparing your preference vector against curated destination content tokens."
)

rec_cols = st.columns(3)
for idx, (_, row) in enumerate(recommendations.iterrows()):
    sim_pct = row.get("match_score_pct", 0.0)
    col = rec_cols[idx % 3]
    with col:
        st.markdown(
            f"""
            <div class="dest-card">
                <div class="dest-header">
                    <span class="dest-title">#{idx + 1} {row['destination']}</span>
                    <span class="dest-badge">{row['category']}</span>
                </div>
                <div class="dest-meta">📍 {row['state']} • ☀️ {row['best_season']} • 🏷️ {row.get('budget_tier', 'Standard')}</div>
                <div class="dest-desc">{row['description']}</div>
                <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.5rem;">
                    <strong>Activities:</strong> {row['activities']}
                </div>
                <div style="background: #f8fafc; border-radius: 8px; padding: 0.4rem 0.6rem; margin-bottom: 0.6rem; border: 1px dashed #cbd5e1;">
                    <span style="font-size: 0.78rem; font-weight: 700; color: #1e3a8a;">
                        🤖 Content Match Score: {sim_pct}%
                    </span>
                    <span style="font-size: 0.72rem; color: #64748b;"> (Cosine: {row['similarity_score']})</span>
                </div>
                <div class="dest-footer">
                    <span class="dest-cost">Est. {format_currency_inr(row['estimated_cost'])}</span>
                    <span class="dest-rating">⭐ {row['rating']} / 5.0</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Tabular view expander
with st.expander("📊 View Detailed Model Scoring Table"):
    table_view = recommendations[
        [
            "destination",
            "state",
            "category",
            "rating",
            "estimated_cost",
            "budget_tier",
            "similarity_score",
            "match_score_pct",
        ]
    ].copy()
    table_view["estimated_cost"] = table_view["estimated_cost"].apply(format_currency_inr)
    st.dataframe(
        table_view,
        column_config={
            "destination": "Destination",
            "state": "State",
            "category": "Theme",
            "rating": "Rating (⭐)",
            "estimated_cost": "Est. Cost",
            "budget_tier": "Budget Tier",
            "similarity_score": "Cosine Similarity",
            "match_score_pct": "Match Percentage (%)",
        },
        hide_index=True,
        use_container_width=True,
    )
