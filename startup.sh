#!/bin/bash

# Azure Web App 啟動腳本

# 建立必要目錄
mkdir -p /home/site/wwwroot/session_data
mkdir -p /home/site/wwwroot/groups_data

# 啟動 Gradio Web 介面（預設）
if [ "$STARTUP_MODE" = "api" ]; then
    echo "Starting API server on port 8000..."
    python -m uvicorn api_server:app --host 0.0.0.0 --port 8000
else
    echo "Starting Gradio web interface on port 8000..."
    python projectflow_web.py
fi
