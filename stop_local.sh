#!/usr/bin/env bash
# ==============================================================================
# WordFeather - Stop Dev Server (Linux)
# Chỉ tắt Dev Server WordFeather, không tắt Docker container
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

PID_FILE="$PROJECT_DIR/dev_server.pid"

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" | tr -d '[:space:]')
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        kill "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        echo "[OK] Đã dừng server WordFeather (PID $PID)."
        exit 0
    fi
    rm -f "$PID_FILE"
fi

PIDS=$(pgrep -f "python.*dev_server.py" || true)
if [ -n "$PIDS" ]; then
    kill $PIDS 2>/dev/null
    echo "[OK] Đã dừng tiến trình dev_server."
else
    echo "[INFO] Không có dev_server nào đang chạy."
fi

