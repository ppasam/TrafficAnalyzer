# 📊 TrafficAnalyzer

**Web Traffic Analyzer** — интерактивное веб-приложение для анализа и визуализации ежедневной посещаемости сайта. Построено на Streamlit с интерактивными графиками Plotly, автоматическим обнаружением аномалий и KPI-дашбордом.

[![CI/CD](https://github.com/ppasam/TrafficAnalyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/ppasam/TrafficAnalyzer/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/docker/image-size/ppasam/traffic-analyzer)](https://hub.docker.com/r/ppasam/traffic-analyzer)

---

## Функционал

### 📈 Дашборд
- **KPI-метрики** — общее количество сессий, среднее за день, максимум за день
- **Интерактивный график** — ежедневная динамика сессий с подсветкой аномалий (красные X)
- **Скользящее среднее** — опциональная 7-дневная скользящая линия
- **Распределение по дням недели** — среднее количество сессий
- **Распределение по месяцам** — сезонные тренды
- **Таблица данных** — сортируемый просмотр всех записей
- **Фильтр по датам** — выбор произвольного диапазона
- **Загрузка CSV** — drag-and-drop или выбор файла

### ❓ Страница справки
- Описание формата входных данных (CSV)
- Примеры и правила валидации

### 🔍 Обнаружение аномалий
- Z-score метод с настраиваемым порогом (по умолчанию 2σ)
- Автоматическое исключение NaN значений

---

## Архитектура

```
.
├── app.py                      # Streamlit приложение (точка входа)
├── data_loader.py              # Загрузка и кэширование CSV (@st.cache_data)
├── analysis.py                 # Анализ: KPI, аномалии, скользящее среднее
├── plotting.py                 # Plotly графики (line, bar)
├── generate_synthetic_traffic.py # Генератор синтетических данных
├── test_analysis.py            # Юнит-тесты для analysis.py (14 тестов)
├── serve.sh                    # Bash-скрипт start/stop/status
├── pages/
│   └── help.py                 # Страница справки Streamlit
├── .github/workflows/
│   └── ci.yml                  # GitHub Actions CI/CD pipeline
├── docs/
│   └── synthetic_traffic.csv   # Тестовый датасет (1096 дней)
├── Dockerfile                  # Docker-образ
├── .dockerignore               # Исключения для Docker
├── requirements.txt            # Python-зависимости
└── .gitignore                  # Исключения для Git
```

### Модули

| Модуль | Описание |
|--------|----------|
| `app.py` | UI-разметка, боковая панель, оркестрация данных |
| `data_loader.py` | Чтение CSV из файла или загруженного файла, валидация колонок |
| `analysis.py` | Фильтрация по датам, KPI, z-score аномалии, скользящее среднее |
| `plotting.py` | Создание интерактивных Plotly графиков |
| `generate_synthetic_traffic.py` | Генерация реалистичных данных с трендами, сезонностью, шумом |
| `test_analysis.py` | 14 юнит-тестов для всех функций анализа |
| `pages/help.py` | Статическая справка о формате данных |

### Публичный API: `analysis.py`

```python
filter_by_date(df, start, end)        → DataFrame
compute_kpis(df)                       → dict[str, float]
detect_anomalies(df, z_threshold=2.0)  → DataFrame
add_moving_average(df, window=7)       → DataFrame
```

---

## Технологии

| Технология | Назначение |
|------------|-----------|
| Python 3.12 | Основной язык |
| Streamlit | Веб-фреймворк |
| pandas | Обработка данных |
| numpy | Численные операции |
| Plotly | Интерактивные графики |
| pytest | Юнит-тестирование |
| flake8 | PEP 8 линтинг |
| black | Автоформатирование (79 символов) |
| Docker | Контейнеризация |
| GitHub Actions | CI/CD pipeline |

---

## Быстрый запуск

### 1. Через Docker (рекомендуемый способ)

```bash
# Загрузить образ с Docker Hub
docker pull ppasam/traffic-analyzer:latest

# Запустить
docker run -d --name traffic-analyzer -p 8501:8501 ppasam/traffic-analyzer:latest
```

Открой **http://localhost:8501**

### 2. Из исходного кода

```bash
# Клонировать репозиторий
git clone git@github.com:ppasam/TrafficAnalyzer.git
cd TrafficAnalyzer

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt

# Запустить приложение
streamlit run app.py --server.headless true --server.port 8501
```

### 3. Через скрипт serve.sh

```bash
./serve.sh start    # запустить
./serve.sh status   # проверить статус
./serve.sh stop     # остановить
```

### Остановка приложения

```bash
# Если запущено через Docker
docker stop traffic-analyzer

# Если запущено вручную
kill $(lsof -t -i:8501)

# Или через скрипт
./serve.sh stop
```

---

## Запуск тестов

```bash
cd TrafficAnalyzer
source venv/bin/activate

# Запустить все тесты
python -m pytest test_analysis.py -v

# Проверка стиля (PEP 8)
python -m flake8 analysis.py test_analysis.py

# Автоформатирование
python -m black --line-length 79 analysis.py test_analysis.py
```

---

## Генерация тестовых данных

```bash
python generate_synthetic_traffic.py
```

Создаёт `docs/synthetic_traffic.csv` с данными:
- **Период:** 2022-01-01 — 2024-12-31 (1096 дней)
- **Тренд:** +15% годовой рост
- **Недельная сезонность:** будни > выходные, понедельник +10%
- **Годовая сезонность:** лето -20%, ноябрь-декабрь +40%
- **Аномалии:** 5-7 случайных выбросов (2-3× нормы)
- **Пропуски:** ~2% NaN значений
- **Шум:** ±5% случайное отклонение

---

## Docker

### Сборка образа локально

```bash
docker build -t traffic-analyzer:latest .
```

### Запуск контейнера

```bash
docker run -d --name traffic-analyzer -p 8501:8501 traffic-analyzer:latest
```

### Несколько экземпляров на разных портах

```bash
docker run -d --name ta-2 -p 8502:8501 traffic-analyzer:latest
docker run -d --name ta-3 -p 9000:8501 traffic-analyzer:latest
```

### Управление контейнером

```bash
docker ps                          # список запущенных
docker logs traffic-analyzer       # логи
docker stop traffic-analyzer       # остановить
docker rm traffic-analyzer         # удалить
```

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless", "true", \
     "--server.port", "8501", "--server.address", "0.0.0.0"]
```

---

## CI/CD Pipeline

GitHub Actions автоматически запускает тесты при каждом push и pull request на `main`:

```
push / PR на main
   │
   ├─→ job: test
   │     ├─ Setup Python 3.12
   │     ├─ pip install -r requirements.txt
   │     ├─ flake8 (PEP 8 linting)
   │     ├─ black --check (format verification)
   │     └─ pytest -v (14 тестов)
   │
   └─→ job: build-and-push (если test ✅ и push на main)
         ├─ Docker login
         ├─ Build image
         └─ Push to Docker Hub:
              - ppasam/traffic-analyzer:latest
              - ppasam/traffic-analyzer:<commit-sha>
```

### Настройка секретов

В настройках репозитория (**Settings → Secrets → Actions**) нужны:

| Secret | Значение |
|--------|----------|
| `DOCKERHUB_USERNAME` | `ppasam` |
| `DOCKERHUB_TOKEN` | Docker Hub access token |

### Где смотреть

- **Actions:** https://github.com/ppasam/TrafficAnalyzer/actions
- **Docker Hub:** https://hub.docker.com/r/ppasam/traffic-analyzer

---

## Ожидаемый формат CSV

```csv
date,sessions
2022-01-01,1037
2022-01-02,1098
```

| Столбец | Тип | Описание |
|---------|-----|----------|
| `date` | YYYY-MM-DD | Дата в формате ISO 8601 |
| `sessions` | число | Количество сессий (NaN допустим) |

**Правила:**
- Разделитель — запятая
- Оба столбца обязательны
- Минимум 1 строка данных
- Рекомендуется: от нескольких месяцев до нескольких лет

---

## Ключевые решения при разработке

| Решение | Обоснование |
|---------|-------------|
| **Streamlit** вместо Flask/React | Быстрая разработка дашбордов, минимум кода |
| **plotly_dark** тема | Лучшая читаемость на тёмном фоне |
| **Z-score** для аномалий | Простой и надёжный статистический метод |
| **@st.cache_data** | Кэширование загрузки CSV между сессиями |
| **Модульность** (<400 строк/файл) | Лёгкая поддержка и тестирование |
| **Docker** | Воспроизводимая среда, один образ — везде работает |
| **GitHub Actions** | Автоматическое тестирование и деплой |

---

## Лицензия

MIT
