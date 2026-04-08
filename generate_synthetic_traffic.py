import os
import pandas as pd
import numpy as np
from datetime import datetime

# --- Configuration ---
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
BASE_SESSIONS = 1500
ANNUAL_GROWTH_RATE = 0.15
WEEKEND_REDUCTION = 0.30
MONDAY_BOOST = 0.10
SUMMER_REDUCTION = 0.20
SALES_BOOST = 0.40
ANOMALY_COUNT = 6
ANOMALY_MULTIPLIER_RANGE = (2, 3)
MISSING_DATA_RATE = 0.02
NOISE_RANGE = 0.05

np.random.seed(42)

# --- 1. Generate date range ---
dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
n_days = len(dates)

df = pd.DataFrame({"date": dates})

# --- 2. Base level + upward trend (15% annual growth) ---
day_index = np.arange(n_days)
years_elapsed = day_index / 365.25
trend = BASE_SESSIONS * (1 + ANNUAL_GROWTH_RATE) ** years_elapsed

# --- 3. Weekly seasonality ---
day_of_week = df["date"].dt.dayofweek  # Mon=0 .. Sun=6
week_factors = np.ones(n_days)

weekend_mask = day_of_week >= 5
week_factors[weekend_mask] *= 1 - WEEKEND_REDUCTION

monday_mask = day_of_week == 0
week_factors[monday_mask] *= 1 + MONDAY_BOOST

# --- 4. Annual seasonality ---
month = df["date"].dt.month
annual_factors = np.ones(n_days)

summer_mask = month.isin([6, 7, 8])
annual_factors[summer_mask] *= 1 - SUMMER_REDUCTION

sales_mask = month.isin([11, 12])
annual_factors[sales_mask] *= 1 + SALES_BOOST

# --- 5. Combine base, trend, seasonality ---
sessions = trend * week_factors * annual_factors

# --- 6. Add noise (±5%) ---
noise = np.random.uniform(-NOISE_RANGE, NOISE_RANGE, n_days)
sessions *= (1 + noise)

# Round to integers
sessions = np.round(sessions).astype(float)

df["sessions"] = sessions

# --- 7. Inject anomalies (5-7 spikes, 2-3x normal) ---
n_anomalies = np.random.randint(5, 8)  # 5..7
anomaly_indices = np.random.choice(n_days, size=n_anomalies, replace=False)
for idx in anomaly_indices:
    multiplier = np.random.uniform(*ANOMALY_MULTIPLIER_RANGE)
    df.loc[df.index[idx], "sessions"] = df.loc[df.index[idx], "sessions"] * multiplier

# --- 8. Introduce missing data (~2% NaN) ---
n_missing = int(n_days * MISSING_DATA_RATE)
missing_indices = np.random.choice(n_days, size=n_missing, replace=False)
df.loc[missing_indices, "sessions"] = np.nan

# --- 9. Round remaining values ---
df["sessions"] = df["sessions"].apply(
    lambda x: round(x) if pd.notna(x) else x
)

# --- 10. Save to CSV ---
OUTPUT_DIR = "docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "synthetic_traffic.csv")
df["date"] = df["date"].dt.strftime("%Y-%m-%d")
df.to_csv(OUTPUT_FILE, index=False)

print(f"Generated {n_days} rows of synthetic traffic data.")
print(f"Date range: {START_DATE} to {END_DATE}")
print(f"Mean sessions: {df['sessions'].mean():.0f}")
print(f"Anomalies injected: {n_anomalies}")
print(f"Missing values: {df['sessions'].isna().sum()} ({df['sessions'].isna().sum()/n_days*100:.1f}%)")
print(f"Saved to {OUTPUT_FILE}")
