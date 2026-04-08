"""Module for analyzing traffic data: statistics and anomaly detection."""

from __future__ import annotations

import numpy as np
import pandas as pd


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Filter the DataFrame to a given date range (inclusive).

    Args:
        df: DataFrame with a 'date' column.
        start: Start date as ISO string (YYYY-MM-DD).
        end: End date as ISO string (YYYY-MM-DD).

    Returns:
        Filtered DataFrame.
    """
    mask = (df["date"] >= start) & (df["date"] <= end)
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Compute key performance indicators for the given data.

    Args:
        df: DataFrame with a 'sessions' column.

    Returns:
        Dictionary with keys 'total_sessions', 'avg_sessions', 'max_sessions'.
    """
    valid = df["sessions"].dropna()
    return {
        "total_sessions": float(valid.sum()),
        "avg_sessions": float(valid.mean()),
        "max_sessions": float(valid.max()),
    }


def detect_anomalies(df: pd.DataFrame, z_threshold: float = 2.0) -> pd.DataFrame:
    """Flag rows where sessions deviate significantly from the mean.

    Uses z-score on non-null values. Rows with |z| > z_threshold are flagged.

    Args:
        df: DataFrame with a 'sessions' column.
        z_threshold: Number of standard deviations to consider anomalous.

    Returns:
        DataFrame with an extra boolean column 'is_anomaly'.
    """
    df = df.copy()
    valid = df["sessions"].dropna()
    if len(valid) < 2:
        df["is_anomaly"] = False
        return df

    mean = valid.mean()
    std = valid.std()
    z_scores = (df["sessions"] - mean) / std if std > 0 else 0.0
    df["is_anomaly"] = z_scores.abs() > z_threshold
    return df


def add_moving_average(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    """Add a 7-day moving average column to the DataFrame.

    Args:
        df: DataFrame with a 'sessions' column.
        window: Size of the moving window.

    Returns:
        DataFrame with an extra 'sessions_ma' column.
    """
    df = df.copy()
    df["sessions_ma"] = df["sessions"].rolling(window=window, min_periods=1).mean()
    return df
