"""Content-Based Destination Recommendation Engine using TF-IDF and Cosine Similarity."""
from typing import Any
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def build_destination_content_text(df: pd.DataFrame) -> pd.Series:
    """Combine meaningful descriptive features of destinations into a single text representation.

    Features combined:
    - destination name
    - state
    - category
    - description
    - best_season
    - activities
    - budget_tier

    Args:
        df: Destination DataFrame.

    Returns:
        pd.Series: Text strings representing each destination.
    """
    if df.empty:
        return pd.Series(dtype=str)

    content_texts = []
    for _, row in df.iterrows():
        parts = []

        # Destination name
        dest = str(row.get("destination", "")).strip()
        if dest and dest != "nan":
            parts.append(dest)

        # State
        state = str(row.get("state", "")).strip()
        if state and state != "nan":
            parts.append(state)

        # Category
        cat = str(row.get("category", "")).strip()
        if cat and cat != "nan":
            parts.append(f"{cat} theme")

        # Description
        desc = str(row.get("description", "")).strip()
        if desc and desc != "nan":
            parts.append(desc)

        # Best season
        season = str(row.get("best_season", "")).strip()
        if season and season != "nan":
            parts.append(f"best in {season}")

        # Activities
        acts = str(row.get("activities", "")).strip()
        if acts and acts != "nan":
            parts.append(f"activities include {acts}")

        # Budget Tier
        b_tier = str(row.get("budget_tier", "")).strip()
        if b_tier and b_tier != "nan":
            parts.append(f"{b_tier} budget")

        combined = " ".join(parts).lower()
        content_texts.append(combined)

    return pd.Series(content_texts, index=df.index)


def build_user_preference_text(profile: dict[str, Any] | None) -> str:
    """Build a search/preference text string from user profile attributes.

    Supported profile keys:
    - categories (list of strings or string)
    - persona_type (string)
    - budget_tier (string)
    - pace (string)
    - preferred_season (string, optional)
    - preferred_activities (string or list, optional)

    Args:
        profile: Dictionary with user preference keys.

    Returns:
        str: Consolidated preference string.
    """
    if not profile or not isinstance(profile, dict):
        return ""

    tokens = []

    # Categories
    cats = profile.get("categories")
    if cats:
        if isinstance(cats, list):
            tokens.extend([str(c).strip() for c in cats if str(c).strip()])
        elif isinstance(cats, str) and cats.strip():
            tokens.append(cats.strip())

    # Persona type
    persona = profile.get("persona_type")
    if persona and isinstance(persona, str) and persona.strip():
        tokens.append(persona.strip())

    # Budget tier (normalize e.g. 'Budget (Under ₹5,000/trip)' -> 'Budget')
    budget_raw = profile.get("budget_tier")
    if budget_raw and isinstance(budget_raw, str):
        budget_clean = budget_raw.split("(")[0].strip()
        if budget_clean:
            tokens.append(f"{budget_clean} budget")

    # Season
    season = profile.get("preferred_season")
    if season and isinstance(season, str) and season.strip():
        tokens.append(f"{season.strip()} season")

    # Activities or specific interests
    acts = profile.get("preferred_activities")
    if acts:
        if isinstance(acts, list):
            tokens.extend([str(a).strip() for a in acts if str(a).strip()])
        elif isinstance(acts, str) and acts.strip():
            tokens.append(acts.strip())

    return " ".join(tokens).lower().strip()


def calculate_content_recommendations(
    df: pd.DataFrame,
    profile: dict[str, Any] | None = None,
    user_query: str = "",
    top_n: int = 5,
) -> pd.DataFrame:
    """Compute content-based recommendations using TF-IDF and Cosine Similarity.

    Args:
        df: Processed destinations DataFrame.
        profile: Optional user profile dictionary from session state.
        user_query: Optional free-form search or interest keywords.
        top_n: Maximum number of ranked recommendations to return.

    Returns:
        pd.DataFrame: Top-N destinations sorted by similarity_score descending,
                      including a 'match_score_pct' formatted percentage.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Combine profile text and optional extra query text
    pref_text_parts = []
    profile_text = build_user_preference_text(profile)
    if profile_text:
        pref_text_parts.append(profile_text)

    if user_query and user_query.strip():
        pref_text_parts.append(user_query.strip().lower())

    combined_user_text = " ".join(pref_text_parts).strip()

    # If no preferences provided at all, return empty DataFrame to prompt user
    if not combined_user_text:
        return pd.DataFrame()

    # Build corpus: destination content strings
    destination_docs = build_destination_content_text(df).tolist()

    # Initialize TF-IDF Vectorizer
    # stop_words='english' removes common non-informative words
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))

    try:
        tfidf_matrix = vectorizer.fit_transform(destination_docs)
        user_vector = vectorizer.transform([combined_user_text])
    except ValueError:
        # Handles edge cases such as empty vocabulary
        return pd.DataFrame()

    # Compute Cosine Similarity between user vector and all destinations
    similarity_scores = cosine_similarity(user_vector, tfidf_matrix).flatten()

    # Construct result DataFrame
    results_df = df.copy()
    results_df["similarity_score"] = similarity_scores.round(4)
    results_df["match_score_pct"] = (similarity_scores * 100).round(1)

    # Sort descending by similarity score
    results_df = results_df.sort_values(by="similarity_score", ascending=False)

    # Return Top-N (capped to length of dataset)
    top_k = max(1, min(top_n, len(results_df)))
    return results_df.head(top_k).reset_index(drop=True)
