#!/bin/bash

# Azure 部署腳本

echo "Starting deployment..."

# 安裝 Python 依賴
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 建立必要目錄
echo "Creating required directories..."
mkdir -p session_data
mkdir -p groups_data

echo "Deployment completed successfully!"
