"""Main Streamlit application for web traffic analysis."""

from __future__ import annotations

import os
import pandas as pd
import streamlit as st

from analysis import add_moving_average, compute_kpis, detect_anomalies, filter_by_date
from data_loader import load_traffic_data_from_path, load_traffic_data_from_upload

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="Анализатор Трафика Веб-сайта",
    page_icon="📊",
    layout="wide",
)

# ── Import plotting lazily to avoid errors on help page ────────
from plotting import (  # noqa: E402
    plot_monthly_distribution,
    plot_sessions,
    plot_weekday_distribution,
)

# ── Sidebar: data source ──────────────────────────────────────
st.sidebar.header("📂 Источник данных")

uploaded_file = st.sidebar.file_uploader(
    "Загрузить CSV",
    type=["csv"],
    help="Формат: столбцы date (YYYY-MM-DD) и sessions (число).",
)

DEFAULT_CSV = os.path.join("docs", "synthetic_traffic.csv")

if uploaded_file is not None:
    try:
        data = load_traffic_data_from_upload(uploaded_file)
        st.sidebar.success(f"✅ Загружен: `{uploaded_file.name}`")
    except ValueError as e:
        st.sidebar.error(f"❌ Ошибка: {e}")
        st.stop()
    except Exception as e:
        st.sidebar.error(f"❌ Не удалось прочитать файл: {e}")
        st.stop()
else:
    try:
        data = load_traffic_data_from_path(DEFAULT_CSV)
        st.sidebar.info(f"📄 Используется по умолчанию: `{DEFAULT_CSV}`")
    except FileNotFoundError:
        st.error(
            f"Файл `{DEFAULT_CSV}` не найден. Загрузите CSV-файл через боковую панель."
        )
        st.stop()
    except ValueError as e:
        st.sidebar.error(f"❌ Ошибка в файле `{DEFAULT_CSV}`: {e}")
        st.stop()

if data.empty:
    st.error("Данные пусты.")
    st.stop()

# ── Sidebar controls ───────────────────────────────────────────
st.sidebar.header("⚙️ Настройки")

min_date = data["date"].min()
max_date = data["date"].max()

start_date, end_date = st.sidebar.date_input(
    "Диапазон дат",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

show_moving_avg = st.sidebar.checkbox(
    "Показать скользящее среднее (7 дней)",
    value=False,
)

# ── Filter data ────────────────────────────────────────────────
filtered = filter_by_date(data, str(start_date), str(end_date))

if filtered.empty:
    st.warning("Нет данных за выбранный период.")
    st.stop()

# ── Compute KPIs ───────────────────────────────────────────────
kpis = compute_kpis(filtered)
col1, col2, col3 = st.columns(3)

col1.metric("Общее количество сессий", f"{kpis['total_sessions']:,.0f}")
col2.metric("Среднее в день", f"{kpis['avg_sessions']:,.0f}")
col3.metric("Максимум в день", f"{kpis['max_sessions']:,.0f}")

# ── Enrich data for plotting ───────────────────────────────────
filtered = add_moving_average(filtered) if show_moving_avg else filtered.copy()
filtered = detect_anomalies(filtered)

# ── Main chart ─────────────────────────────────────────────────
st.subheader("📈 Динамика сессий")
fig_sessions = plot_sessions(
    filtered,
    show_moving_average=show_moving_avg,
    highlight_anomalies=True,
)
st.plotly_chart(fig_sessions, use_container_width=True)

# ── Distribution charts ────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📅 По дням недели")
    fig_weekday = plot_weekday_distribution(filtered)
    st.plotly_chart(fig_weekday, use_container_width=True)

with col_right:
    st.subheader("📆 По месяцам")
    fig_monthly = plot_monthly_distribution(filtered)
    st.plotly_chart(fig_monthly, use_container_width=True)

# ── Data table ─────────────────────────────────────────────────
st.subheader("📋 Таблица данных")
display_df = filtered.sort_values("date", ascending=False).reset_index(drop=True)
display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
st.dataframe(display_df, use_container_width=True)
