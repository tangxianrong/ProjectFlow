#!/bin/bash

# Azure Web App 啟動腳本

echo "Starting ProjectFlow application..."

# 建立必要目錄
mkdir -p /home/site/wwwroot/session_data
mkdir -p /home/site/wwwroot/groups_data

# 設定 Python 路徑
export PYTHONPATH=/home/site/wwwroot:$PYTHONPATH

# 根據環境變數決定啟動模式
if [ "$STARTUP_MODE" = "api" ]; then
    echo "Starting API server on port ${WEBSITES_PORT:-8000}..."
    gunicorn api_server:app \
        --workers 2 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:${WEBSITES_PORT:-8000} \
        --timeout 120 \
        --access-logfile - \
        --error-logfile -
else
    echo "Starting Gradio web interface on port ${WEBSITES_PORT:-8000}..."
    python projectflow_web.py
fi
