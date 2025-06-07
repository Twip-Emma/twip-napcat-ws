#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"
VENV_PATH="${SCRIPT_DIR}/twipenv/bin/activate"
PID_FILE="${SCRIPT_DIR}/bot.pid"

# 检查虚拟环境
[ ! -f "$VENV_PATH" ] && {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Error: Virtual environment not found" | tee -a "${LOG_DIR}/error.log"
    exit 1
}

get_log_file() {
    echo "${LOG_DIR}/$(date +"%Y-%m-%d").log"
}

# 获取实际bot.py的PID
get_bot_pid() {
    pgrep -f "python3.*bot.py"
}

start_bot() {
    # 检查是否已运行
    if [ -f "$PID_FILE" ]; then
        local PID=$(cat "$PID_FILE")
        if ps -p $PID >/dev/null 2>&1; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - bot.py is already running (PID: $PID)" | tee -a "$(get_log_file)"
            return 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting bot.py..." | tee -a "$(get_log_file)"
    
    # 启动bot.py并获取其真实PID
    {
        source "$VENV_PATH"
        python3 "${SCRIPT_DIR}/bot.py" >> "$(get_log_file)" 2>&1 &
        local BOT_PID=$!
        echo $BOT_PID > "$PID_FILE"
        sleep 1
        if ps -p $BOT_PID >/dev/null 2>&1; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - bot.py started (PID: $BOT_PID)" | tee -a "$(get_log_file)"
        else
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Failed to start bot.py" | tee -a "$(get_log_file)"
            rm -f "$PID_FILE"
            return 1
        fi
    } 
}

stop_bot() {
    local BOT_PID=$(get_bot_pid)
    if [ -n "$BOT_PID" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Stopping bot.py (PID: $BOT_PID)..." | tee -a "$(get_log_file)"
        kill $BOT_PID
        rm -f "$PID_FILE"
        # 等待进程结束
        while ps -p $BOT_PID >/dev/null 2>&1; do
            sleep 1
        done
        echo "$(date '+%Y-%m-%d %H:%M:%S') - bot.py stopped" | tee -a "$(get_log_file)"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - bot.py is not running" | tee -a "$(get_log_file)"
        rm -f "$PID_FILE"
    fi
}

restart_bot() {
    stop_bot
    sleep 2
    start_bot
}

case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        BOT_PID=$(get_bot_pid)
        if [ -n "$BOT_PID" ]; then
            echo "bot.py is running (PID: $BOT_PID)"
        else
            echo "bot.py is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac