# AI-Powered Personalized Travel Intelligence & Trip Planning System

A modern, data-driven travel technology platform designed to assist travelers with intelligent destination discovery, personalized content-based recommendations, conversational guidance, smart day-by-day trip planning, budget optimization, and saved itinerary bookmark management.

> **Project Phase Status:** Phase 6 (Saved Trips & Itinerary Bookmark Management) Successfully Implemented & Verified.

---

## 1. Problem Statement
Travelers often struggle with fragmented tourism data, opaque budget estimations, and generic travel recommendations that do not match their personalized preferences, budget boundaries, or travel pace.

## 2. Project Objective
To engineer an end-to-end intelligent travel platform that:
1. Surfaces structured, high-integrity destination information across Indian states and travel themes.
2. Provides a **Content-Based Recommendation Engine** using TF-IDF and Cosine Similarity to rank destinations according to active traveler personas.
3. Provides an interactive **Conversational Travel Assistant** that parses natural-language prompts, tracks dialogue state across turns, asks clarification questions, and connects directly to the recommendation engine.
4. Provides a **Smart Day-by-Day Trip Planner** that creates realistic daily schedules (Morning, Afternoon, Evening) based on destination activities, duration, and pacing.
5. Provides a **Smart Travel Budget Intelligence & Optimizer** breaking down expenditures into 5 key categories (Accommodation, Food, Transportation, Activities, Miscellaneous), comparing against user targets, and generating actionable savings levers.
6. Provides a **Saved Trips & Itinerary Bookmark Manager** enabling travelers to bookmark generated trip plans, inspect schedules and cost breakdowns, compare trips side-by-side, and download plans as formatted JSON or plain-text documents.
7. Enables intuitive filtering across multi-dimensional criteria (budget, state, rating, category).

---

## 3. Architecture & Phase Scope

### Phase 1: Architecture Foundation
- **Clean Modular Codebase:** Separated data pipelines, reusable utilities, UI styling, automated tests, and multi-page routing.
- **Curated Starter Dataset:** A transparent 20-destination curated dataset across India covering Heritage, Nature, Beach, Adventure, and Spiritual themes.
- **Data Preprocessing & Ingestion:** Loading, type standardization, latitude/longitude parsing, and automatic budget categorization (`Budget`, `Moderate`, `Luxury`).
- **Interactive Explore Page:** Multi-attribute filtering (state, category, budget slider, rating) with card and tabular views.
- **Traveler Profile Module:** Configures travel personas, preferred pacing, categories, budget tiers, and seasons.

### Phase 2: Content-Based Recommendation Engine
- **`src/recommendation.py`:** Core recommendation module built with `scikit-learn`:
  - `build_destination_content_text()`: Synthesizes destination name, state, category, description, best season, activities, and budget tier.
  - `build_user_preference_text()`: Translates traveler persona preferences into a consolidated preference document.
  - `calculate_content_recommendations()`: Computes TF-IDF vectorization (unigrams + bigrams) and measures Cosine Similarity against all destination vectors.
  - Returns Top-N ranked destinations sorted by Cosine Similarity with percentage match indicators.
- **`pages/7_Recommendations.py`:** Interactive recommendations UI with Top 3/5/10 controls, keyword recalibration, and detailed scoring tables.

### Phase 3: Conversational Travel Assistant
- **`src/query_parser.py`:** Rule-based natural language parser:
  - Budget extraction (numeric, k-format like `15k`, INR/₹ currencies, preposition patterns like `under 15000`).
  - Duration extraction (`3 days`, `weekend`, `a week`, `4 nights`).
  - Travel theme extraction mapped to dataset categories (`Beach`, `Heritage`, `Nature`, `Adventure`, `Spiritual`).
  - Travel style/vibe recognition (`Relaxed`, `Adventurous`, `Cultural`, `Romantic`, `Family`, `Luxury`, `Budget`).
  - Season/month recognition (`Winter`, `Summer`, `Monsoon`, `Spring`).
  - Activity keyword extraction (`trekking`, `scuba diving`, `temple visits`, `tea tasting`, etc.).
- **`src/conversation_manager.py`:** Dialogue state and conversation controller:
  - Manages session messages and ongoing preference state.
  - Asks contextual follow-up questions when required details are missing.
  - Passes extracted parameters directly to `src.recommendation` without duplicate recommendation logic.
- **`pages/2_AI_Travel_Assistant.py`:** Streamlit chat interface with native components, context banner, and inline recommendation cards.

### Phase 4: Smart Day-by-Day Trip Planner
- **`src/itinerary.py`:** Deterministic day-by-day scheduling engine:
  - `parse_activities()`: Parses comma-separated activities from dataset.
  - `get_destination_activities()`: Safely retrieves destination details and activities.
  - `classify_activity_slot()`: Assigns activities to optimal time windows (Morning, Afternoon, Evening) using domain heuristics.
  - `generate_day_plan()`: Builds balanced 3-slot schedules with contextual fallbacks per theme.
  - `generate_itinerary()`: Distributes activities across multi-day durations (1–10 days), adapts pacing to travel styles, and prioritizes user interests.
- **`pages/3_Trip_Planner.py`:** Functional interactive planning dashboard with auto-filled defaults, morning/afternoon/evening timeline cards, and save hooks.

### Phase 5: Smart Travel Budget Intelligence & Optimizer
- **`src/budget.py`:** Deterministic financial projection and optimization engine:
  - `validate_budget()`: Validates numeric user budget targets.
  - `get_style_allocations()`: Style-adjusted percentage allocation across 5 categories (Accommodation, Food, Transportation, Activities, Miscellaneous), strictly totaling 100%.
  - `calculate_base_daily_cost()`: Anchors daily rate to destination `estimated_cost` and style intensity multipliers.
  - `estimate_expenses()`: Allocates expenses with exact integer balance.
  - `calculate_total_budget()`: Computes total projected cost and daily averages across 1–10 days.
  - `compare_with_user_budget()`: Calculates variance, surplus/deficit, and utilization percentages.
  - `generate_budget_suggestions()`: Proposes ranked savings levers (style downgrade, duration reduction, accommodation adjustments, activity reprioritization).
- **`pages/4_Budget_Planner.py`:** Upgraded interactive budgeting dashboard with KPI metrics, expense cards, distribution chart, and savings levers.

### Phase 6: Saved Trips & Itinerary Bookmark Management
- **`src/saved_trips.py`:** Saved trips management module:
  - `normalize_saved_trip()`: Normalizes saved itineraries and budget payloads into a unified, stable schema.
  - `is_duplicate_trip()` & `save_trip()`: Prevents accidental duplicate saves of identical destination, duration, and style configurations.
  - `delete_trip()` & `clear_saved_trips()`: Provides selective removal by trip ID/index or complete clearing.
  - `compare_trips()`: Produces a multi-trip comparison matrix across destination, duration, style, estimated cost, and theme.
  - `export_trip_json()`: Exports complete structured trip data as a JSON document.
  - `export_trip_text()`: Generates a human-readable, formatted text itinerary document with daily schedules and budget breakdown.
- **`pages/5_Saved_Trips.py`:** Comprehensive Saved Trips dashboard:
  - Friendly empty state with direct guidance to the Trip Planner.
  - Visual summary cards showing destination, duration, style, and cost.
  - Expandable itinerary detail viewer with individual daily slots.
  - Selective side-by-side trip comparison table.
  - Streamlit `st.download_button` hooks for JSON and TXT exports.

---

## 4. Technology Stack
- **Language:** Python 3.11+
- **Frontend / Application Framework:** Streamlit (v1.30+)
- **Data Manipulation:** Pandas
- **Machine Learning:** Scikit-learn (`TfidfVectorizer`, `cosine_similarity`)
- **Testing:** Custom test suites (`test_basic.py`, `test_recommendations.py`, `test_query_parser.py`, `test_conversation.py`, `test_itinerary.py`, `test_budget.py`, `test_saved_trips.py`, `verify_differentiation.py`)

---

## 5. Project Structure
```text
travel_intelligence/
│
├── app.py                         # Application landing page & featured overview
├── requirements.txt               # Streamlit, Pandas, Scikit-learn
├── README.md                      # Project documentation & setup guide
│
├── data/
│   ├── raw/
│   │   └── destinations.csv       # Curated development starter dataset
│   └── processed/
│       └── destinations_clean.csv # Cleaned & enriched dataset
│
├── pages/
│   ├── 1_Explore_Destinations.py  # Interactive search & filtering interface
│   ├── 2_AI_Travel_Assistant.py   # Phase 3 Conversational Travel Assistant
│   ├── 3_Trip_Planner.py          # Phase 4 Smart Day-by-Day Trip Planner
│   ├── 4_Budget_Planner.py        # Phase 5 Smart Travel Budget Optimizer
│   ├── 5_Saved_Trips.py           # Phase 6 Saved Trips & Itinerary Bookmarks
│   ├── 6_Profile.py               # Traveler style & preference configuration
│   └── 7_Recommendations.py       # Phase 2 ML Recommendation Engine UI
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Dataset discovery & loader
│   ├── preprocessing.py           # Cleans attributes & assigns budget tiers
│   ├── recommendation.py          # TF-IDF & Cosine Similarity ML Engine
│   ├── query_parser.py            # Natural language travel query parser
│   ├── conversation_manager.py    # Conversation state & dialogue management
│   ├── itinerary.py               # Day-by-day scheduling & activity allocation
│   ├── budget.py                  # Expense breakdown & budget optimization
│   ├── saved_trips.py             # Saved trips, comparison & export engine
│   ├── utils.py                   # Search & filter functions, currency helpers
│   └── ui_components.py           # CSS styling & placeholder components
│
├── assets/                        # Visual assets (static resources)
└── tests/
    ├── test_basic.py              # Phase 1 unit test verification
    ├── test_recommendations.py    # Regression & ML algorithm unit tests
    ├── test_query_parser.py       # Phase 3 query parser test suite
    ├── test_conversation.py       # Phase 3 conversation manager test suite
    ├── test_itinerary.py          # Phase 4 itinerary generator test suite
    ├── test_budget.py             # Phase 5 budget intelligence test suite
    ├── test_saved_trips.py        # Phase 6 saved trips & export test suite
    └── verify_differentiation.py  # Persona recommendation differentiation test
```

---

## 6. Dataset Information & Source
- **Dataset File:** `data/raw/destinations.csv`
- **Source Disclosure:** **Curated Starter Development Dataset** specifically prepared for UI and pipeline architecture verification.
- **Attributes Provided:**
  - `destination`: Name of the travel spot
  - `state`: State or Union Territory
  - `category`: Theme (`Heritage`, `Nature`, `Adventure`, `Beach`, `Spiritual`)
  - `description`: Overview description
  - `rating`: Representative tourist review rating (scale 1.0 - 5.0)
  - `estimated_cost`: Average estimated cost in INR (₹)
  - `best_season`: Optimal season for travel (`Winter`, `Summer`, `Monsoon`, `Spring`)
  - `activities`: Key travel activities
  - `location`: Geographic coordinates (`Latitude, Longitude`)
  - `budget_tier`: `Budget` (≤ ₹5k), `Moderate` (₹5k - ₹10k), `Luxury` (> ₹10k)

> *Data Integrity Note: No fabricated reviews or synthetic user behavior statistics are included.*

---

## 7. How to Install & Run

### Step 1: Navigate to the Project Directory
```powershell
cd C:\Users\HP\OneDrive\Desktop\AIML_Engineer\travel_intelligence
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Run the Automated Test Suites
```powershell
python tests/test_recommendations.py
python tests/test_query_parser.py
python tests/test_conversation.py
python tests/test_itinerary.py
python tests/test_budget.py
python tests/test_saved_trips.py
python tests/verify_differentiation.py
```

### Step 4: Launch the Streamlit Web Application
```powershell
streamlit run app.py
```

Once executed, open your browser at the displayed local URL (typically `http://localhost:8501`).

---

## 8. Current Limitations
- Saved trips are stored in `st.session_state` for the duration of the browser session; persistent external database backing (SQLite/PostgreSQL) can be added in a production deployment.
- The budget engine provides deterministic planning estimates based on curated destination data and configurable assumptions; it is not a live hotel/flight booking price system.
- The itinerary planner is a deterministic scheduling algorithm driven by dataset activities and theme heuristics; live transit routing APIs and dynamic map integrations are not included.
- Conversational assistant uses rule-based parsing and pattern extraction (no external LLM API keys needed).
- Curated development dataset currently contains 20 Indian destinations.
