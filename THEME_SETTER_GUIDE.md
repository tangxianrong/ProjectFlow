# 主題設定 Agent 使用說明

## 概述

主題設定 Agent (Theme Setter Agent) 是一個獨立的工具，允許教師透過互動式對話來訂定專案主題，並自動修改 projectflow_agent 的四個 agent prompts，使其能夠引導學生在特定的專案主題下完成學習。

## 功能

1. **收集課程資訊**：透過互動式問答收集教師的課程名稱、專案主題和其他要求
2. **自動生成主題設定**：使用 AI 根據教師輸入生成完整的主題設定（包含學習目標、評估重點等）
3. **修改 Agent Prompts**：自動修改四個 agent（Summary、Score、Decision、Response）的系統提示詞
4. **儲存設定**：將主題設定儲存為 YAML 檔案，並備份原始 prompts

## 安裝

確保已安裝所有必要的依賴套件：

```bash
pip install python-dotenv pyyaml langchain langchain-openai langchain-google-vertexai
```

或使用 uv：

```bash
uv sync
```

## 使用方式

### 1. 設定環境變數

在 `.env` 檔案中設定 LLM 相關的環境變數：

```env
# 使用 Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# 或使用 Google Vertex AI
# 請先設定 Google Cloud 認證
```

### 2. 執行主題設定工具

```bash
python theme_setter.py
```

### 3. 按照提示輸入資訊

程式會詢問以下問題：

1. **課程名稱**：例如「永續發展專題」、「社會創新實作」等
2. **專案主題**：例如「社區環境議題探究」、「循環經濟實踐」等
3. **特定要求或限制**（可選）：例如「必須與地方社區結合」
4. **學習目標**（可選）：例如「學會問題分析與解決方法」
5. **SDGs 連結**（可選）：例如「SDG 11 永續城市、SDG 13 氣候行動」

### 4. 確認生成的主題設定

程式會顯示 AI 生成的主題設定，包含：

- 課程名稱和描述
- 專案主題
- 專案目標（3-5個要點）
- 專案範圍
- 建議的探索方向（3-5個方向）
- 評估重點（3-5個項目）
- 相關的 SDGs 目標

### 5. 確認並應用設定

確認後，程式會：

1. 備份原始的 `prompts/__init__.py` 為 `prompts/__init__.py.backup`
2. 儲存主題設定到 `prompts/theme_config.yaml`
3. 使用 AI 修改四個 agent 的 prompts
4. 更新 `prompts/__init__.py` 檔案

## 輸出檔案

執行完成後會產生以下檔案：

- `prompts/theme_config.yaml`：主題設定檔案
- `prompts/__init__.py.backup`：原始 prompts 的備份

## 恢復原始設定

如果需要恢復到原始設定，可以：

```bash
cp prompts/__init__.py.backup prompts/__init__.py
```

## 範例

### 輸入範例

```
課程名稱：永續發展專題
專案主題：社區環境議題探究與解決方案設計
特定要求：必須選擇學校周邊的真實環境議題
學習目標：學會問題分析、資料蒐集、方案設計
SDGs 連結：SDG 11 永續城市、SDG 13 氣候行動
```

### 輸出範例（theme_config.yaml）

```yaml
course_name: "永續發展專題"
course_description: "引導學生探究社區環境議題，並設計可行的解決方案"
project_theme: "社區環境議題探究與解決方案設計"
project_goals:
  - "能夠發現並定義學校周邊的真實環境問題"
  - "學會蒐集與分析環境相關資料"
  - "設計符合永續發展理念的解決方案"
  - "培養社區參與和公民意識"
project_scope: "專案必須聚焦在學校周邊可觀察的環境議題，如空氣品質、廢棄物、水資源等"
exploration_directions:
  - "觀察記錄社區環境現況"
  - "訪談社區居民了解環境問題"
  - "蒐集環境監測數據"
  - "研究類似案例的解決方案"
evaluation_points:
  - "問題定義的明確性和重要性"
  - "資料蒐集的完整性和可信度"
  - "解決方案的可行性和創新性"
  - "與 SDGs 目標的連結程度"
related_sdgs:
  - "SDG 11: 永續城市與社區"
  - "SDG 13: 氣候行動"
```

## 注意事項

1. **備份重要**：執行前建議手動備份整個 `prompts` 目錄
2. **環境變數**：確保已正確設定 `.env` 檔案中的 LLM API 金鑰
3. **網路連線**：需要網路連線以呼叫 LLM API
4. **中文支援**：所有輸入和輸出都使用繁體中文

## 常見問題

### Q: 如何修改已經設定的主題？

A: 重新執行 `theme_setter.py`，輸入新的主題設定即可。程式會覆蓋現有的設定。

### Q: 可以手動編輯 theme_config.yaml 嗎？

A: 可以，但編輯後需要重新執行 `theme_setter.py` 來更新 agent prompts。

### Q: 如何在不同課程間切換？

A: 可以為不同課程建立不同的主題設定檔案（手動命名），然後在需要時複製到 `prompts/theme_config.yaml`。

## 技術細節

### Agent Prompts 修改原則

主題設定工具會修改四個 agent 的 prompts：

1. **Summary Agent**：加入課程主題和專案範圍，確保摘要內容聚焦在課程要求
2. **Score Agent**：根據課程的評估重點調整評分標準
3. **Decision Agent**：加入專案目標和探索方向，引導學生朝正確方向發展
4. **Response Agent**：調整回應語氣和引導方式，符合課程的教學風格

### 資料流程

```
教師輸入 → LLM 生成主題設定 → 儲存 YAML → 
    → 讀取原始 prompts → LLM 修改 prompts → 更新檔案
```

## 授權

本工具為 ProjectFlow Agent 的一部分，遵循相同的授權條款。
