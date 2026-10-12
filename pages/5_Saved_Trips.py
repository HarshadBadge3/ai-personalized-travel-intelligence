"""Saved Trips & Itinerary Bookmark Management Page."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.saved_trips import (
    get_saved_trips,
    delete_trip,
    clear_saved_trips,
    compare_trips,
    export_trip_json,
    export_trip_text,
)
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Saved Trips | Travel Intelligence",
    page_icon="🔖",
    layout="wide",
)

apply_custom_css()

# Header
st.title("🔖 Saved Trips & Itinerary Bookmarks")
st.markdown(
    "Review, inspect, compare, and export your saved multi-day itineraries and bookmarked travel plans."
)

# 2. Retrieve Saved Trips from Session State
if "saved_trips" not in st.session_state:
    st.session_state["saved_trips"] = []

saved_trips = get_saved_trips(st.session_state["saved_trips"])

# 3. Top Action Bar: Count, Clear All
top_c1, top_c2 = st.columns([1.5, 0.5])
with top_c1:
    st.markdown(f"### 🧳 Bookmarked Itineraries ({len(saved_trips)})")
with top_c2:
    if saved_trips:
        if st.button("🗑️ Clear All Trips", use_container_width=True, type="secondary"):
            st.session_state["saved_trips"] = clear_saved_trips()
            st.rerun()

st.divider()

# 4. Handle Empty State
if not saved_trips:
    st.info("ℹ️ **No saved trips yet.** You have not bookmarked any travel plans in this session.")
    st.markdown(
        """
        ### How to get started:
        1. Open **3_Trip_Planner** from the sidebar.
        2. Pick your destination, trip duration, and travel style.
        3. Click **Generate Itinerary** and then **Save Itinerary to My Trips**.
        4. Return here to review, compare, or export your saved travel plans!
        """
    )
    st.stop()

# 5. Saved Trips List View
selected_for_comparison = []

for idx, trip in enumerate(saved_trips):
    t_id = trip["id"]
    dest = trip["destination"]
    days_cnt = trip["duration_days"]
    style = trip["travel_style"]
    cost = trip["estimated_cost"]
    rating = trip.get("rating", 4.5)
    season = trip.get("best_season", "All Year")
    saved_time = trip.get("saved_at", "")

    with st.container():
        card_col, act_col = st.columns([1.6, 0.4])

        with card_col:
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 12px; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="color: #0f172a; margin: 0; font-size: 1.3rem;">📍 {dest}, {trip.get('state', '')}</h3>
                        <span style="background: #e0f2fe; color: #0369a1; padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.8rem;">
                            {trip.get('category', 'Theme')}
                        </span>
                    </div>
                    <div style="font-size: 0.88rem; color: #475569; margin: 0.4rem 0;">
                        ⏱️ <strong>{days_cnt} Days</strong> • 🌟 Style: <strong>{style}</strong> • ☀️ Season: <strong>{season}</strong> • ⭐ {rating} / 5.0
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #059669; margin-top: 0.4rem;">
                        Est. Trip Cost: {format_currency_inr(cost)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with act_col:
            st.write("")
            # Delete button
            if st.button("🗑️ Delete", key=f"del_{t_id}_{idx}", use_container_width=True):
                updated, _ = delete_trip(st.session_state["saved_trips"], t_id)
                st.session_state["saved_trips"] = updated
                st.rerun()

            # Compare checkbox
            is_comp = st.checkbox("Select to Compare", key=f"comp_{t_id}_{idx}")
            if is_comp:
                selected_for_comparison.append(trip)

        # Expandable Detailed View
        with st.expander(f"📋 View Full {days_cnt}-Day Itinerary Details ({dest})", expanded=False):
            exp_col1, exp_col2 = st.columns([1, 1])
            with exp_col1:
                json_data = export_trip_json(trip)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"{dest.lower()}_{days_cnt}d_itinerary.json",
                    mime="application/json",
                    key=f"dl_json_{t_id}_{idx}",
                    use_container_width=True,
                )
            with exp_col2:
                text_doc = export_trip_text(trip)
                st.download_button(
                    label="📄 Download Formatted Text",
                    data=text_doc,
                    file_name=f"{dest.lower()}_{days_cnt}d_itinerary.txt",
                    mime="text/plain",
                    key=f"dl_txt_{t_id}_{idx}",
                    use_container_width=True,
                )

            # Daily breakdown display
            days_list = trip.get("days", [])
            if not days_list:
                st.caption("No daily activity breakdown stored for this trip.")
            else:
                st.markdown("#### Day-by-Day Schedule:")
                for d_obj in days_list:
                    d_num = d_obj.get("day", 1)
                    d_theme = d_obj.get("theme_focus", f"Day {d_num}")
                    slots = d_obj.get("slots", {})

                    st.markdown(f"**📅 {d_theme}**")
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        m = slots.get("Morning", {})
                        st.markdown(f"- 🌅 **Morning:** {m.get('title', 'N/A')}\n  *{m.get('description', '')}*")
                    with sc2:
                        a = slots.get("Afternoon", {})
                        st.markdown(f"- ☀️ **Afternoon:** {a.get('title', 'N/A')}\n  *{a.get('description', '')}*")
                    with sc3:
                        e = slots.get("Evening", {})
                        st.markdown(f"- 🌆 **Evening:** {e.get('title', 'N/A')}\n  *{e.get('description', '')}*")
                    st.divider()

            # Budget breakdown if present
            if trip.get("budget"):
                b_info = trip["budget"].get("expenses", {})
                if b_info:
                    st.markdown("#### Estimated Budget Breakdown:")
                    b_cols = st.columns(len(b_info))
                    for b_idx, (b_cat, b_amt) in enumerate(b_info.items()):
                        with b_cols[b_idx]:
                            st.metric(b_cat, format_currency_inr(b_amt))

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)

st.divider()

# 6. Side-by-Side Trip Comparison Section
st.subheader("⚖️ Side-by-Side Trip Comparison")

if len(selected_for_comparison) >= 2:
    st.markdown(f"Comparing **{len(selected_for_comparison)}** selected trips:")
    comp_df = compare_trips(selected_for_comparison)
    st.dataframe(comp_df, hide_index=True, use_container_width=True)
elif len(selected_for_comparison) == 1:
    st.info("ℹ️ Select at least one more trip using the **'Select to Compare'** checkboxes above to view a comparison table.")
else:
    st.caption("Select two or more trips above to activate side-by-side comparison.")
