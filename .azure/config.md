# Azure App Service 配置

## 運行時設定
- Python 版本：3.12
- 作業系統：Linux
- 啟動命令：bash startup.sh

## 必需的應用程式設定（環境變數）

```bash
# LLM 設定
AZURE_OPENAI_ENDPOINT=https://your-endpoint.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-model-name

# Azure Web App 設定
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true

# Session 設定
SESSION_DIR=/home/site/wwwroot/session_data

# 日誌設定
LOG_LEVEL=INFO
MODULE_LOG_LEVEL=INFO
ENV=production

# 可選：啟動 API 模式而非 Web 介面
# STARTUP_MODE=api
```

## 自動部署設定

### 方法 1：GitHub Actions（推薦）

在 GitHub repo 設定中啟用 Actions，Azure 會自動建立 workflow。

### 方法 2：Azure CLI

```bash
# 設定環境變數
az webapp config appsettings set \
  --name your-app-name \
  --resource-group your-rg \
  --settings @appsettings.json
```

建立 `appsettings.json`：
```json
[
  {
    "name": "AZURE_OPENAI_ENDPOINT",
    "value": "https://your-endpoint.com/",
    "slotSetting": false
  },
  {
    "name": "AZURE_OPENAI_API_KEY",
    "value": "your-api-key",
    "slotSetting": false
  },
  {
    "name": "AZURE_OPENAI_DEPLOYMENT",
    "value": "your-model-name",
    "slotSetting": false
  },
  {
    "name": "WEBSITES_PORT",
    "value": "8000",
    "slotSetting": false
  },
  {
    "name": "SCM_DO_BUILD_DURING_DEPLOYMENT",
    "value": "true",
    "slotSetting": false
  }
]
```

### 方法 3：Azure Portal

1. 前往 App Service → 設定 → 環境變數
2. 新增上述所有變數
3. 儲存並重啟應用程式

## 建置設定

確保以下檔案存在：
- `requirements.txt` - Python 依賴（使用版本範圍，不固定版本）
- `runtime.txt` - Python 版本（python-3.12）
- `startup.sh` - 啟動腳本
- `deploy.sh` - 部署腳本（由 .deployment 調用）

## 疑難排解

### 建置失敗

查看建置日誌：
```bash
az webapp log deployment show --name your-app-name --resource-group your-rg
```

常見問題：
1. **setuptools 錯誤** → deploy.sh 已包含 `pip install --upgrade setuptools`
2. **版本衝突** → requirements.txt 使用版本範圍（>=）而非固定版本
3. **平台特定套件** → 移除 Windows 特定套件

### 運行時錯誤

查看應用程式日誌：
```bash
az webapp log tail --name your-app-name --resource-group your-rg
```

## 效能優化

### 使用 Gunicorn（生產環境）

已在 startup.sh 中配置：
- 2 個 worker processes
- Uvicorn worker class（支援 async）
- 120 秒 timeout

### 冷啟動優化

- 使用 Always On（付費方案）
- 預熱端點：設定健康檢查路徑

## 監控

### 啟用 Application Insights

```bash
az monitor app-insights component create \
  --app your-insights-name \
  --location eastasia \
  --resource-group your-rg
```

### 設定警報

- CPU 使用率 > 80%
- 記憶體使用率 > 90%
- HTTP 5xx 錯誤
- 回應時間 > 5 秒
