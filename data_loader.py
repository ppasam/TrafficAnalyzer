"""Module for loading and caching traffic data from CSV files."""

from __future__ import annotations

import io
import pandas as pd
import streamlit as st


@st.cache_data
def load_traffic_data_from_path(filepath: str) -> pd.DataFrame:
    """Load traffic data from a CSV file path and cache the result.

    Args:
        filepath: Path to the CSV file containing traffic data.

    Returns:
        DataFrame with 'date' (datetime) and 'sessions' (float) columns.

    Raises:
        ValueError: If required columns are missing.
    """
    df = pd.read_csv(filepath, parse_dates=["date"])
    _validate_columns(df)
    return df


def load_traffic_data_from_upload(
    uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
) -> pd.DataFrame:
    """Load traffic data from an uploaded Streamlit file object.

    Args:
        uploaded_file: A Streamlit UploadedFile instance.

    Returns:
        DataFrame with 'date' (datetime) and 'sessions' (float) columns.

    Raises:
        ValueError: If required columns are missing or data is invalid.
    """
    raw = uploaded_file.getvalue()
    df = pd.read_csv(io.BytesIO(raw), parse_dates=["date"])
    _validate_columns(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    """Ensure the DataFrame has the required columns.

    Args:
        df: DataFrame to validate.

    Raises:
        ValueError: If 'date' or 'sessions' column is missing.
    """
    required = {"date", "sessions"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")
