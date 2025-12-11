# ProjectFlow Web 應用部署指南

本指南提供詳細的 ProjectFlow 系統部署流程，適用於各種部署環境。

## 目錄

- [快速開始](#快速開始)
- [使用 Docker 部署（推薦）](#使用-docker-部署推薦)
- [傳統部署方式](#傳統部署方式)
- [雲端平台部署](#雲端平台部署)
- [環境變數設定](#環境變數設定)
- [常見問題](#常見問題)

---

## 快速開始

### 前置需求

- **Docker & Docker Compose**（推薦）或
- **Python 3.12+** 與 **uv** 或 **pip**
- **LLM API 金鑰**（OpenAI 或 Google Vertex AI）

### 30 秒快速部署

```bash
# 1. 克隆專案
git clone https://github.com/AldoTang/projectflow_agent.git
cd projectflow_agent

# 2. 設定環境變數
cp .env.example .env
# 編輯 .env 填入你的 API 金鑰

# 3. 使用 Docker Compose 啟動
docker-compose up -d

# 完成！
# Web 介面：http://localhost:7860
# API 文件：http://localhost:8000/docs
```

---

## 使用 Docker 部署（推薦）

### 方式一：使用 Docker Compose（最簡單）

#### 1. 準備環境變數

建立 `.env` 檔案：

```bash
# LLM API 設定
AZURE_OPENAI_ENDPOINT=https://api.openai.com
AZURE_OPENAI_API_KEY=sk-your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# 或使用 Google Vertex AI
# GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# 應用設定
LOG_LEVEL=INFO
MODULE_LOG_LEVEL=INFO
```

#### 2. 啟動服務

```bash
# 啟動所有服務（Web 介面 + API）
docker-compose up -d

# 查看日誌
docker-compose logs -f

# 只啟動 Web 介面
docker-compose up -d projectflow-web

# 只啟動 API 服務
docker-compose up -d projectflow-api
```

#### 3. 訪問服務

- **Web 介面**：http://localhost:7860
- **API 文件**：http://localhost:8000/docs
- **API Swagger UI**：http://localhost:8000/redoc

#### 4. 停止服務

```bash
# 停止服務
docker-compose down

# 停止並刪除資料（謹慎使用！）
docker-compose down -v
```

### 方式二：使用 Docker 命令

#### 建立映像

```bash
docker build -t projectflow:latest .
```

#### 啟動 Web 介面

```bash
docker run -d \
  --name projectflow-web \
  -p 7860:7860 \
  -e AZURE_OPENAI_ENDPOINT=https://api.openai.com \
  -e AZURE_OPENAI_API_KEY=sk-your-key \
  -e AZURE_OPENAI_DEPLOYMENT=gpt-4o \
  -v $(pwd)/session_data:/app/session_data \
  projectflow:latest
```

#### 啟動 API 服務

```bash
docker run -d \
  --name projectflow-api \
  -p 8000:8000 \
  -e AZURE_OPENAI_ENDPOINT=https://api.openai.com \
  -e AZURE_OPENAI_API_KEY=sk-your-key \
  -e AZURE_OPENAI_DEPLOYMENT=gpt-4o \
  -v $(pwd)/session_data:/app/session_data \
  projectflow:latest \
  uv run uvicorn api_server:app --host 0.0.0.0 --port 8000
```

---

## 傳統部署方式

### 使用 uv（推薦）

```bash
# 1. 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安裝依賴
uv sync

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env

# 4. 啟動 Web 介面
uv run projectflow_web.py

# 或啟動 API 服務
uv run api_server.py
```

### 使用 pip

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定環境變數
cp .env.example .env
# 編輯 .env

# 4. 啟動服務
python projectflow_web.py
# 或
python api_server.py
```

### 使用 Systemd（Linux 生產環境）

建立服務檔案 `/etc/systemd/system/projectflow-web.service`：

```ini
[Unit]
Description=ProjectFlow Web Interface
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/projectflow_agent
Environment="PATH=/opt/projectflow_agent/.venv/bin"
EnvironmentFile=/opt/projectflow_agent/.env
ExecStart=/opt/projectflow_agent/.venv/bin/python projectflow_web.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl enable projectflow-web
sudo systemctl start projectflow-web
sudo systemctl status projectflow-web
```

---

## 雲端平台部署

### Heroku

#### 1. 準備檔案

建立 `Procfile`：

```
web: uvicorn api_server:app --host 0.0.0.0 --port $PORT
```

建立 `runtime.txt`：

```
python-3.12.0
```

#### 2. 部署

```bash
# 登入 Heroku
heroku login

# 建立應用
heroku create your-app-name

# 設定環境變數
heroku config:set AZURE_OPENAI_ENDPOINT=https://api.openai.com
heroku config:set AZURE_OPENAI_API_KEY=sk-your-key
heroku config:set AZURE_OPENAI_DEPLOYMENT=gpt-4o

# 部署
git push heroku main

# 開啟應用
heroku open
```

### Google Cloud Run

```bash
# 設定專案
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# 建立並推送映像
gcloud builds submit --tag gcr.io/$PROJECT_ID/projectflow

# 部署
gcloud run deploy projectflow \
  --image gcr.io/$PROJECT_ID/projectflow \
  --platform managed \
  --region asia-east1 \
  --allow-unauthenticated \
  --set-env-vars AZURE_OPENAI_ENDPOINT=xxx,AZURE_OPENAI_API_KEY=xxx \
  --port 7860
```

### AWS Elastic Beanstalk

```bash
# 安裝 EB CLI
pip install awsebcli

# 初始化
eb init -p docker projectflow

# 建立環境並部署
eb create projectflow-env

# 設定環境變數
eb setenv AZURE_OPENAI_ENDPOINT=xxx AZURE_OPENAI_API_KEY=xxx

# 開啟應用
eb open
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name projectflow \
  --image your-registry/projectflow:latest \
  --dns-name-label projectflow \
  --ports 7860 8000 \
  --environment-variables \
    AZURE_OPENAI_ENDPOINT=xxx \
    AZURE_OPENAI_API_KEY=xxx \
    AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### Render.com

1. 連接 GitHub 儲存庫
2. 選擇 "Web Service"
3. 設定：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python projectflow_web.py`
4. 新增環境變數
5. 部署

### Railway.app

1. 連接 GitHub 儲存庫
2. 自動偵測並部署
3. 在設定中新增環境變數
4. 完成！

---

## 環境變數設定

### 必要變數

| 變數名稱 | 說明 | 範例 |
|---------|------|------|
| `AZURE_OPENAI_ENDPOINT` | OpenAI API 端點 | `https://api.openai.com` |
| `AZURE_OPENAI_API_KEY` | OpenAI API 金鑰 | `sk-...` |
| `AZURE_OPENAI_DEPLOYMENT` | 模型名稱 | `gpt-4o` |

### 可選變數

| 變數名稱 | 說明 | 預設值 |
|---------|------|--------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Vertex AI 憑證路徑 | - |
| `SESSION_DIR` | Session 資料目錄 | `session_data` |
| `LOG_LEVEL` | 日誌層級 | `INFO` |
| `MODULE_LOG_LEVEL` | 模組日誌層級 | `INFO` |

### Google Vertex AI 設定

如果使用 Google Vertex AI 而非 OpenAI：

1. 不設定 `AZURE_OPENAI_*` 變數
2. 設定 `GOOGLE_APPLICATION_CREDENTIALS` 指向服務帳號金鑰 JSON 檔案
3. 確保有 Vertex AI API 的存取權限

---

## 使用反向代理（Nginx）

### 安裝 Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 設定 Nginx

建立 `/etc/nginx/sites-available/projectflow`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Web 介面
    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_buffering off;
    }
}

# API 服務（子網域）
server {
    listen 80;
    server_name api.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

啟用設定：

```bash
sudo ln -s /etc/nginx/sites-available/projectflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 設定 HTTPS（Let's Encrypt）

```bash
# 安裝 Certbot
sudo apt install certbot python3-certbot-nginx

# 取得憑證
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# 測試自動更新
sudo certbot renew --dry-run
```

---

## 健康檢查與監控

### 健康檢查端點

```bash
# Web 介面健康檢查
curl http://localhost:7860/

# API 健康檢查
curl http://localhost:8000/docs
```

### 日誌查看

```bash
# Docker
docker-compose logs -f projectflow-web
docker-compose logs -f projectflow-api

# Systemd
journalctl -u projectflow-web -f
journalctl -u projectflow-api -f
```

---

## 常見問題

### Q: 如何更新到最新版本？

**Docker 部署：**
```bash
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**傳統部署：**
```bash
git pull
uv sync  # 或 pip install -r requirements.txt
sudo systemctl restart projectflow-web
```

### Q: 如何備份資料？

```bash
# 備份 session 資料
tar -czf backup-$(date +%Y%m%d).tar.gz session_data/ groups_data/

# 恢復備份
tar -xzf backup-20231201.tar.gz
```

### Q: 服務無法啟動怎麼辦？

1. 檢查日誌：`docker-compose logs` 或 `journalctl -u projectflow-web`
2. 確認環境變數設定正確
3. 檢查埠口是否被占用：`lsof -i :7860`
4. 確認 LLM API 金鑰有效

### Q: 如何限制訪問？

使用 Nginx 設定 HTTP Basic Auth：

```bash
# 建立密碼檔案
sudo htpasswd -c /etc/nginx/.htpasswd username

# 在 Nginx 設定中加入
location / {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://127.0.0.1:7860;
}
```

### Q: 如何擴展到多個實例？

使用 Docker Swarm 或 Kubernetes 進行容器編排：

**Docker Swarm 範例：**
```bash
docker swarm init
docker stack deploy -c docker-compose.yml projectflow
docker service scale projectflow_projectflow-web=3
```

---

## 效能調校建議

### 生產環境設定

1. **使用 Gunicorn + Uvicorn workers（API）**
   ```bash
   gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. **調整 Gradio 設定**
   ```python
   demo.launch(
       server_name="0.0.0.0",
       server_port=7860,
       max_threads=40,
       show_error=False
   )
   ```

3. **啟用資料庫快取**（如使用 Redis）

4. **設定 CDN**（靜態資源）

---

## 安全建議

- ✅ 使用 HTTPS（Let's Encrypt）
- ✅ 設定防火牆規則
- ✅ 定期更新依賴套件
- ✅ 使用環境變數管理機密資訊
- ✅ 啟用 API 金鑰驗證
- ✅ 限制 CORS 來源
- ✅ 定期備份資料

---

## 支援與回饋

如有問題或建議：
- 📧 提交 [GitHub Issue](https://github.com/AldoTang/projectflow_agent/issues)
- 💬 參與 [GitHub Discussions](https://github.com/AldoTang/projectflow_agent/discussions)

---

**祝您部署順利！** 🚀
