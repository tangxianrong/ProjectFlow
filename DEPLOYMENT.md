# ProjectFlow 部署指南

## 目錄
- [部署前準備](#部署前準備)
- [本地開發部署](#本地開發部署)
- [生產環境部署](#生產環境部署)
- [Docker 部署](#docker-部署)
- [雲端部署](#雲端部署)
- [監控與維運](#監控與維運)
- [故障排除](#故障排除)

## 部署前準備

### 系統需求

**硬體需求**：
- CPU: 2 核心以上
- RAM: 4GB 以上（建議 8GB）
- 儲存空間: 10GB 以上
- 網路: 穩定的網際網路連線（用於 LLM API 呼叫）

**軟體需求**：
- 作業系統: Linux (Ubuntu 20.04+), macOS (10.15+), Windows 10/11
- Python: 3.12 或更高版本
- uv 或 pip
- Git

**LLM API 需求**：
- OpenAI API 金鑰，或
- Google Cloud Platform 帳號（使用 Vertex AI），或
- 自架的 OpenAI 相容 API 服務

### 環境變數設定

建立 `.env` 檔案（可從 `.env.example` 複製）：

```bash
# === LLM 設定 ===

# 使用 OpenAI 或相容 API
AZURE_OPENAI_ENDPOINT=https://api.openai.com  # 或你的端點
AZURE_OPENAI_API_KEY=sk-xxx                    # 你的 API 金鑰
AZURE_OPENAI_DEPLOYMENT=gpt-4o                 # 模型名稱

# 使用 Google Vertex AI (不設定上述變數時自動使用)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# === 應用設定 ===
SESSION_DIR=session_data           # Session 資料目錄
LOG_LEVEL=INFO                     # 日誌層級
MODULE_LOG_LEVEL=INFO              # 模組日誌層級

# === API 安全 (生產環境建議啟用) ===
# API_KEY=your-secure-api-key      # API 驗證金鑰
```

### 安全性檢查清單

- [ ] API 金鑰已安全儲存（環境變數或密鑰管理系統）
- [ ] `.env` 檔案已加入 `.gitignore`
- [ ] 生產環境已設定防火牆規則
- [ ] API 端點已啟用驗證機制
- [ ] Session 資料目錄權限設定正確
- [ ] HTTPS 已啟用（生產環境）

## 本地開發部署

### 使用 uv（推薦）

```bash
# 1. 克隆專案
git clone https://github.com/AldoTang/projectflow_agent.git
cd projectflow_agent

# 2. 安裝依賴
uv sync

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的設定

# 4. 測試設定
uv run test_dotenv_setting.py

# 5. 啟動 Web 介面
uv run projectflow_web.py

# 或啟動 API 伺服器
uv run api_server.py
```

### 使用 pip

```bash
# 1. 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 2. 安裝依賴
pip install -r requirements.txt

# 3-5. 同上
```

### Windows 快速啟動

```bash
# Web 介面
start_web.bat

# API 伺服器
start_api.bat
```

## 生產環境部署

### 使用 Systemd (Linux)

#### 1. 建立服務檔案

**Web 服務** (`/etc/systemd/system/projectflow-web.service`)：
```ini
[Unit]
Description=ProjectFlow Web Interface
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/projectflow_agent
Environment="PATH=/opt/projectflow_agent/.venv/bin"
ExecStart=/opt/projectflow_agent/.venv/bin/python projectflow_web.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**API 服務** (`/etc/systemd/system/projectflow-api.service`)：
```ini
[Unit]
Description=ProjectFlow API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/projectflow_agent
Environment="PATH=/opt/projectflow_agent/.venv/bin"
ExecStart=/opt/projectflow_agent/.venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. 啟動服務

```bash
# 重新載入 systemd
sudo systemctl daemon-reload

# 啟動服務
sudo systemctl start projectflow-web
sudo systemctl start projectflow-api

# 設定開機自動啟動
sudo systemctl enable projectflow-web
sudo systemctl enable projectflow-api

# 檢查狀態
sudo systemctl status projectflow-web
sudo systemctl status projectflow-api
```

### 使用 Nginx 反向代理

#### 安裝 Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 設定 Nginx

建立設定檔 `/etc/nginx/sites-available/projectflow`：

```nginx
# Web 介面
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Gradio 特定設定
        proxy_buffering off;
    }
}

# API 伺服器
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

啟用設定：

```bash
sudo ln -s /etc/nginx/sites-available/projectflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### HTTPS 設定（使用 Let's Encrypt）

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 取得憑證並自動設定 Nginx
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# 測試自動更新
sudo certbot renew --dry-run
```

## Docker 部署

### 建立 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 複製專案檔案
COPY pyproject.toml uv.lock ./
COPY . .

# 安裝 Python 依賴
RUN uv sync --frozen

# 建立 session 資料目錄
RUN mkdir -p session_data

# 暴露埠口
EXPOSE 7860 8000

# 預設啟動 Web 介面
CMD ["uv", "run", "projectflow_web.py"]
```

### 建立 docker-compose.yml

```yaml
version: '3.8'

services:
  projectflow-web:
    build: .
    ports:
      - "7860:7860"
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - SESSION_DIR=/app/session_data
      - LOG_LEVEL=INFO
    volumes:
      - ./session_data:/app/session_data
    restart: unless-stopped
    command: uv run projectflow_web.py

  projectflow-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
      - AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
      - AZURE_OPENAI_DEPLOYMENT=${AZURE_OPENAI_DEPLOYMENT}
      - SESSION_DIR=/app/session_data
      - LOG_LEVEL=INFO
    volumes:
      - ./session_data:/app/session_data
    restart: unless-stopped
    command: uv run uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 部署

```bash
# 建立並啟動容器
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down
```

## 雲端部署

### Google Cloud Platform

#### 使用 Cloud Run

1. **準備 Dockerfile**（同上）

2. **建立並推送映像**
```bash
# 設定專案 ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 建立映像
gcloud builds submit --tag gcr.io/$PROJECT_ID/projectflow-web

# 部署到 Cloud Run
gcloud run deploy projectflow-web \
  --image gcr.io/$PROJECT_ID/projectflow-web \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars AZURE_OPENAI_ENDPOINT=xxx,AZURE_OPENAI_API_KEY=xxx
```

#### 使用 Compute Engine

```bash
# 建立 VM
gcloud compute instances create projectflow-vm \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB

# SSH 連線
gcloud compute ssh projectflow-vm

# 在 VM 中安裝並部署（參考生產環境部署）
```

### AWS

#### 使用 EC2

1. 建立 EC2 執行個體（Ubuntu 22.04）
2. 設定安全群組：開放 80, 443, 7860, 8000 埠
3. SSH 連線並部署（參考生產環境部署）

#### 使用 ECS (Fargate)

1. 建立 ECR 儲存庫
2. 推送 Docker 映像
3. 建立 ECS 任務定義
4. 建立 ECS 服務

### Azure

#### 使用 Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name projectflow-web \
  --image your-registry/projectflow:latest \
  --dns-name-label projectflow \
  --ports 7860 \
  --environment-variables \
    AZURE_OPENAI_ENDPOINT=xxx \
    AZURE_OPENAI_API_KEY=xxx
```

## 監控與維運

### 日誌管理

#### 本地日誌

```bash
# 即時查看日誌
tail -f /var/log/projectflow/web.log
tail -f /var/log/projectflow/api.log

# 使用 journalctl (systemd)
journalctl -u projectflow-web -f
journalctl -u projectflow-api -f
```

#### 日誌輪轉

建立 `/etc/logrotate.d/projectflow`：

```
/var/log/projectflow/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload projectflow-web
        systemctl reload projectflow-api
    endscript
}
```

### 效能監控

#### 基本監控

```bash
# CPU 和記憶體使用
htop

# 磁碟使用
df -h
du -sh session_data/

# 網路連線
netstat -tulpn | grep -E '7860|8000'
```

#### 進階監控（使用 Prometheus + Grafana）

1. 安裝 Prometheus
2. 設定 metrics endpoint（需要擴充程式碼）
3. 配置 Grafana 儀表板

### 備份策略

#### Session 資料備份

```bash
# 每日備份腳本
#!/bin/bash
BACKUP_DIR=/backup/projectflow
DATE=$(date +%Y%m%d)

# 建立備份
tar -czf $BACKUP_DIR/session_data_$DATE.tar.gz session_data/

# 只保留 30 天內的備份
find $BACKUP_DIR -name "session_data_*.tar.gz" -mtime +30 -delete
```

設定 crontab：
```bash
0 2 * * * /opt/projectflow_agent/backup.sh
```

### 更新與升級

```bash
# 1. 備份當前版本
cp -r /opt/projectflow_agent /opt/projectflow_agent.backup

# 2. 拉取最新程式碼
cd /opt/projectflow_agent
git pull

# 3. 更新依賴
uv sync

# 4. 重啟服務
sudo systemctl restart projectflow-web
sudo systemctl restart projectflow-api

# 5. 檢查服務狀態
sudo systemctl status projectflow-web
sudo systemctl status projectflow-api
```

## 故障排除

### 常見問題

#### 服務無法啟動

```bash
# 檢查日誌
journalctl -u projectflow-web -n 100

# 檢查埠口占用
sudo lsof -i :7860
sudo lsof -i :8000

# 檢查環境變數
systemctl show projectflow-web | grep Environment
```

#### LLM API 連線失敗

```bash
# 測試 API 連線
curl -X POST $AZURE_OPENAI_ENDPOINT/chat/completions \
  -H "Authorization: Bearer $AZURE_OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "test"}]}'

# 檢查網路連線
ping api.openai.com
```

#### Session 資料遺失

```bash
# 檢查目錄權限
ls -la session_data/

# 檢查磁碟空間
df -h

# 恢復備份
tar -xzf /backup/projectflow/session_data_YYYYMMDD.tar.gz
```

#### 記憶體不足

```bash
# 檢查記憶體使用
free -h

# 增加 swap（臨時方案）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 效能調校

#### Gradio 設定

在 `projectflow_web.py` 中調整：

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False,
    max_threads=40,  # 增加執行緒數
    show_error=False  # 生產環境隱藏錯誤
)
```

#### Uvicorn 設定

```bash
uvicorn api_server:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --limit-concurrency 100 \
  --timeout-keep-alive 30
```

### 安全加固

1. **啟用 API 金鑰驗證**（修改 `api_server.py`）
2. **設定速率限制**
3. **啟用 CORS 限制**
4. **定期更新依賴**
5. **使用防火牆限制存取**

### 聯絡支援

如遇到無法解決的問題：
1. 查看 GitHub Issues
2. 提交新的 Issue 並附上詳細資訊
3. 聯絡專案維護者

---

**部署完成後的檢查清單**：
- [ ] 服務正常運行
- [ ] 可透過網頁或 API 存取
- [ ] LLM API 連線正常
- [ ] Session 資料正確儲存
- [ ] 日誌正常記錄
- [ ] 備份機制已設定
- [ ] 監控系統已啟用
- [ ] 安全設定已完成
