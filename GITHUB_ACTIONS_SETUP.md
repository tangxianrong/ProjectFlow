# GitHub Actions 自動部署設定指南

由於 GitHub 的安全限制，workflow 檔案需要在 GitHub 網頁上直接建立。

## 方法 1：在 GitHub 網頁上建立 Workflow（推薦）

### 步驟 1：在 GitHub 建立 Workflow 檔案

1. 前往你的 GitHub repo：https://github.com/tangxianrong/ProjectFlow
2. 點擊 **Actions** 標籤
3. 點擊 **"set up a workflow yourself"** 或 **"New workflow"**
4. 將以下內容貼上：

```yaml
name: Build and deploy Python app to Azure Web App

on:
  push:
    branches:
      - main
  workflow_dispatch:

env:
  AZURE_WEBAPP_NAME: projectflow-app    # 改成你的 App Service 名稱
  PYTHON_VERSION: '3.12'

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python version
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Create and start virtual environment
        run: |
          python -m venv venv
          source venv/bin/activate
      
      - name: Upgrade pip and install dependencies
        run: |
          python -m pip install --upgrade pip setuptools wheel
          pip install -r requirements.txt
        
      - name: Zip artifact for deployment
        run: |
          zip -r release.zip . -x "*.git*" "venv/*" "__pycache__/*" "*.pyc"

      - name: Upload artifact for deployment jobs
        uses: actions/upload-artifact@v4
        with:
          name: python-app
          path: release.zip

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment:
      name: 'Production'
      url: ${{ steps.deploy-to-webapp.outputs.webapp-url }}

    steps:
      - name: Download artifact from build job
        uses: actions/download-artifact@v4
        with:
          name: python-app

      - name: Unzip artifact for deployment
        run: unzip release.zip

      - name: 'Deploy to Azure Web App'
        uses: azure/webapps-deploy@v3
        id: deploy-to-webapp
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
```

5. 檔案名稱命名為：`azure-webapps-python.yml`
6. 點擊 **"Commit changes"**

### 步驟 2：設定 Azure Publish Profile

1. 前往 [Azure Portal](https://portal.azure.com)
2. 找到你的 Web App
3. 點擊 **"概觀"** → **"下載發佈設定檔"**
4. 下載 `.PublishSettings` 檔案
5. 用記事本開啟，複製所有內容

### 步驟 3：在 GitHub 設定 Secret

1. 回到 GitHub repo
2. 點擊 **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **"New repository secret"**
4. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
5. Value: 貼上剛才複製的發佈設定檔內容
6. 點擊 **"Add secret"**

### 步驟 4：修改 Workflow 中的 App 名稱

回到 Actions 頁面編輯 workflow：
```yaml
env:
  AZURE_WEBAPP_NAME: 你的app名稱    # 例如: projectflow-app-yourname
```

### 步驟 5：觸發部署

現在每次推送到 main 分支都會自動部署到 Azure！

你也可以手動觸發：
1. 前往 **Actions** 標籤
2. 選擇 workflow
3. 點擊 **"Run workflow"**

## 方法 2：使用 Azure Portal 設定 Deployment Center（更簡單）

如果不想用 GitHub Actions，可以直接在 Azure 設定：

### 步驟 1：在 Azure Portal 設定

1. 前往你的 Web App
2. 左側選單：**部署** → **部署中心**（Deployment Center）
3. 選擇 **GitHub** 作為來源
4. 登入你的 GitHub 帳號並授權
5. 選擇：
   - Organization: tangxianrong
   - Repository: ProjectFlow
   - Branch: main
6. Build provider 選擇：**GitHub Actions**
7. 點擊 **儲存**

Azure 會自動在你的 repo 建立 workflow 檔案！

### 步驟 2：確認設定

1. 回到 GitHub repo，應該會看到 `.github/workflows/` 目錄下有新的 workflow
2. 每次推送到 main 分支會自動部署

## 方法 3：使用 Azure CLI 直接部署（不需要 GitHub Actions）

如果不需要自動化，可以用 CLI 手動部署：

```bash
# 方法 A：從本地部署
az webapp up \
  --name projectflow-app-yourname \
  --resource-group projectflow-rg \
  --runtime "PYTHON:3.12"

# 方法 B：從 GitHub 部署（一次性）
az webapp deployment source config \
  --name projectflow-app-yourname \
  --resource-group projectflow-rg \
  --repo-url https://github.com/tangxianrong/ProjectFlow \
  --branch main \
  --manual-integration
```

## 推薦方式

- **最簡單**：使用 Azure Portal 的部署中心（方法 2）
- **最彈性**：手動在 GitHub 建立 workflow（方法 1）
- **最快速**：使用 Azure CLI（方法 3）

選擇最適合你的方式即可！
