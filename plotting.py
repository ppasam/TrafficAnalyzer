"""Module for creating interactive Plotly charts from traffic data."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_sessions(
    df: pd.DataFrame,
    show_moving_average: bool = False,
    highlight_anomalies: bool = True,
) -> go.Figure:
    """Create an interactive line chart of daily sessions.

    Args:
        df: DataFrame with 'date', 'sessions', and optionally 'sessions_ma'
            and 'is_anomaly' columns.
        show_moving_average: Whether to overlay the moving-average line.
        highlight_anomalies: Whether to mark anomalous points.

    Returns:
        A Plotly Figure object.
    """
    fig = px.line(
        df,
        x="date",
        y="sessions",
        title="Daily Sessions",
        labels={"date": "Date", "sessions": "Sessions"},
        template="plotly_dark",
    )

    fig.update_traces(line=dict(color="#00BFFF", width=1.2))

    if show_moving_average and "sessions_ma" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["sessions_ma"],
                mode="lines",
                name="7-day Moving Avg",
                line=dict(color="#FF8C00", width=2),
            )
        )

    if highlight_anomalies and "is_anomaly" in df.columns:
        anomalies = df[df["is_anomaly"]].copy()
        if not anomalies.empty:
            fig.add_trace(
                go.Scatter(
                    x=anomalies["date"],
                    y=anomalies["sessions"],
                    mode="markers",
                    name="Anomalies",
                    marker=dict(color="#FF4444", size=10, symbol="x"),
                )
            )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Sessions",
        hovermode="x unified",
        showlegend=True,
    )

    return fig


def plot_weekday_distribution(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing average sessions by day of week.

    Args:
        df: DataFrame with 'date' and 'sessions' columns.

    Returns:
        A Plotly Figure object.
    """
    weekday_names = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df = df.copy()
    df["weekday"] = df["date"].dt.dayofweek
    avg_by_day = df.groupby("weekday")["sessions"].mean().reindex(range(7))

    fig = px.bar(
        x=avg_by_day.index,
        y=avg_by_day.values,
        labels={"x": "Day of Week", "y": "Avg Sessions"},
        title="Average Sessions by Day of Week",
        template="plotly_dark",
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(7)),
            ticktext=weekday_names,
        ),
        hovermode="x",
    )

    return fig


def plot_monthly_distribution(df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing average sessions by month.

    Args:
        df: DataFrame with 'date' and 'sessions' columns.

    Returns:
        A Plotly Figure object.
    """
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]
    df = df.copy()
    df["month"] = df["date"].dt.month
    avg_by_month = df.groupby("month")["sessions"].mean().reindex(range(1, 13))

    fig = px.bar(
        x=avg_by_month.index,
        y=avg_by_month.values,
        labels={"x": "Month", "y": "Avg Sessions"},
        title="Average Sessions by Month",
        template="plotly_dark",
    )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(1, 13)),
            ticktext=month_names,
        ),
        hovermode="x",
    )

    return fig
