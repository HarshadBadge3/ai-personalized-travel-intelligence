"""Smart Travel Budget Planner & Optimizer Page."""
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.budget import (
    validate_budget,
    calculate_total_budget,
    compare_with_user_budget,
    generate_budget_suggestions,
)
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Budget Planner | Travel Intelligence",
    page_icon="💰",
    layout="wide",
)

apply_custom_css()

# Header
st.title("💰 Smart Travel Budget Intelligence & Optimizer")
st.markdown(
    "Analyze granular trip expenditures across accommodation, dining, transit, and activities, compare with your target budget, and explore actionable cost-saving levers."
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

# 3. Retrieve Context from Session State (Profile, Conversation, Trip Planner)
profile = st.session_state.get("traveler_profile", {})
conv_state = st.session_state.get("conversation_state", {})
conv_prefs = conv_state.get("preferences", {})
trip_plan = st.session_state.get("current_itinerary", {})

# Determine defaults
all_destinations = sorted(df["destination"].unique().tolist())

# Destination default
default_dest = trip_plan.get("destination") or conv_prefs.get("destination") or "Jaipur"
if default_dest not in all_destinations:
    default_dest = all_destinations[0]
dest_idx = all_destinations.index(default_dest)

# Duration default
default_duration = trip_plan.get("duration_days") or conv_prefs.get("duration") or 3
default_duration = max(1, min(int(default_duration), 10))

# Style default
style_options = ["Balanced", "Relaxed", "Adventurous", "Cultural", "Romantic", "Family", "Budget", "Luxury"]
context_style = trip_plan.get("travel_style") or conv_prefs.get("travel_style") or profile.get("persona_type", "Balanced")

selected_style_idx = 0
for idx, opt in enumerate(style_options):
    if opt.lower() in str(context_style).lower():
        selected_style_idx = idx
        break

# Target budget default
default_budget = conv_prefs.get("budget") or 15000
default_budget = int(default_budget)

# 4. Input Section
with st.container():
    st.subheader("Configure Travel Budget Parameters")

    b_col1, b_col2, b_col3, b_col4 = st.columns([1.2, 1, 1, 1.2])

    with b_col1:
        chosen_destination = st.selectbox(
            "Destination",
            options=all_destinations,
            index=dest_idx,
            help="Destination whose cost anchor calibrates baseline projections.",
        )

    with b_col2:
        chosen_duration = st.number_input(
            "Duration (Days)",
            min_value=1,
            max_value=10,
            value=default_duration,
            step=1,
            help="Length of stay for expense projection.",
        )

    with b_col3:
        chosen_style = st.selectbox(
            "Travel Style",
            options=style_options,
            index=selected_style_idx,
            help="Adjusts expense distribution weights across categories.",
        )

    with b_col4:
        user_budget_input = st.number_input(
            "Target Budget (INR)",
            min_value=1000,
            max_value=500000,
            value=default_budget,
            step=500,
            help="Your planned total spending budget.",
        )

    calc_btn = st.button("📊 Calculate & Optimize Budget", use_container_width=True, type="primary")

st.divider()

# 5. Calculation
valid_user_budget = validate_budget(user_budget_input)

budget_calc = calculate_total_budget(
    df=df,
    destination_name=chosen_destination,
    duration_days=chosen_duration,
    travel_style=chosen_style,
)

comparison = compare_with_user_budget(
    estimated_total=budget_calc["total_estimated"],
    user_budget=valid_user_budget,
)

# Store in session state for cross-module accessibility
st.session_state["current_budget_plan"] = {
    "calculation": budget_calc,
    "comparison": comparison,
}

# 6. Budget Status & KPI Overview
st.subheader("Financial Projection & Variance")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        label="Total Estimated Cost",
        value=format_currency_inr(budget_calc["total_estimated"]),
        help="Deterministic planning projection based on destination and duration.",
    )

with kpi2:
    st.metric(
        label="Average Daily Cost",
        value=f"{format_currency_inr(budget_calc['daily_average'])} / day",
        help="Projected average cost per day.",
    )

with kpi3:
    st.metric(
        label="Your Target Budget",
        value=format_currency_inr(valid_user_budget) if valid_user_budget else "Not Set",
    )

with kpi4:
    if comparison["status"] == "Within Budget":
        st.metric(
            label="Budget Surplus",
            value=f"+ {format_currency_inr(comparison['difference'])}",
            delta="Within Budget",
            delta_color="normal",
        )
    elif comparison["status"] == "Budget Fully Utilized":
        st.metric(
            label="Budget Balance",
            value="Exact Match",
            delta="100% Utilized",
            delta_color="off",
        )
    elif comparison["status"] == "Over Budget":
        st.metric(
            label="Projected Deficit",
            value=f"- {format_currency_inr(comparison['difference'])}",
            delta="Over Budget",
            delta_color="inverse",
        )
    else:
        st.metric(label="Status", value="No Target Set")

# Status Banner
if comparison["status"] == "Within Budget":
    st.success(
        f"✅ **Great news!** Your projected trip expense of **{format_currency_inr(budget_calc['total_estimated'])}** is within your budget of **{format_currency_inr(valid_user_budget)}** (Utilization: {comparison['utilization_pct']}%)."
    )
elif comparison["status"] == "Over Budget":
    st.warning(
        f"⚠️ **Attention:** Your projected trip expense of **{format_currency_inr(budget_calc['total_estimated'])}** exceeds your budget by **{format_currency_inr(comparison['difference'])}** (Utilization: {comparison['utilization_pct']}%). Review the optimization levers below!"
    )

st.divider()

# 7. Expense Category Breakdown & Native Visualization
st.subheader("Granular Expense Breakdown")

col_exp_cards, col_exp_chart = st.columns([1.2, 0.8])

expenses = budget_calc["expenses"]
categories_order = ["Accommodation", "Food", "Transportation", "Activities", "Miscellaneous"]
category_icons = {
    "Accommodation": "🏨",
    "Food": "🍽️",
    "Transportation": "🚕",
    "Activities": "🎟️",
    "Miscellaneous": "🛍️",
}

with col_exp_cards:
    for cat in categories_order:
        amt = expenses.get(cat, 0)
        pct = round((amt / budget_calc["total_estimated"]) * 100, 1) if budget_calc["total_estimated"] > 0 else 0
        icon = category_icons.get(cat, "💳")

        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.8rem 1.1rem; margin-bottom: 0.6rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.04);">
                <div>
                    <span style="font-size: 1.1rem; margin-right: 0.5rem;">{icon}</span>
                    <strong style="color: #0f172a; font-size: 0.95rem;">{cat}</strong>
                    <span style="color: #64748b; font-size: 0.8rem; margin-left: 0.4rem;">({pct}%)</span>
                </div>
                <div style="font-weight: 700; color: #1e3a8a; font-size: 1rem;">
                    {format_currency_inr(amt)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_exp_chart:
    st.caption("📈 **Expense Distribution by Category**")
    chart_df = pd.DataFrame({
        "Category": [f"{category_icons.get(c, '')} {c}" for c in categories_order],
        "Amount (INR)": [expenses.get(c, 0) for c in categories_order],
    }).set_index("Category")

    st.bar_chart(chart_df, use_container_width=True)

st.divider()

# 8. Budget Optimization Suggestions
st.subheader("💡 Budget Optimization & Cost-Saving Levers")
suggestions = generate_budget_suggestions(
    df=df,
    destination_name=chosen_destination,
    duration_days=chosen_duration,
    travel_style=chosen_style,
    user_budget=valid_user_budget,
    current_estimated_total=budget_calc["total_estimated"],
)

if not suggestions:
    st.info("Your budget is well-balanced. No adjustments necessary!")
else:
    s_cols = st.columns(min(len(suggestions), 3))
    for idx, s in enumerate(suggestions[:3]):
        with s_cols[idx]:
            savings_label = f"Save ~{format_currency_inr(s['estimated_savings'])}" if s['estimated_savings'] > 0 else "Surplus Tip"
            badge_color = "#059669" if s['estimated_savings'] > 0 else "#2563eb"
            st.markdown(
                f"""
                <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 1.1rem; height: 100%;">
                    <div style="display: inline-block; background: {badge_color}; color: #ffffff; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-bottom: 0.5rem;">
                        {savings_label}
                    </div>
                    <div style="font-size: 1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.4rem;">{s['title']}</div>
                    <div style="font-size: 0.85rem; color: #475569; line-height: 1.45; margin-bottom: 0.6rem;">{s['description']}</div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #334155;">New Projected Total: <strong>{format_currency_inr(s['new_total'])}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.divider()
st.info(
    "📌 **Methodology Note:** The budget intelligence engine generates deterministic planning estimates based on curated destination baseline data and travel-style assumptions. It is designed for realistic trip budgeting rather than live hotel/flight booking prices."
)
