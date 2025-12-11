# Azure Web App 部署指南

## 方法一：使用 Azure Portal 部署

### 1. 建立 Azure Web App

1. 登入 [Azure Portal](https://portal.azure.com)
2. 點擊「建立資源」→「Web App」
3. 設定：
   - **訂用帳戶**：選擇你的訂閱
   - **資源群組**：新建或選擇現有
   - **名稱**：例如 `projectflow-app`
   - **發佈**：程式碼
   - **執行階段堆疊**：Python 3.12
   - **作業系統**：Linux
   - **區域**：選擇最近的區域（如 East Asia）
   - **定價方案**：建議 B1 或以上

### 2. 設定環境變數

在 Azure Portal 中，進入你的 Web App：
1. 左側選單：「設定」→「環境變數」
2. 新增應用程式設定：

```
AZURE_OPENAI_ENDPOINT=https://your-endpoint.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-model-name
SESSION_DIR=/home/site/wwwroot/session_data
LOG_LEVEL=INFO
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=true
```

### 3. 部署程式碼

**選項 A：使用 Git 部署**

```bash
# 1. 在 Azure Portal 取得 Git URL
# 設定 → 部署中心 → 本機 Git

# 2. 設定 Git remote
git remote add azure <your-git-url>

# 3. 推送程式碼
git push azure main
```

**選項 B：使用 Azure CLI**

```bash
# 1. 安裝 Azure CLI
# https://docs.microsoft.com/cli/azure/install-azure-cli

# 2. 登入
az login

# 3. 部署
az webapp up --name projectflow-app --resource-group your-rg --runtime "PYTHON:3.12" --sku B1
```

**選項 C：使用 VS Code Azure 擴充功能**

1. 安裝 Azure App Service 擴充功能
2. 右鍵專案資料夾 → Deploy to Web App
3. 選擇訂閱和 Web App

### 4. 設定啟動命令

在 Azure Portal：
1. 「設定」→「組態」
2. 「一般設定」→「啟動命令」
3. 輸入：`bash startup.sh`

### 5. 調整 Gradio 設定

確保 `projectflow_web.py` 中的 Gradio 設定正確：

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=8000,  # Azure Web App 預設 port
    share=False,
    show_error=False  # 生產環境隱藏錯誤詳情
)
```

## 方法二：使用 Docker 容器部署

### 1. 建立 Azure Container Registry (ACR)

```bash
az acr create --name projectflowacr --resource-group your-rg --sku Basic
az acr login --name projectflowacr
```

### 2. 建置並推送映像

```bash
# 標記映像
docker tag projectflow:latest projectflowacr.azurecr.io/projectflow:latest

# 推送到 ACR
docker push projectflowacr.azurecr.io/projectflow:latest
```

### 3. 建立 Web App from Container

```bash
az webapp create \
  --resource-group your-rg \
  --plan your-app-service-plan \
  --name projectflow-app \
  --deployment-container-image-name projectflowacr.azurecr.io/projectflow:latest
```

## 部署檢查清單

- [ ] `requirements.txt` 已更新
- [ ] 環境變數已設定（API keys 等）
- [ ] `WEBSITES_PORT=8000` 已設定
- [ ] 啟動命令已設定為 `bash startup.sh`
- [ ] Session 資料目錄路徑正確
- [ ] 測試地端 OpenAI endpoint 可從 Azure 訪問
- [ ] 防火牆規則允許 Azure IP

## 監控與維運

### 查看日誌

```bash
# 使用 Azure CLI
az webapp log tail --name projectflow-app --resource-group your-rg

# 或在 Portal：監視 → 記錄資料流
```

### 設定自動縮放

1. Azure Portal → Web App → 相應增加和減少
2. 設定規則（例如 CPU > 70% 時增加實例）

### 啟用 Application Insights

1. Web App → Application Insights → 開啟
2. 可監控效能、錯誤、使用量

## 成本優化

- **開發/測試**：使用 B1 方案（約 $13/月）
- **生產環境**：使用 P1V2 或以上
- **閒置時**：可調整為 F1 免費方案（有限制）

## 疑難排解

### 問題：應用程式無法啟動

檢查：
```bash
az webapp log tail --name projectflow-app --resource-group your-rg
```

常見原因：
- Python 版本不符
- 依賴安裝失敗
- 環境變數未設定
- Port 設定錯誤

### 問題：Session 資料遺失

使用 Azure File Share 持久化：
```bash
az webapp config storage-account add \
  --resource-group your-rg \
  --name projectflow-app \
  --custom-id SessionData \
  --storage-type AzureFiles \
  --share-name projectflow-sessions \
  --account-name yourstorageaccount \
  --mount-path /home/site/wwwroot/session_data
```

## 進階設定

### 使用 Azure Database 替代 Pickle

建議遷移到 Azure Database for PostgreSQL 以獲得更好的擴展性和可靠性。

### 設定 CDN

如果有大量靜態資源，可使用 Azure CDN 加速。

### 啟用 HTTPS

Azure Web App 預設提供免費 SSL，只需在自訂網域設定中啟用。
