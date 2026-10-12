"""Explore Destinations Page - Interactive filtering and searching of travel spots."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.ui_components import apply_custom_css
from src.utils import filter_destinations, format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Explore Destinations | Travel Intelligence",
    page_icon="🔍",
    layout="wide",
)

apply_custom_css()

# Header
st.title("🔍 Explore Destinations")
st.markdown("Search, filter, and inspect curated Indian tourist destinations across categories and budget segments.")

# 2. Data Loading & Preprocessing
@st.cache_data
def get_destinations_data():
    raw = load_raw_destinations()
    return preprocess_destinations(raw)

try:
    df = get_destinations_data()
except Exception as e:
    st.error(f"Failed to load destination dataset: {e}")
    st.stop()

# 3. Filter Controls
with st.expander("🎯 Filter Options & Search Bar", expanded=True):
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1, 1, 1])

    with f_col1:
        search_query = st.text_input(
            "Search Destination or Activity",
            placeholder="e.g. Jaipur, rafting, tea, beach",
            help="Filters by destination name, description, or activities",
        )

    with f_col2:
        states = ["All"] + sorted(df["state"].unique().tolist())
        selected_state = st.selectbox("State / Territory", states)

    with f_col3:
        categories = ["All"] + sorted(df["category"].unique().tolist())
        selected_category = st.selectbox("Theme / Category", categories)

    with f_col4:
        min_cost = int(df["estimated_cost"].min())
        max_cost_limit = int(df["estimated_cost"].max())
        max_budget = st.slider(
            "Max Budget (INR)",
            min_value=min_cost,
            max_value=max_cost_limit,
            value=max_cost_limit,
            step=500,
        )

    f_col5, f_col6 = st.columns([1, 3])
    with f_col5:
        min_rating = st.slider("Minimum Rating", min_value=4.0, max_value=5.0, value=4.0, step=0.1)
    with f_col6:
        st.write("")
        st.write("")
        view_mode = st.radio("Display Format", ["Card View", "Table View"], horizontal=True)

# 4. Filter Application
filtered_df = filter_destinations(
    df,
    search_query=search_query,
    selected_state=selected_state,
    selected_category=selected_category,
    max_budget=max_budget,
    min_rating=min_rating,
)

# 5. Results Section
st.markdown(f"**Showing {len(filtered_df)} of {len(df)} destinations**")
st.divider()

if filtered_df.empty:
    st.warning("No destinations match your selected filters. Try broadening your budget or clearing keywords.")
else:
    if view_mode == "Card View":
        # 3 columns card grid
        cols = st.columns(3)
        for idx, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[idx % 3]:
                st.markdown(
                    f"""
                    <div class="dest-card">
                        <div class="dest-header">
                            <span class="dest-title">{row['destination']}</span>
                            <span class="dest-badge">{row['category']}</span>
                        </div>
                        <div class="dest-meta">📍 {row['state']} • ☀️ {row['best_season']} • 🏷️ {row.get('budget_tier', 'Standard')}</div>
                        <div class="dest-desc">{row['description']}</div>
                        <div style="font-size: 0.8rem; color: #475569; margin-bottom: 0.5rem;">
                            <strong>Activities:</strong> {row['activities']}
                        </div>
                        <div class="dest-footer">
                            <span class="dest-cost">Est. {format_currency_inr(row['estimated_cost'])}</span>
                            <span class="dest-rating">⭐ {row['rating']} / 5.0</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        # Structured tabular representation
        display_cols = [
            "destination",
            "state",
            "category",
            "rating",
            "estimated_cost",
            "budget_tier",
            "best_season",
            "activities",
        ]
        formatted_table = filtered_df[display_cols].copy()
        formatted_table["estimated_cost"] = formatted_table["estimated_cost"].apply(format_currency_inr)
        st.dataframe(
            formatted_table,
            column_config={
                "destination": "Destination",
                "state": "State",
                "category": "Category",
                "rating": "Rating (⭐)",
                "estimated_cost": "Estimated Cost",
                "budget_tier": "Budget Tier",
                "best_season": "Best Season",
                "activities": "Activities",
            },
            hide_index=True,
            use_container_width=True,
        )

# Direct CTA to Personalized Recommendations
st.divider()
st.info(
    "💡 **Looking for AI-curated suggestions?** Visit **7_Recommendations** in the sidebar to get rankings customized to your profile and preferred travel style."
)
