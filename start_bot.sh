#!/bin/bash

SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
LOG_DIR="${SCRIPT_DIR}/logs"
mkdir -p "$LOG_DIR"
VENV_PATH="${SCRIPT_DIR}/twipenv/bin/activate"
PID_FILE="${SCRIPT_DIR}/bot.pid"

# 设置 MEME_HOME 环境变量
export MEME_HOME="${SCRIPT_DIR}/data"
# 如果需要在脚本中使用，也可以导出到系统环境
# 创建数据目录（如果不存在）
mkdir -p "$MEME_HOME"

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
    echo "$(date '+%Y-%m-%d %H:%M:%S') - MEME_HOME set to: $MEME_HOME" | tee -a "$(get_log_file)"
    
    # 启动bot.py并获取其真实PID
    {
        source "$VENV_PATH"
        # 在子进程中设置环境变量并启动机器人
        env MEME_HOME="$MEME_HOME" python3 "${SCRIPT_DIR}/bot.py" >> "$(get_log_file)" 2>&1 &
        local BOT_PID=$!
        echo $BOT_PID > "$PID_FILE"
        sleep 1
        if ps -p $BOT_PID >/dev/null 2>&1; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - bot.py started (PID: $BOT_PID)" | tee -a "$(get_log_file)"
            echo "$(date '+%Y-%m-%d %H:%M:%S') - Environment: MEME_HOME=$MEME_HOME" | tee -a "$(get_log_file)"
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

# 显示环境信息
show_env() {
    echo "Current Environment:"
    echo "SCRIPT_DIR: $SCRIPT_DIR"
    echo "LOG_DIR: $LOG_DIR"
    echo "VENV_PATH: $VENV_PATH"
    echo "MEME_HOME: $MEME_HOME"
    echo "Data directory exists: $(if [ -d "$MEME_HOME" ]; then echo "Yes"; else echo "No"; fi)"
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
            echo "Environment: MEME_HOME=$MEME_HOME"
            # 查看进程的环境变量
            echo "Process environment:"
            cat /proc/$BOT_PID/environ 2>/dev/null | tr '\0' '\n' | grep MEME_HOME || echo "Cannot read process environment"
        else
            echo "bot.py is not running"
            echo "MEME_HOME would be set to: $MEME_HOME"
        fi
        ;;
    env)
        show_env
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|env}"
        echo ""
        echo "Options:"
        echo "  start    - Start the bot"
        echo "  stop     - Stop the bot"
        echo "  restart  - Restart the bot"
        echo "  status   - Check bot status and environment"
        echo "  env      - Show environment configuration"
        echo ""
        echo "Environment:"
        echo "  MEME_HOME is set to: $MEME_HOME"
        exit 1
        ;;
esac