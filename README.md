# ProjectFlow

> 基於多智能體的專案導向學習輔助系統

## 專案簡介

ProjectFlow 是一個為 **Project-Based Learning (PBL)** 及 **Problem-Based Learning (PrBL)** 設計的多智能體（Multi-Agent）系統。系統透過四個智能體協作，從問題探索、進度評估、策略決策到回應生成，全方位協助學生在專案學習過程中獲得最佳支持。

### 核心特色

- 🤖 **多智能體協作**：四個 agent 串聯，分層處理學習問題與進度
- 🎯 **聚焦 SDGs**：專注於聯合國永續發展目標相關專案
- 📊 **智能評估**：自動追蹤學習進度並提供適當鷹架支援
- 🔄 **階段式引導**：從問題探索到行動規劃的完整學習歷程
- 💾 **狀態持久化**：完整保存對話記錄與專案內容
- 🌐 **友善介面**：提供 Web 介面與 API 兩種使用方式
- 👥 **多組支援**：支援多組學生同時使用，各組資料完全獨立
- 🎨 **主題客製化**：教師可針對特定課程客製化 agent 行為

### 系統架構

```
用戶 → Web/API → Decision Agent → Response Agent → 回應
                      ↓
                  (背景執行)
                      ↓
              Summary Agent → Score Agent → 狀態更新
```

**四個智能體分工**：
1. **Summary Agent**：摘要對話，維護專案內容與學習記錄
2. **Score Agent**：評估學習表現，追蹤各階段目標達成度
3. **Decision Agent**：分析進度，決定下一步引導策略
4. **Response Agent**：生成友善且有效的對話回應

## 快速開始

### 環境需求

- Python 3.12 或以上版本
- [uv](https://github.com/astral-sh/uv) (推薦) 或 pip
- OpenAI API 金鑰或 Google Vertex AI 憑證

### 安裝步驟

#### 1. 克隆專案
```bash
git clone https://github.com/AldoTang/projectflow_agent.git
cd projectflow_agent
```

#### 2. 安裝 uv (推薦)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. 安裝依賴
```bash
uv sync
```

#### 4. 設定環境變數
```bash
# 複製環境變數範例檔案
cp .env.example .env

# 編輯 .env 填入你的 API 設定
# nano .env 或使用你喜歡的編輯器
```

環境變數說明：
```bash
# OpenAI 或相容 API (地端部署)
AZURE_OPENAI_ENDPOINT=https://your-endpoint.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=your-model-name

# 或使用 Google Vertex AI (不設定上述變數即自動使用)
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

#### 5. 測試設定
```bash
uv run test_dotenv_setting.py
```

#### 6. (可選) 設定課程主題
教師可以使用主題設定工具來客製化 agent 行為：
```bash
uv run theme_setter.py
```

#### 7. 啟動服務

**啟動 Web 介面** (推薦新手使用)：
```bash
uv run projectflow_web.py
# 開啟瀏覽器訪問 http://localhost:7860
```

**或啟動 API 伺服器**：
```bash
uv run api_server.py
# API 文件：http://localhost:8000/docs
```

**Windows 使用者可使用快速啟動腳本**：
```bash
start_web.bat    # 啟動 Web 介面
start_api.bat    # 啟動 API 伺服器
```

## 使用方式

### Web 介面使用

1. 啟動後在瀏覽器開啟 http://localhost:7860
2. 在輸入框中描述你想解決的問題或專案構想
3. 系統會引導你逐步完成專案規劃
4. 可隨時下載專案計畫書和對話記錄

### API 使用

詳細 API 文件請訪問：http://localhost:8000/docs

範例請求：
```bash
curl -X POST http://localhost:8000/background_update \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "prev_ai_prompt": "歡迎訊息",
    "user_prompt": "我想解決社區的空氣污染問題"
  }'
```

## 專案結構

```
projectflow_agent/
├── projectflow_graph.py      # 核心工作流程與智能體定義
├── projectflow_web.py         # Gradio Web 介面
├── api_server.py              # FastAPI 後端服務
├── background_tool.py         # 背景工作流程工具
├── test_dotenv_setting.py     # 環境設定測試
├── theme_setter.py            # 主題設定工具
├── prompts/                   # Prompt 模板與設定
│   ├── __init__.py           # 所有 Agent 的 Prompt
│   ├── doc_struct.py         # 文檔結構定義
│   └── stage_setting.yaml    # 學習階段設定
├── dev_env_docker/           # Docker 開發環境
├── session_data/             # Session 資料儲存 (自動建立)
├── groups_data/              # 多組資料儲存 (自動建立)
├── pyproject.toml            # 專案依賴定義
├── .env.example              # 環境變數範例
└── README.md                 # 本文件
```

## 學習階段

系統預設提供兩個學習階段：

**階段一：PBL 問題探索**
- 建立問題意識
- 描述觀察到的現象
- 連結 SDGs 目標

**階段二：PBL 探索行動決定**
- 提出具體行動方案
- 評估行動的可行性
- 規劃所需資源

可透過修改 `prompts/stage_setting.yaml` 自訂更多階段。

## 技術棧

- **LangGraph** - 工作流程編排
- **LangChain** - LLM 整合
- **FastAPI** - API 服務框架
- **Gradio** - Web 介面框架
- **OpenAI / Vertex AI** - 大型語言模型
- **uv** - Python 套件管理

## 貢獻指南

歡迎貢獻！請參考以下步驟：

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

請確保：
- 遵循現有程式碼風格
- 添加適當的註解
- 更新相關文檔
- 通過所有測試

## 常見問題

**Q: 支援哪些 LLM？**  
A: 支援 OpenAI API、OpenAI 相容 API (如地端部署模型)，以及 Google Vertex AI。

**Q: 可以離線使用嗎？**  
A: 需要連接 LLM API，但可以使用地端部署的模型。

**Q: 如何新增學習階段？**  
A: 編輯 `prompts/stage_setting.yaml` 即可新增自訂階段。

**Q: Session 資料儲存在哪裡？**  
A: 預設儲存在 `session_data/` 目錄，可透過環境變數 `SESSION_DIR` 自訂。

**Q: 如何設定課程主題？**  
A: 執行 `uv run theme_setter.py` 並按照提示設定。

## 授權

本專案採用 MIT 授權條款。

## 聯絡方式

如有問題或建議，歡迎：
- 📧 提交 GitHub Issue
- 💬 發起 GitHub Discussion
- 👥 聯絡專案維護者

---

**專案作者**：[AldoTang](https://github.com/AldoTang)  
**最後更新**：2025-12
