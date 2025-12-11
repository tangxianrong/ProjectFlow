#!/bin/bash

# Azure 部署腳本

echo "Starting deployment..."

# 更新 pip 和 setuptools
echo "Upgrading pip and setuptools..."
python -m pip install --upgrade pip setuptools wheel

# 安裝 Python 依賴
echo "Installing Python dependencies..."
pip install -r requirements.txt --no-cache-dir

# 建立必要目錄
echo "Creating required directories..."
mkdir -p session_data
mkdir -p groups_data

echo "Deployment completed successfully!"
