"""Module for analyzing traffic data: statistics and anomaly detection."""

from __future__ import annotations

import pandas as pd

# ── Module constants ─────────────────────────────────────────────

COL_DATE = "date"
COL_SESSIONS = "sessions"
COL_IS_ANOMALY = "is_anomaly"
COL_SESSIONS_MA = "sessions_ma"

DEFAULT_Z_THRESHOLD = 2.0
DEFAULT_MA_WINDOW = 7
MIN_ROWS_FOR_ZSCORE = 2


# ── Public functions ─────────────────────────────────────────────


def filter_by_date(df: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Filter data to a date range (inclusive).

    Args:
        df: DataFrame with a date column.
        start: Start date as ISO string (YYYY-MM-DD).
        end: End date as ISO string (YYYY-MM-DD).

    Returns:
        A new DataFrame containing only rows within the range.
    """
    mask = (df[COL_DATE] >= start) & (df[COL_DATE] <= end)
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Compute key performance indicators.

    Calculates total, average, and maximum sessions from non-null values.

    Args:
        df: DataFrame with a sessions column.

    Returns:
        Dictionary with keys ``total_sessions``, ``avg_sessions``,
        and ``max_sessions``. All values are float.
    """
    sessions = df[COL_SESSIONS].dropna()
    return {
        "total_sessions": float(sessions.sum()),
        "avg_sessions": float(sessions.mean()),
        "max_sessions": float(sessions.max()),
    }


def detect_anomalies(
    df: pd.DataFrame,
    z_threshold: float = DEFAULT_Z_THRESHOLD,
) -> pd.DataFrame:
    """Flag rows where sessions deviate significantly from the mean.

    Uses z-score on non-null values. A row is flagged when
    ``|z-score| > z_threshold``.

    Args:
        df: DataFrame with a sessions column.
        z_threshold: Number of standard deviations to consider anomalous.

    Returns:
        A new DataFrame with an additional boolean ``is_anomaly`` column.
    """
    df = df.copy()

    if len(df[COL_SESSIONS].dropna()) < MIN_ROWS_FOR_ZSCORE:
        df[COL_IS_ANOMALY] = False
        return df

    z_scores = _compute_z_scores(df[COL_SESSIONS])
    df[COL_IS_ANOMALY] = z_scores.abs() > z_threshold
    return df


def add_moving_average(
    df: pd.DataFrame,
    window: int = DEFAULT_MA_WINDOW,
) -> pd.DataFrame:
    """Add a rolling mean column to the DataFrame.

    Args:
        df: DataFrame with a sessions column.
        window: Size of the rolling window in days.

    Returns:
        A new DataFrame with an additional ``sessions_ma`` column.
    """
    df = df.copy()
    df[COL_SESSIONS_MA] = (
        df[COL_SESSIONS].rolling(window=window, min_periods=1).mean()
    )
    return df


# ── Private helper functions ─────────────────────────────────────


def _compute_z_scores(series: pd.Series) -> pd.Series:
    """Compute z-scores for a numeric Series, handling NaN and zero variance.

    NaN values propagate as NaN in the output. When the standard deviation
    is zero (all values identical), every z-score is set to 0.0.

    Args:
        series: Numeric Series (may contain NaN).

    Returns:
        A Series of z-scores with the same index as the input.
    """
    valid = series.dropna()

    if len(valid) < MIN_ROWS_FOR_ZSCORE:
        return pd.Series(0.0, index=series.index)

    mean_val = valid.mean()
    std_val = valid.std()

    if std_val == 0.0:
        return pd.Series(0.0, index=series.index)

    return (series - mean_val) / std_val
