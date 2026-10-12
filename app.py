"""Home Page - AI-Powered Personalized Travel Intelligence & Trip Planning System."""
import sys
from pathlib import Path
import streamlit as st

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_raw_destinations
from src.preprocessing import preprocess_destinations
from src.ui_components import apply_custom_css
from src.utils import format_currency_inr

# 1. Page Configuration
st.set_page_config(
    page_title="Travel Intelligence | AI Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Apply Custom Modern Styling
apply_custom_css()

# 3. Sidebar Branding & Info
with st.sidebar:
    st.markdown("### 🧭 Travel Intelligence")
    st.caption("Phase 6: Saved Trips Active")
    st.divider()
    st.markdown("**Project State:**")
    st.markdown("✅ Core Modular Structure")
    st.markdown("✅ Curated Destination Dataset")
    st.markdown("✅ Interactive Exploration Engine")
    st.markdown("✅ Content-Based Recommendations (Phase 2)")
    st.markdown("✅ Conversational Assistant (Phase 3)")
    st.markdown("✅ Smart Day-by-Day Trip Planner (Phase 4)")
    st.markdown("✅ Travel Budget Optimizer (Phase 5)")
    st.markdown("✅ Saved Trips & Bookmarks (Phase 6)")
    st.divider()
    st.caption("Final-Year Travel Tech Project")

# 4. Hero Section
st.markdown(
    """
    <div class="hero-banner">
        <span class="hero-badge">PHASE 6 • SAVED TRIPS & BOOKMARK MANAGEMENT ACTIVE</span>
        <div class="hero-title">AI-Powered Personalized Travel Intelligence & Trip Planning System</div>
        <div class="hero-subtitle">
            An intelligent travel tech platform designed to discover destinations, plan personalized itineraries, 
            and optimize travel budgets with data-driven precision.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 5. Core Platform Capabilities Grid
st.subheader("Explore Platform Modules")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Explore Destinations</div>
            <div class="feature-desc">
                Browse verified Indian travel spots with multi-attribute filtering by state, category, budget, and visitor ratings.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Travel Assistant</div>
            <div class="feature-desc">
                Conversational assistant for travel advice, custom itineraries, and local nuances (scheduled for Phase 2).
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Smart Trip Planner</div>
            <div class="feature-desc">
                Automated day-by-day scheduling based on travel pacing, interests, and geographical proximity.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)
with col4:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">💰</div>
            <div class="feature-title">Budget Optimizer</div>
            <div class="feature-desc">
                Breakdown travel expenditures across lodging, dining, transit, and activities with cost constraints.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔖</div>
            <div class="feature-title">Saved Trips & Bookmarks</div>
            <div class="feature-desc">
                Store generated itineraries, track bucket lists, and review trip summaries offline.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col6:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">👤</div>
            <div class="feature-title">User Traveler Profile</div>
            <div class="feature-desc">
                Configure traveler personas (solo, family, backpacker, luxury) to calibrate future AI recommendations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# 6. Destination Highlight Section (Driven by Dataset)
st.subheader("Featured Destinations Snapshot")

try:
    raw_df = load_raw_destinations()
    df = preprocess_destinations(raw_df)

    # Key Statistics Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Indexed Destinations", len(df))
    m2.metric("Covered States / UTs", df["state"].nunique())
    m3.metric("Travel Themes", df["category"].nunique())
    m4.metric("Avg Estimated Cost", format_currency_inr(df["estimated_cost"].mean()))

    # Top Rated Quick Preview
    top_destinations = df.sort_values(by="rating", ascending=False).head(3)
    
    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("##### Highest Rated Highlights")
    preview_cols = st.columns(3)

    for idx, (_, row) in enumerate(top_destinations.iterrows()):
        with preview_cols[idx]:
            st.markdown(
                f"""
                <div class="dest-card">
                    <div class="dest-header">
                        <span class="dest-title">{row['destination']}</span>
                        <span class="dest-badge">{row['category']}</span>
                    </div>
                    <div class="dest-meta">📍 {row['state']} • ☀️ {row['best_season']}</div>
                    <div class="dest-desc">{row['description']}</div>
                    <div class="dest-footer">
                        <span class="dest-cost">{format_currency_inr(row['estimated_cost'])} / trip</span>
                        <span class="dest-rating">⭐ {row['rating']} / 5.0</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info("👉 Use the **Explore Destinations** tab in the sidebar to search, filter by state/budget, and view full records.")

except Exception as e:
    st.error(f"Could not load destination preview: {e}")
