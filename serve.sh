#!/usr/bin/env bash
# Streamlit app start/stop helper for TrafficAnalyzer

PROJECT_DIR="/home/ppasam/Documents/projects/TrafficAnalyzer"
PID_FILE="$PROJECT_DIR/.streamlit.pid"

start_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✅ Приложение уже запущено (PID: $PID)"
            echo "🌐 http://localhost:8501"
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi

    cd "$PROJECT_DIR"
    source venv/bin/activate
    streamlit run app.py --server.headless true --server.port 8501 &
    STREAMLIT_PID=$!
    echo $STREAMLIT_PID > "$PID_FILE"
    echo "✅ Приложение запущено (PID: $STREAMLIT_PID)"
    echo "🌐 http://localhost:8501"
}

stop_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm -f "$PID_FILE"
            echo "🛑 Приложение остановлено (PID: $PID)"
        else
            rm -f "$PID_FILE"
            echo "⚠️ Процесс уже был завершён"
        fi
    else
        # Fallback: try lsof
        PIDS=$(lsof -t -i:8501 2>/dev/null)
        if [ -n "$PIDS" ]; then
            kill $PIDS
            echo "🛑 Процесс(ы) на порту 8501 завершены: $PIDS"
        else
            echo "⚠️ Приложение не запущено"
        fi
    fi
}

status_app() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "🟢 Запущено (PID: $PID)"
            echo "🌐 http://localhost:8501"
        else
            rm -f "$PID_FILE"
            echo "🔴 Не запущено"
        fi
    else
        echo "🔴 Не запущено"
    fi
}

case "${1:-start}" in
    start)   start_app ;;
    stop)    stop_app ;;
    status)  status_app ;;
    *)       echo "Usage: $0 {start|stop|status}"; exit 1 ;;
esac
