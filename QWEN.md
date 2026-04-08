# Web Traffic Analyzer

A Streamlit-based web application for analyzing and visualizing daily website traffic data.

## Project Overview

This project provides:
- A **synthetic data generator** that creates realistic 3-year web traffic data with trends, seasonality, anomalies, and missing values.
- An **interactive dashboard** for exploring traffic data with KPIs, charts, and filters.
- A **help page** documenting the expected CSV input format.
- A **unit test suite** for the analysis module.

## Tech Stack

- **Python 3.12+**
- **Streamlit** — web UI framework
- **pandas** — data manipulation
- **numpy** — numerical operations
- **plotly** — interactive charts
- **pytest** — testing framework
- **flake8** — PEP 8 linting
- **black** — code formatting (line-length 79)

## Project Structure

```
.
├── app.py                      # Main Streamlit application (entry point)
├── data_loader.py              # CSV loading & caching (@st.cache_data)
├── analysis.py                 # Data analysis: KPIs, anomaly detection, moving average
├── plotting.py                 # Plotly chart functions (line, bar charts)
├── generate_synthetic_traffic.py # Script to generate synthetic traffic data
├── test_analysis.py            # Unit tests for analysis module
├── serve.sh                    # Start/stop/status helper script
├── aliases.sh                  # Shell aliases (for ~/.bashrc)
├── pages/
│   └── help.py                 # Help page (accessible via Streamlit navigation)
├── docs/                       # Application data (excluded from git)
│   └── synthetic_traffic.csv   # Default synthetic dataset
├── venv/                       # Python virtual environment (excluded from git)
├── startproject.md             # Quick-start guide (launch, stop, recreate venv)
├── .gitignore                  # Git ignore rules
└── QWEN.md                     # This file
```

## Repository

- **GitHub:** https://github.com/ppasam/TrafficAnalyzer
- **SSH remote:** `git@github.com:ppasam/TrafficAnalyzer.git`

## Running the App

### Quick way (serve.sh)

| Action | Command |
|--------|---------|
| Start | `./serve.sh start` |
| Stop | `./serve.sh stop` |
| Status | `./serve.sh status` |

### Manual way

```bash
cd /home/ppasam/Documents/projects/TrafficAnalyzer
source venv/bin/activate
streamlit run app.py --server.headless true --server.port 8501
```

Open **http://localhost:8501** in your browser.

### Stopping the app

```bash
./serve.sh stop
# or:
kill $(lsof -t -i:8501)
```

### Recreate virtual environment (after renaming the project folder)

If you rename the project directory, the existing `venv/` will break (its internal paths are absolute). Recreate it:

```bash
rm -rf venv && python3 -m venv venv && venv/bin/pip install streamlit pandas numpy plotly
```

## Setup

### 1. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install streamlit pandas numpy plotly
# For development:
pip install pytest flake8 black
```

### 3. Generate synthetic data (optional)

```bash
python3 generate_synthetic_traffic.py
```

This creates `docs/synthetic_traffic.csv` with 1096 days of data (2022-01-01 to 2024-12-31).

### 4. Set up SSH authentication

The project uses SSH to push to GitHub. Key: `~/.ssh/ppa_key`.
Before pushing, add it to the agent:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/ppa_key
```

### 5. Git push

```bash
git add -A && git commit -m "..." && git push
```

## Testing

### Run tests

```bash
venv/bin/python -m pytest test_analysis.py -v
```

### Check style

```bash
# PEP 8 linting
venv/bin/python -m flake8 analysis.py test_analysis.py

# Auto-formatting
venv/bin/python -m black --line-length 79 analysis.py test_analysis.py
```

### Test coverage

The `analysis.py` module has **14 unit tests** covering:
- `filter_by_date` — inclusive range, no match, full range
- `compute_kpis` — normal data, NaN handling, empty DataFrame
- `detect_anomalies` — outlier flagging, no anomalies, too few rows, custom threshold, immutability
- `add_moving_average` — default/custom window, immutability

## Features

### Dashboard (`app.py`)
- **File upload** — drag-and-drop or browse for CSV files via sidebar
- **Default data** — uses `docs/synthetic_traffic.csv` if no file is uploaded
- **Date range filter** — `st.date_input` for start/end date selection
- **Moving average toggle** — checkbox to overlay a 7-day moving average on the main chart
- **KPI metrics** — total sessions, average per day, maximum per day
- **Interactive line chart** — daily sessions with anomaly highlighting (red X markers)
- **Distribution charts** — average sessions by day of week and by month
- **Data table** — sortable DataFrame view of all records

### Help Page (`pages/help.py`)
- Documents required CSV columns: `date` (YYYY-MM-DD), `sessions` (number)
- Shows example CSV content
- Lists validation rules and recommendations

### Data Generator (`generate_synthetic_traffic.py`)
- **Trend** — 15% annual growth
- **Weekly seasonality** — weekends -30%, Monday +10% boost
- **Annual seasonality** — summer (Jun-Aug) -20%, sales season (Nov-Dec) +40%
- **Anomalies** — 5-7 random spikes at 2-3× normal value
- **Missing data** — ~2% of `sessions` values replaced with NaN
- **Noise** — ±5% random variation per day

## Module Responsibilities

| Module | Responsibility | Line limit |
|---|---|---|
| `app.py` | UI layout, sidebar controls, data flow orchestration | < 400 |
| `data_loader.py` | CSV loading from path or uploaded file, column validation | < 400 |
| `analysis.py` | Date filtering, KPI computation, z-score anomaly detection, moving average | < 400 |
| `plotting.py` | Plotly chart creation (line, bar) | < 400 |
| `pages/help.py` | Static help content | < 400 |
| `test_analysis.py` | Unit tests for analysis module | — |

### Public API: `analysis.py`

```
filter_by_date(df, start, end)        → DataFrame
compute_kpis(df)                       → dict[str, float]
detect_anomalies(df, z_threshold=2.0)  → DataFrame
add_moving_average(df, window=7)       → DataFrame
_compute_z_scores(series)              → Series  (private)
```

## Development Conventions

- **PEP 8** — all code follows standard Python style, enforced by flake8
- **Type hints** — all function parameters and return values are annotated
- **Docstrings** — every function has a docstring with Args/Returns/Raises
- **Modularity** — no file exceeds 400 lines
- **Formatting** — black with `--line-length 79`
- **Line length** — 79 characters (flake8 default)
- **Data directory** — all generated/sample data lives in `docs/`, excluded from git via `.gitignore`
- **Module constants** — column names and default parameters are defined at module level (`analysis.py`)
- **Immutability** — analysis functions return copies; input DataFrames are not mutated

## Expected CSV Format

```csv
date,sessions
2022-01-01,1037
2022-01-02,1098
```

- `date`: ISO 8601 format (`YYYY-MM-DD`), parsed as datetime
- `sessions`: numeric (int/float), NaN values allowed

## Common Commands Quick Reference

```bash
# Development workflow
./serve.sh start                          # start app
venv/bin/python -m pytest test_analysis.py -v  # run tests
venv/bin/python -m flake8 *.py            # lint check
venv/bin/python -m black --line-length 79 *.py  # format
git add -A && git commit -m "..." && git push   # commit & push
./serve.sh stop                           # stop app
```
