#!/usr/bin/env bash
# ==============================================================================
# WordFeather - 1-Click App Launcher (Linux)
# Tự động bật Docker TTS, khởi chạy Dev Server và mở trình duyệt học tiếng Đức
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

echo "=================================================="
echo "  🪶 Khởi động WordFeather & Giọng đọc Thorsten TTS"
echo "=================================================="

# 1. Kiểm tra & Khởi động Docker Container (thorsten-kokoro-tts)
echo "[1/4] Kiểm tra dịch vụ giọng đọc Thorsten TTS (Docker)..."

# Xác định quyền chạy docker
DOCKER_CMD="docker"
if ! docker info >/dev/null 2>&1; then
    if sudo -n docker info >/dev/null 2>&1; then
        DOCKER_CMD="sudo docker"
    fi
fi

# Kiểm tra container đã tồn tại chưa
if ! $DOCKER_CMD inspect thorsten-kokoro-tts >/dev/null 2>&1; then
    echo "  -> Đang tạo và khởi chạy container 'thorsten-kokoro-tts' lần đầu..."
    $DOCKER_CMD run -d --name thorsten-kokoro-tts \
        -p 8000:8000 \
        -v kokoro_cache:/data/hf-cache \
        --restart unless-stopped \
        thorstenvoice/kokoro-tts:latest >/dev/null 2>&1
else
    # Nếu container đã có, kiểm tra xem có đang chạy không
    IS_RUNNING=$($DOCKER_CMD inspect -f '{{.State.Running}}' thorsten-kokoro-tts 2>/dev/null)
    if [ "$IS_RUNNING" != "true" ]; then
        echo "  -> Đang bật lại container 'thorsten-kokoro-tts'..."
        $DOCKER_CMD start thorsten-kokoro-tts >/dev/null 2>&1
    else
        echo "  -> Container 'thorsten-kokoro-tts' đã sẵn sàng."
    fi
fi

# 2. Đợi dịch vụ TTS sẵn sàng
echo "[2/4] Kiểm tra kết nối model TTS..."
TTS_READY=0
for i in {1..30}; do
    if curl -s -f http://127.0.0.1:8000/health >/dev/null 2>&1; then
        TTS_READY=1
        break
    fi
    sleep 1
done

if [ $TTS_READY -eq 1 ]; then
    echo "  -> Model Thorsten TTS đã kết nối thành công!"
else
    echo "  -> Model TTS đang khởi động hoặc chưa bật (sẽ dự phòng bằng giọng trình duyệt)."
fi

# 3. Khởi chạy Dev Server Proxy (port 8080)
echo "[3/4] Kiểm tra mã nguồn & Khởi chạy Dev Server (cổng 8080)..."

# Tự động phát hiện và build lại từ điển nếu có thay đổi trong template hoặc từ điển JSON
if [ "$PROJECT_DIR/templates/dictionary.template.html" -nt "$PROJECT_DIR/dictionary.html" ] || \
   [ "$PROJECT_DIR/words_final.json" -nt "$PROJECT_DIR/dictionary.html" ]; then
    echo "  -> Phát hiện cập nhật mã từ điển, đang tự động đồng bộ..."
    python3 "$PROJECT_DIR/build.py" --dictionary >/dev/null 2>&1
fi

# Tự động restart dev_server nếu file dev_server.py vừa được cập nhật mới
if [ -f "$PROJECT_DIR/dev_server.pid" ]; then
    PID=$(cat "$PROJECT_DIR/dev_server.pid" | tr -d '[:space:]')
    if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
        if [ "$PROJECT_DIR/dev_server.py" -nt "$PROJECT_DIR/dev_server.pid" ]; then
            echo "  -> Phát hiện mã backend dev_server.py mới, đang khởi động lại server..."
            kill "$PID" 2>/dev/null
            sleep 0.5
        fi
    fi
fi

if curl -s -f http://127.0.0.1:8080/api/tts/health >/dev/null 2>&1; then
    echo "  -> Dev Server đã đang chạy sẵn với mã nguồn mới nhất."
else
    echo "  -> Đang khởi chạy dev_server.py..."
    nohup python3 "$PROJECT_DIR/dev_server.py" > "$PROJECT_DIR/dev_server.log" 2>&1 &
    
    for i in {1..10}; do
        if curl -s -f http://127.0.0.1:8080/api/tts/health >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
fi

# 4. Tự động mở trình duyệt
TARGET_URL="http://localhost:8080/dictionary-h.html"
echo "[4/4] Mở trình duyệt: $TARGET_URL"

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$TARGET_URL" >/dev/null 2>&1 &
elif command -v sensible-browser >/dev/null 2>&1; then
    sensible-browser "$TARGET_URL" >/dev/null 2>&1 &
elif command -v x-www-browser >/dev/null 2>&1; then
    x-www-browser "$TARGET_URL" >/dev/null 2>&1 &
fi

# Lấy địa chỉ IP mạng nội bộ
LAN_IP=$(ip route get 1.1.1.1 2>/dev/null | grep -oP 'src \K\S+' || ip -4 addr show 2>/dev/null | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '^127\.' | grep -v '^172\.17\.' | head -n 1)
[ -z "$LAN_IP" ] && LAN_IP="127.0.0.1"
MOBILE_URL="http://${LAN_IP}:8080/m"

# Gửi thông báo trên desktop nếu có
if command -v notify-send >/dev/null 2>&1; then
    notify-send "WordFeather Deutsch" "Đã khởi động xong! Mobile App: $MOBILE_URL" -i "$PROJECT_DIR/icons/192.png" 2>/dev/null
fi

echo "=================================================="
echo "  🎉 Hoàn tất! Bạn có thể bắt đầu học ngay bây giờ."
echo "--------------------------------------------------"
echo "  💻 Trên Laptop:      http://localhost:8080/"
echo "  📱 Trên Realme GT:   $MOBILE_URL"
echo "  (Mẹo: Mở trên Realme và bấm 'Thêm vào màn hình chính')"
echo "=================================================="

