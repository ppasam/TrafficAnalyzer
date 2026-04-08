"""Unit tests for the analysis module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis import (
    add_moving_average,
    compute_kpis,
    detect_anomalies,
    filter_by_date,
)

# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Small DataFrame with known session values."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2022-01-01",
                    "2022-01-02",
                    "2022-01-03",
                    "2022-01-04",
                    "2022-01-05",
                ]
            ),
            "sessions": [100.0, 200.0, 300.0, 400.0, 500.0],
        }
    )


@pytest.fixture
def df_with_nans() -> pd.DataFrame:
    """DataFrame containing NaN values in sessions."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2022-01-01", "2022-01-02", "2022-01-03"]),
            "sessions": [100.0, np.nan, 300.0],
        }
    )


@pytest.fixture
def empty_df() -> pd.DataFrame:
    """Empty DataFrame with the correct columns."""
    return pd.DataFrame(columns=["date", "sessions"]).astype(
        {"date": "datetime64[ns]", "sessions": "float64"}
    )


@pytest.fixture
def df_with_anomaly() -> pd.DataFrame:
    """DataFrame with one obvious outlier (z-score > 2)."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime([f"2022-01-{d:02d}" for d in range(1, 11)]),
            "sessions": [100.0] * 9 + [10000.0],  # last row is a clear anomaly
        }
    )


# ── filter_by_date ──────────────────────────────────────────────


def test_filter_by_date_inclusive(sample_df: pd.DataFrame) -> None:
    """Dates matching start/end are included."""
    result = filter_by_date(sample_df, "2022-01-02", "2022-01-04")
    assert len(result) == 3
    assert result["sessions"].tolist() == [200.0, 300.0, 400.0]


def test_filter_by_date_no_match(sample_df: pd.DataFrame) -> None:
    """Returns empty DataFrame when no dates match."""
    result = filter_by_date(sample_df, "2023-01-01", "2023-01-31")
    assert result.empty


def test_filter_by_date_full_range(sample_df: pd.DataFrame) -> None:
    """Full range returns all rows."""
    result = filter_by_date(sample_df, "2020-01-01", "2030-01-01")
    assert len(result) == len(sample_df)


# ── compute_kpis ────────────────────────────────────────────────


def test_compute_kpis_normal(sample_df: pd.DataFrame) -> None:
    """Basic correctness check."""
    kpis = compute_kpis(sample_df)
    assert kpis["total_sessions"] == pytest.approx(1500.0)
    assert kpis["avg_sessions"] == pytest.approx(300.0)
    assert kpis["max_sessions"] == pytest.approx(500.0)


def test_compute_kpis_ignores_nans(df_with_nans: pd.DataFrame) -> None:
    """NaN values should be excluded from calculations."""
    kpis = compute_kpis(df_with_nans)
    assert kpis["total_sessions"] == pytest.approx(400.0)
    assert kpis["avg_sessions"] == pytest.approx(200.0)
    assert kpis["max_sessions"] == pytest.approx(300.0)


def test_compute_kpis_empty_df(empty_df: pd.DataFrame) -> None:
    """Empty DataFrame should return NaN for avg/max and 0 for total."""
    kpis = compute_kpis(empty_df)
    assert kpis["total_sessions"] == 0.0
    assert np.isnan(kpis["avg_sessions"])
    assert np.isnan(kpis["max_sessions"])


# ── detect_anomalies ────────────────────────────────────────────


def test_detect_anomalies_flags_outlier(df_with_anomaly: pd.DataFrame) -> None:
    """The spike row should be flagged as anomaly."""
    result = detect_anomalies(df_with_anomaly)
    assert result["is_anomaly"].iloc[-1] == True  # noqa: E712
    assert (result["is_anomaly"].iloc[:-1] == False).all()  # noqa: E712


def test_detect_anomalies_no_anomalies(sample_df: pd.DataFrame) -> None:
    """Uniformly spaced data should have no anomalies at default threshold."""
    result = detect_anomalies(sample_df)
    assert "is_anomaly" in result.columns
    assert result["is_anomaly"].sum() == 0


def test_detect_anomalies_too_few_rows() -> None:
    """A single-row DataFrame should have is_anomaly=False."""
    single = pd.DataFrame(
        {"date": pd.to_datetime(["2022-01-01"]), "sessions": [100.0]}
    )
    result = detect_anomalies(single)
    assert result["is_anomaly"].iloc[0] == False  # noqa: E712


def test_detect_anomalies_custom_threshold(sample_df: pd.DataFrame) -> None:
    """Lower threshold should flag more rows as anomalies."""
    strict = detect_anomalies(sample_df, z_threshold=0.5)
    default = detect_anomalies(sample_df, z_threshold=2.0)
    assert strict["is_anomaly"].sum() >= default["is_anomaly"].sum()


def test_detect_anomalies_original_unchanged(sample_df: pd.DataFrame) -> None:
    """Input DataFrame should not be mutated (returns a copy)."""
    original_sessions = sample_df["sessions"].copy()
    detect_anomalies(sample_df)
    pd.testing.assert_series_equal(sample_df["sessions"], original_sessions)


# ── add_moving_average ─────────────────────────────────────────


def test_add_moving_average_default_window(sample_df: pd.DataFrame) -> None:
    """Default window=7 should produce a sessions_ma column."""
    result = add_moving_average(sample_df)
    assert "sessions_ma" in result.columns
    # First row: min_periods=1 → equals the value itself
    assert result["sessions_ma"].iloc[0] == pytest.approx(100.0)
    # Second row: mean of [100, 200]
    assert result["sessions_ma"].iloc[1] == pytest.approx(150.0)


def test_add_moving_average_custom_window(sample_df: pd.DataFrame) -> None:
    """Custom window should be respected."""
    result = add_moving_average(sample_df, window=3)
    assert "sessions_ma" in result.columns
    # Row 3 (0-indexed): mean of [100, 200, 300, 400] → window=3 → last 3
    assert result["sessions_ma"].iloc[2] == pytest.approx(200.0)


def test_add_moving_average_original_unchanged(
    sample_df: pd.DataFrame,
) -> None:
    """Input DataFrame should not be mutated."""
    original_cols = list(sample_df.columns)
    add_moving_average(sample_df)
    assert list(sample_df.columns) == original_cols
