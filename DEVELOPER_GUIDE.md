# ProjectFlow 開發者指南

## 目錄
- [快速開始](#快速開始)
- [開發環境設定](#開發環境設定)
- [專案結構](#專案結構)
- [開發流程](#開發流程)
- [程式碼規範](#程式碼規範)
- [測試](#測試)
- [除錯技巧](#除錯技巧)
- [常見問題](#常見問題)

## 快速開始

### 環境需求
- Python 3.12 或以上
- uv (推薦) 或 pip
- Git
- 有效的 LLM API 金鑰 (OpenAI 或 Google Vertex AI)

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/AldoTang/projectflow_agent.git
cd projectflow_agent
```

2. **安裝 uv (推薦)**
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **安裝依賴**
```bash
uv sync
```

4. **設定環境變數**
```bash
cp .env.example .env
# 編輯 .env 填入你的 API 金鑰
```

5. **測試安裝**
```bash
uv run test_dotenv_setting.py
```

6. **啟動服務**

啟動 Web 介面：
```bash
uv run projectflow_web.py
# 開啟瀏覽器訪問 http://localhost:7860
```

或啟動 API 伺服器：
```bash
uv run api_server.py
# API 文件：http://localhost:8000/docs
```

## 開發環境設定

### 使用 IDE

**VS Code 推薦設定** (`.vscode/settings.json`)：
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.analysis.typeCheckingMode": "basic"
}
```

**PyCharm 設定**：
1. File → Settings → Project → Python Interpreter
2. 選擇 uv 建立的虛擬環境 (`.venv`)
3. 啟用 Type Checker

### 環境變數說明

建立 `.env` 檔案並設定以下變數：

```bash
# === LLM 設定 ===

# 選項 1: 使用 OpenAI 相容 API (地端或雲端)
AZURE_OPENAI_ENDPOINT=http://localhost:8080  # API 端點
AZURE_OPENAI_API_KEY=your-api-key-here       # API 金鑰
AZURE_OPENAI_DEPLOYMENT=gpt-4o               # 模型名稱

# 選項 2: 使用 Google Vertex AI
# (不設定 AZURE_* 變數即自動使用 Vertex AI)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# === 應用設定 ===
SESSION_DIR=session_data      # Session 資料儲存目錄
LOG_LEVEL=INFO                # 日誌層級: DEBUG, INFO, WARNING, ERROR
MODULE_LOG_LEVEL=INFO         # 模組日誌層級
```

### Docker 開發環境

```bash
cd dev_env_docker
docker build -t projectflow-dev .
docker run -d -p 8000:8000 -p 22:22 -v $(pwd):/app projectflow-dev
```

SSH 連線：
```bash
ssh devuser@localhost
# 密碼：devpassword
```

## 專案結構

```
projectflow_agent/
├── projectflow_graph.py      # 核心工作流程與智能體定義
├── projectflow_web.py         # Gradio Web 介面
├── api_server.py              # FastAPI 後端服務
├── background_tool.py         # 背景工作流程工具
├── test_dotenv_setting.py     # 環境設定測試
├── prompts/                   # Prompt 模板與設定
│   ├── __init__.py           # Prompt 載入與定義
│   ├── doc_struct.py         # 文檔結構定義
│   └── stage_setting.yaml    # 學習階段設定
├── dev_env_docker/           # Docker 開發環境
│   └── dockerfile
├── session_data/             # Session 資料儲存 (gitignore)
├── pyproject.toml            # 專案依賴定義
├── uv.lock                   # 依賴鎖定檔
├── .env                      # 環境變數 (gitignore)
├── .env.example              # 環境變數範例
└── README.md                 # 專案說明
```

### 核心檔案說明

#### `projectflow_graph.py`
專案核心，包含：
- `AgentState`：狀態定義
- 四個智能體函式：`summary_agent`, `score_agent`, `decision_agent`, `response_agent`
- 工作流程定義：`main_graph`, `background_graph`
- LLM 初始化邏輯
- Token 統計功能

#### `prompts/__init__.py`
定義所有智能體的 prompt 模板：
- `SUMMARY_AGENT_PROMPT`
- `SCORE_AGENT_PROMPT`
- `DECISION_AGENT_PROMPT`
- `RESPONSE_AGENT_PROMPT`

#### `background_tool.py`
模組化的背景更新工具：
- Session 狀態管理
- 背景 workflow 執行
- 狀態持久化

## 開發流程

### 新增功能

1. **建立功能分支**
```bash
git checkout -b feature/your-feature-name
```

2. **編寫程式碼**
- 遵循現有程式碼風格
- 添加適當的註解
- 更新相關文檔

3. **測試**
```bash
# 執行基本測試
uv run test_dotenv_setting.py

# 手動測試對話流程
uv run projectflow_web.py
```

4. **提交變更**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 修改 Prompt

1. 編輯 `prompts/__init__.py` 中對應的 prompt 模板
2. 測試新 prompt 的效果
3. 記錄改動原因與預期效果

**Prompt 編寫原則**：
- 明確的角色定義
- 清晰的任務說明
- 具體的輸出格式
- 完整的範例
- 必要的限制條件

### 新增學習階段

1. **編輯 `prompts/stage_setting.yaml`**
```yaml
stage_3:
  sequence: 3
  name: 階段三 行動執行與反思
  main_issue: 用戶是否完成行動並進行反思
  description: 引導學生執行計畫並記錄過程
  score_list:
    - 行動執行的完整性
    - 資料記錄的詳實度
    - 反思的深度
```

2. **更新相關 Prompt**
- 在 `SUMMARY_AGENT_PROMPT` 中說明新階段
- 在 `DECISION_AGENT_PROMPT` 中定義階段轉換邏輯

3. **測試階段轉換**

### 新增或更換 LLM

**方案 1：OpenAI 相容 API**
```python
# 在 projectflow_graph.py 中
llm = ChatOpenAI(
    model="your-model-name",
    base_url="https://your-endpoint/v1",
    api_key=os.getenv("YOUR_API_KEY"),
    temperature=0.7,
    timeout=60,
    max_retries=2
)
```

**方案 2：其他 LangChain 支援的 LLM**
```python
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-3-opus-20240229",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    temperature=0
)
```

## 程式碼規範

### Python 風格指南

1. **遵循 PEP 8**
2. **使用型別提示**
```python
def process_message(message: str, session_id: str) -> dict:
    ...
```

3. **函式命名**
- 使用小寫加底線：`load_state()`, `update_progress()`
- 類別使用駝峰式：`AgentState`, `BackgroundTool`

4. **註解規範**
```python
def summary_agent(state: AgentState) -> AgentState:
    """
    摘要智能體：維護專案內容與學習歷程記錄
    
    Args:
        state: 當前 agent 狀態
        
    Returns:
        更新後的狀態
    """
    ...
```

5. **日誌記錄**
```python
logger.info(f"[function_name] 重要資訊")
logger.debug(f"[function_name] 除錯資訊")
logger.warning(f"[function_name] 警告訊息")
logger.error(f"[function_name] 錯誤訊息")
```

### Git Commit 規範

使用 Conventional Commits：
- `feat:` 新功能
- `fix:` 錯誤修正
- `docs:` 文檔更新
- `style:` 程式碼格式調整
- `refactor:` 重構
- `test:` 測試相關
- `chore:` 建置或輔助工具變動

範例：
```
feat: add export to PDF functionality
fix: resolve session state synchronization issue
docs: update API documentation
```

## 測試

### 單元測試 (建議新增)

建立 `tests/` 目錄並使用 pytest：

```python
# tests/test_agents.py
import pytest
from projectflow_graph import summary_agent, AgentState

def test_summary_agent_updates_project_content():
    state = {
        "messages": [...],
        "project_content": "",
        ...
    }
    result = summary_agent(state)
    assert "project_content" in result
```

執行測試：
```bash
uv run pytest tests/
```

### 整合測試

**測試 Web 介面**：
```bash
uv run projectflow_web.py
# 手動測試對話流程
```

**測試 API**：
```bash
# 終端 1: 啟動 API
uv run api_server.py

# 終端 2: 測試請求
curl -X POST http://localhost:8000/background_update \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "prev_ai_prompt": "歡迎",
    "user_prompt": "我想解決空氣污染問題"
  }'
```

### 測試 LLM 連線

```bash
uv run test_dotenv_setting.py
```

## 除錯技巧

### 啟用詳細日誌

```bash
# 設定環境變數
export LOG_LEVEL=DEBUG
export MODULE_LOG_LEVEL=DEBUG

# 或在 .env 檔案中設定
LOG_LEVEL=DEBUG
MODULE_LOG_LEVEL=DEBUG
```

### 檢查狀態檔案

```python
import pickle

with open("session_data/state_{session_id}.pkl", "rb") as f:
    state = pickle.load(f)
    print(state.keys())
    print(state["project_content"])
```

### 追蹤 Token 使用

在 `projectflow_graph.py` 中已內建 Token 統計：

```python
from projectflow_graph import TOKEN_STATS

print(TOKEN_STATS)
# {
#   'summary_agent': {'input': 1234, 'output': 567},
#   'score_agent': {'input': 890, 'output': 234},
#   ...
# }
```

### LangGraph 除錯

```python
# 啟用 LangChain 除錯日誌
import logging
logging.getLogger("langchain").setLevel("DEBUG")
logging.getLogger("httpx").setLevel("DEBUG")
```

### 常見錯誤排查

**JSON 解析失敗**：
- 檢查 LLM 輸出格式
- 使用 `extract_first_json_list()` 容錯處理
- 調整 prompt 明確要求 JSON 格式

**Session 狀態遺失**：
- 確認 `session_data/` 目錄存在
- 檢查檔案權限
- 驗證 session_id 一致性

**LLM 請求超時**：
- 增加 `timeout` 參數
- 檢查網路連線
- 驗證 API 端點可用性

## 常見問題

### Q: 如何切換不同的 LLM？
A: 修改 `.env` 中的 API 設定，或直接編輯 `projectflow_graph.py` 中的 LLM 初始化邏輯。

### Q: 如何重設對話狀態？
A: 刪除對應的 `session_data/state_{session_id}.pkl` 檔案。

### Q: 如何調整智能體行為？
A: 修改 `prompts/__init__.py` 中對應的 prompt 模板。

### Q: 為什麼背景更新沒有立即生效？
A: 背景工作流程是異步執行的，需要等待執行緒完成並寫入檔案。在下次載入狀態時會讀取更新後的內容。

### Q: 如何增加評分項目？
A: 編輯 `prompts/stage_setting.yaml` 中對應階段的 `score_list`。

### Q: 可以使用其他資料庫嗎？
A: 可以，需要修改 `background_tool.py` 中的狀態持久化邏輯，從 Pickle 改為資料庫操作。

## 效能優化建議

1. **限制對話歷史長度**：避免過長的 context 導致 token 浪費
2. **使用較小的模型**：開發階段可使用 GPT-3.5 或 Gemini Flash
3. **快取常用回應**：對於常見問題可建立快取機制
4. **批次處理**：如果有多個 session，可考慮批次呼叫 LLM

## 貢獻指南

歡迎提交 Pull Request！請確保：

1. 程式碼符合風格規範
2. 添加必要的註解和文檔
3. 通過所有測試
4. 更新 CHANGELOG（如有）
5. 在 PR 中清楚說明變更內容

## 參考資源

- [LangGraph 文檔](https://langchain-ai.github.io/langgraph/)
- [LangChain 文檔](https://python.langchain.com/)
- [Gradio 文檔](https://www.gradio.app/docs)
- [FastAPI 文檔](https://fastapi.tiangolo.com/)
- [uv 使用指南](https://github.com/astral-sh/uv)

## 聯絡方式

如有問題或建議，歡迎：
- 提交 GitHub Issue
- 發起 Discussion
- 聯絡專案維護者
