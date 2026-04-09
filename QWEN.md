# Web Traffic Analyzer

A Streamlit-based web application for analyzing and visualizing daily website traffic data.
Production-ready with Docker containerization and GitHub Actions CI/CD.

## Repository

- **GitHub:** https://github.com/ppasam/TrafficAnalyzer
- **Docker Hub:** https://hub.docker.com/r/ppasam/traffic-analyzer
- **SSH remote:** `git@github.com:ppasam/TrafficAnalyzer.git`

## Project Overview

This project provides:
- An **interactive dashboard** for exploring traffic data with KPIs, charts, and filters.
- **Automatic anomaly detection** using z-score statistics.
- A **synthetic data generator** that creates realistic 3-year web traffic data.
- A **unit test suite** (14 tests) for the analysis module.
- **Docker containerization** for reproducible deployment.
- **CI/CD pipeline** that runs tests on every push/PR and auto-pushes to Docker Hub.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Web framework | Streamlit |
| Data | pandas, numpy |
| Charts | Plotly (plotly_dark theme) |
| Testing | pytest |
| Linting | flake8 |
| Formatting | black (line-length 79) |
| Container | Docker (python:3.12-slim) |
| CI/CD | GitHub Actions |
| Container registry | Docker Hub |

## Project Structure

```
.
├── app.py                      # Streamlit app (entry point)
├── data_loader.py              # CSV loading & caching (@st.cache_data)
├── analysis.py                 # KPIs, z-score anomaly detection, moving average
├── plotting.py                 # Plotly chart creation (line, bar)
├── generate_synthetic_traffic.py # Synthetic data generator
├── test_analysis.py            # 14 unit tests for analysis.py
├── serve.sh                    # Bash helper: start/stop/status
├── Dockerfile                  # Docker image definition
├── .dockerignore               # Docker build exclusions
├── requirements.txt            # Python dependencies
├── aliases.sh                  # Shell aliases (for ~/.bashrc)
├── pages/
│   └── help.py                 # Help page (Streamlit navigation)
├── docs/
│   └── synthetic_traffic.csv   # Default dataset (1096 days)
├── .github/workflows/
│   └── ci.yml                  # CI/CD pipeline
├── .gitignore                  # Git exclusions
└── QWEN.md                     # This file
```

### Module Responsibilities

| Module | Responsibility |
|---|---|
| `app.py` | UI layout, sidebar controls, data flow orchestration |
| `data_loader.py` | CSV loading from path or uploaded file, column validation |
| `analysis.py` | Date filtering, KPI computation, z-score anomaly detection, moving average |
| `plotting.py` | Plotly chart creation (line, bar) |
| `generate_synthetic_traffic.py` | Generates 3 years of synthetic traffic data |
| `test_analysis.py` | Unit tests for analysis module |
| `pages/help.py` | Static help content |

### Public API: `analysis.py`

```python
filter_by_date(df, start, end)        → DataFrame
compute_kpis(df)                       → dict[str, float]
detect_anomalies(df, z_threshold=2.0)  → DataFrame
add_moving_average(df, window=7)       → DataFrame
_compute_z_scores(series)              → Series  (private helper)
```

## Building and Running

### Quick start (Docker — recommended)

```bash
# Pull from Docker Hub
docker pull ppasam/traffic-analyzer:latest

# Run
docker run -d --name traffic-analyzer -p 8501:8501 ppasam/traffic-analyzer:latest
```

Open **http://localhost:8501**.

### From source code

```bash
git clone git@github.com:ppasam/TrafficAnalyzer.git
cd TrafficAnalyzer
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.headless true --server.port 8501
```

### Using serve.sh (local convenience)

```bash
./serve.sh start    # start app
./serve.sh status   # check status
./serve.sh stop     # stop app
```

### Stopping

```bash
# Docker
docker stop traffic-analyzer

# Manual
kill $(lsof -t -i:8501)

# serve.sh
./serve.sh stop
```

### Running tests

```bash
# Activate venv
source venv/bin/activate

# Run tests
python -m pytest test_analysis.py -v

# Lint check
python -m flake8 analysis.py test_analysis.py

# Auto-format
python -m black --line-length 79 analysis.py test_analysis.py
```

### Generate synthetic data

```bash
python generate_synthetic_traffic.py
```

Creates `docs/synthetic_traffic.csv` with:
- **Period:** 2022-01-01 to 2024-12-31 (1096 days)
- **Trend:** +15% annual growth
- **Weekly seasonality:** weekends -30%, Monday +10%
- **Annual seasonality:** summer -20%, Nov-Dec +40%
- **Anomalies:** 5-7 random spikes (2-3× normal)
- **Missing data:** ~2% NaN
- **Noise:** ±5% random variation

### Docker multi-instance

Multiple containers from the same image on different host ports:

```bash
docker run -d --name ta-2 -p 8502:8501 traffic-analyzer:latest
docker run -d --name ta-3 -p 9000:8501 traffic-analyzer:latest
```

### Rebuild and redeploy (local)

```bash
docker build -t traffic-analyzer:latest .
docker rm -f traffic-analyzer
docker run -d --name traffic-analyzer -p 8501:8501 traffic-analyzer:latest
```

## CI/CD Pipeline

GitHub Actions runs on every push/PR to `main`:

```
push / PR to main
   │
   ├─→ job: test
   │     ├─ Setup Python 3.12
   │     ├─ pip install -r requirements.txt pytest flake8 black
   │     ├─ flake8 (PEP 8 linting)
   │     ├─ black --check (format verification)
   │     └─ pytest -v (14 tests)
   │
   └─→ job: build-and-push (if test ✅ and push to main)
         ├─ Docker login
         ├─ Build image
         └─ Push to Docker Hub:
              - ppasam/traffic-analyzer:latest
              - ppasam/traffic-analyzer:<commit-sha>
```

### Required secrets (Settings → Secrets → Actions)

| Secret | Value |
|---|---|
| `DOCKERHUB_USERNAME` | `ppasam` |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

### Useful links

- **Actions:** https://github.com/ppasam/TrafficAnalyzer/actions
- **Docker Hub:** https://hub.docker.com/r/ppasam/traffic-analyzer

## Development Conventions

- **PEP 8** — enforced by flake8, line length 79
- **Type hints** — all function parameters and return values annotated
- **Docstrings** — every function has Args/Returns documentation
- **Modularity** — no file exceeds 400 lines
- **Formatting** — black with `--line-length 79`
- **Testing** — pytest with fixtures for test data, 14 tests covering all analysis functions
- **Immutability** — analysis functions return copies; input DataFrames are not mutated
- **Module constants** — column names and default parameters defined at module top level
- **Data directory** — `docs/` excluded from git except `synthetic_traffic.csv`

## Expected CSV Format

```csv
date,sessions
2022-01-01,1037
2022-01-02,1098
```

| Column | Type | Description |
|---|---|---|
| `date` | YYYY-MM-DD | ISO 8601 date |
| `sessions` | number | Session count (NaN allowed) |

**Rules:** comma delimiter, both columns required, minimum 1 row, recommended: months to years of data.

## SSH Authentication

SSH key: `~/.ssh/ppa_key`. Add before pushing:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/ppa_key
```

## Common Commands Quick Reference

```bash
# Development
./serve.sh start                              # start app
venv/bin/python -m pytest test_analysis.py -v # run tests
venv/bin/python -m flake8 *.py                # lint
venv/bin/python -m black --line-length 79 *.py # format
git add -A && git commit -m "..." && git push # push
./serve.sh stop                               # stop app

# Docker
docker pull ppasam/traffic-analyzer:latest    # download
docker run -d --name traffic-analyzer -p 8501:8501 traffic-analyzer:latest  # run
docker logs traffic-analyzer                  # view logs
docker stop traffic-analyzer && docker rm traffic-analyzer  # cleanup
```
