# Запуск проекта

## Быстрый способ (скрипт serve.sh)

| Действие | Команда |
|----------|---------|
|  Запустить | `./serve.sh start` |
| 🔴 Остановить | `./serve.sh stop` |
| 📡 Статус | `./serve.sh status` |

## Альтернатива: алиасы в ~/.bashrc

Добавь в `~/.bashrc` (или `~/.zshrc`):

```bash
alias ta-start='/home/ppasam/Documents/projects/TrafficAnalyzer/serve.sh start'
alias ta-stop='/home/ppasam/Documents/projects/TrafficAnalyzer/serve.sh stop'
alias ta-status='/home/ppasam/Documents/projects/TrafficAnalyzer/serve.sh status'
```

Затем просто:

```bash
ta-start   # запустить
ta-stop    # остановить
ta-status  # проверить статус
```

## Ручной способ

```bash
cd /home/ppasam/Documents/projects/TrafficAnalyzer
source venv/bin/activate
streamlit run app.py --server.headless true --server.port 8501
```

Остановить:

```bash
kill $(lsof -t -i:8501)
```

## Запуск тестов

```bash
cd /home/ppasam/Documents/projects/TrafficAnalyzer
source venv/bin/activate

# Запустить все тесты
pytest test_analysis.py -v

# Или без активации venv:
venv/bin/python -m pytest test_analysis.py -v
```

Проверка стиля:

```bash
# PEP 8 — linting
venv/bin/python -m flake8 analysis.py test_analysis.py

# Автоформатирование
venv/bin/python -m black --line-length 79 analysis.py test_analysis.py
```

## Если переименовал папку — venv нужно пересоздать

```bash
rm -rf venv && python3 -m venv venv && venv/bin/pip install streamlit pandas numpy plotly
```
