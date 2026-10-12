"""Data loader module for loading raw and processed travel datasets."""
from pathlib import Path
import pandas as pd


def get_project_root() -> Path:
    """Return the base path of the travel_intelligence project directory."""
    return Path(__file__).resolve().parent.parent


def load_raw_destinations(filepath: str | Path | None = None) -> pd.DataFrame:
    """Load the raw destinations CSV dataset.

    Args:
        filepath: Optional path to the CSV file. If None, default raw path is used.

    Returns:
        pd.DataFrame: Loaded raw destinations dataframe.
    """
    if filepath is None:
        filepath = get_project_root() / "data" / "raw" / "destinations.csv"
    
    path_obj = Path(filepath)
    if not path_obj.exists():
        raise FileNotFoundError(f"Destinations dataset not found at: {path_obj}")
    
    return pd.read_csv(path_obj)
