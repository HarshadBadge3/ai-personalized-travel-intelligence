"""Preprocessing functions for cleaning and enriching destination data."""
from pathlib import Path
import pandas as pd


def preprocess_destinations(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize destination dataset fields.

    Args:
        df: Raw destinations DataFrame.

    Returns:
        pd.DataFrame: Cleaned and structured DataFrame.
    """
    clean_df = df.copy()

    # Strip whitespace from string columns
    str_cols = ["destination", "state", "category", "description", "best_season", "activities"]
    for col in str_cols:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].astype(str).str.strip()

    # Ensure numeric columns are properly typed
    if "rating" in clean_df.columns:
        clean_df["rating"] = pd.to_numeric(clean_df["rating"], errors="coerce").fillna(4.0)

    if "estimated_cost" in clean_df.columns:
        clean_df["estimated_cost"] = pd.to_numeric(clean_df["estimated_cost"], errors="coerce").fillna(5000)

    # Derive budget tier if missing or standardize it
    if "budget_tier" not in clean_df.columns:
        clean_df["budget_tier"] = clean_df["estimated_cost"].apply(assign_budget_tier)
    else:
        clean_df["budget_tier"] = clean_df["budget_tier"].fillna(
            clean_df["estimated_cost"].apply(assign_budget_tier)
        )

    # Parse latitude and longitude if location exists as 'lat, lon'
    if "location" in clean_df.columns:
        coords = clean_df["location"].str.split(",", expand=True)
        if coords.shape[1] >= 2:
            clean_df["latitude"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
            clean_df["longitude"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")

    return clean_df


def assign_budget_tier(cost: float) -> str:
    """Helper function to classify budget tier based on estimated cost."""
    if cost <= 5000:
        return "Budget"
    elif cost <= 10000:
        return "Moderate"
    else:
        return "Luxury"


def save_processed_destinations(df: pd.DataFrame, output_path: str | Path | None = None) -> Path:
    """Save cleaned destination dataframe to processed directory."""
    if output_path is None:
        from src.data_loader import get_project_root
        output_path = get_project_root() / "data" / "processed" / "destinations_clean.csv"
    
    path_obj = Path(output_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path_obj, index=False)
    return path_obj
