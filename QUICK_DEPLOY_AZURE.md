# Azure Web App 快速部署指南

## 前置準備

1. Azure 帳號（免費試用：https://azure.microsoft.com/free/）
2. Azure CLI（下載：https://aka.ms/installazurecli）
3. 確保你的地端 OpenAI endpoint 可從 Azure 訪問
4. **重要**：已更新 `requirements.txt` 為跨平台相容版本

## 檔案說明

本專案已包含 Azure 部署所需的所有檔案：
- ✅ `requirements.txt` - 跨平台 Python 依賴（使用版本範圍）
- ✅ `runtime.txt` - Python 3.12
- ✅ `startup.sh` - Linux 啟動腳本
- ✅ `deploy.sh` - 部署時執行的腳本
- ✅ `.deployment` - 部署配置
- ✅ `.github/workflows/azure-webapps-python.yml` - GitHub Actions（可選）

## 最快 5 步驟部署

### 步驟 1：登入 Azure

```bash
az login
```

### 步驟 2：建立資源群組

```bash
az group create --name projectflow-rg --location eastasia
```

### 步驟 3：一鍵部署

```bash
az webapp up \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg \
  --runtime "PYTHON:3.12" \
  --sku B1 \
  --location eastasia
```

### 步驟 4：設定環境變數

```bash
az webapp config appsettings set \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg \
  --settings \
    AZURE_OPENAI_ENDPOINT="https://928c30333ca8.ngrok-free.app/" \
    AZURE_OPENAI_API_KEY="will_way" \
    AZURE_OPENAI_DEPLOYMENT="openai/gpt-oss-120b" \
    WEBSITES_PORT="8000" \
    SESSION_DIR="/home/site/wwwroot/session_data" \
    ENV="production"
```

### 步驟 5：設定啟動命令

```bash
az webapp config set \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg \
  --startup-file "bash startup.sh"
```

## 訪問應用程式

部署完成後，訪問：
```
https://projectflow-app-<你的名字>.azurewebsites.net
```

## 查看日誌

```bash
az webapp log tail \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg
```

## 更新程式碼

修改後重新部署：
```bash
az webapp up \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg
```

## 重要注意事項

### 1. 地端 OpenAI Endpoint

如果你的 OpenAI endpoint 是 ngrok（`https://928c30333ca8.ngrok-free.app/`），需要注意：

- ⚠️ ngrok 免費版 URL 會定期改變
- ⚠️ 需要確保 Azure 可以訪問你的 ngrok URL
- 💡 建議：使用穩定的公開 endpoint 或 Azure 內部服務

### 2. Session 資料持久化

預設 session 資料會在應用程式重啟時遺失。生產環境建議：

**選項 A：使用 Azure Files**

```bash
# 建立儲存體帳戶
az storage account create \
  --name projectflowstorage \
  --resource-group projectflow-rg \
  --location eastasia \
  --sku Standard_LRS

# 建立檔案共用
az storage share create \
  --name sessions \
  --account-name projectflowstorage

# 掛載到 Web App
az webapp config storage-account add \
  --name projectflow-app-<你的名字> \
  --resource-group projectflow-rg \
  --custom-id SessionData \
  --storage-type AzureFiles \
  --share-name sessions \
  --account-name projectflowstorage \
  --mount-path /home/site/wwwroot/session_data
```

**選項 B：使用 Azure Database**（長期建議）

考慮將 pickle 改為 PostgreSQL 或 Cosmos DB。

### 3. 成本估算

- **B1 方案**：約 NT$ 400/月
- **加上儲存體**：約 NT$ 50/月
- **總計**：約 NT$ 450/月

免費額度（F1）：
- 可用但有限制（1 GB RAM，60 分鐘/天 CPU 時間）

### 4. 監控與告警

啟用 Application Insights：
```bash
az monitor app-insights component create \
  --app projectflow-insights \
  --location eastasia \
  --resource-group projectflow-rg \
  --application-type web
```

## 疑難排解

### 應用程式無法啟動

1. 檢查日誌：
```bash
az webapp log tail --name projectflow-app-<你的名字> --resource-group projectflow-rg
```

2. 常見問題：
   - Python 版本不符 → 檢查 `runtime.txt`
   - 依賴安裝失敗 → 檢查 `requirements.txt`
   - Port 設定錯誤 → 確認 `WEBSITES_PORT=8000`

### Gradio 介面無法載入

確認：
```python
# projectflow_web.py
demo.launch(
    server_name="0.0.0.0",  # 必須是 0.0.0.0
    server_port=port,        # 使用環境變數
    share=False              # Azure 上不需要 share
)
```

### 地端模型連線失敗

檢查：
1. ngrok URL 是否仍然有效
2. Azure Web App 可否訪問你的 endpoint（防火牆設定）
3. API key 是否正確

## 刪除資源（停止計費）

```bash
az group delete --name projectflow-rg --yes
```

## 下一步

詳細部署文檔請參考：[AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)
