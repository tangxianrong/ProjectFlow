# ProjectFlow

## 專案簡介

ProjectFlow 是一個為 Project-Based Learning (PBL) 及 Problem-Based Learning (PrBL) 設計的多智能體（Multi-Agent）系統。系統由四個智能體協作，從底層的問題提出與學生討論、到中層理解學生學習進度與掌握程度，再到上層的學習策略規劃，協助學生在專案學習過程中獲得最佳支持。

## 系統架構
<<<<<<< HEAD

### 學生端架構
- **多組學生支援**：支援多組學生同時使用，各組資料完全獨立，互不干擾
- **多智能體協作**：四個 agent 串聯，分層處理學習問題與進度
- **組別識別**：每組學生擁有獨立的組別代碼和對話歷史

### 教師端架構
- **進度總覽**：查看所有組別的學習進度與階段分布
- **AI 分析助手**：TeacherAnalysisAgent 協助分析各組困難點
- **介入建議**：提供教師具體的介入時機與引導方式
- **批量分析**：一次分析所有組別的學習狀況

### 技術特色
- 支援 PBL/PrBL 教學法：從問題提出、討論、進度追蹤到策略規劃
- 可擴展性：方便教師或研究人員根據需求擴充 agent 功能
- 資料隔離：各組資料獨立儲存，確保隱私與安全
=======
- 多智能體協作：四個 agent 串聯，分層處理學習問題與進度。
- 支援 PBL/PrBL 教學法：從問題提出、討論、進度追蹤到策略規劃。
- 可擴展性：方便教師或研究人員根據需求擴充 agent 功能。
- **主題客製化**：提供主題設定工具，讓教師可以針對特定課程和專案主題客製化 agent 行為。
>>>>>>> dev2

## 啟動方式

### 1. 安裝 uv
本專案建議使用 [uv](https://github.com/astral-sh/uv) 作為 Python 套件與環境管理工具。

### 2. 安裝依賴
建議使用 Python 3.12 以上版本。

```bash
uv sync
```

<<<<<<< HEAD
### 3. 啟動介面
=======
### 3. (可選) 設定課程主題

在啟動主程式前，教師可以使用主題設定工具來客製化 agent 行為：

```bash
uv run theme_setter.py
```

或

```bash
python theme_setter.py
```

此工具會引導教師輸入課程資訊和專案要求，然後自動修改四個 agent 的 prompts，使其能夠引導學生在特定的專案主題下完成學習。詳細使用說明請參考 [THEME_SETTER_GUIDE.md](THEME_SETTER_GUIDE.md)。

### 4. 啟動主程式
>>>>>>> dev2

#### 學生介面（預設 port 7860）
- 支援多組學生獨立使用
- 每組需要輸入組別代碼
- 對話歷史與進度獨立儲存

Windows:
```bash
start_student.bat
```

Linux/Mac:
```bash
uv run student_interface.py
```

#### 教師介面（預設 port 7861）
- 查看所有組別進度
- AI 分析各組學習狀況
- 取得介入建議

Windows:
```bash
start_teacher.bat
```

Linux/Mac:
```bash
uv run teacher_interface.py
```

#### API 伺服器（預設 port 8000）
提供 RESTful API 支援外部整合

```bash
uv run api_server.py
```

#### 原始網頁介面（相容性保留）
```bash
uv run projectflow_web.py
```

## API 端點

### 組別管理
- `POST /groups/create` - 建立新組別
- `GET /groups/list` - 列出所有組別
- `GET /groups/{group_id}/progress` - 取得組別進度

### 教師功能
- `GET /teacher/overview` - 取得教師總覽
- `POST /teacher/analyze` - 分析特定組別

### 背景更新
- `POST /background_update` - 背景更新工具

## 專案結構
<<<<<<< HEAD

### 核心模組
- `api_server.py` - API 伺服器（支援組別與教師功能）
- `student_interface.py` - 學生介面（支援多組）
- `teacher_interface.py` - 教師介面（分析與總覽）
- `projectflow_web.py` - 原始網頁介面（相容性保留）

### 資料模型與管理
- `models.py` - 資料模型定義（Group, GroupProgress, TeacherAnalysis）
- `group_manager.py` - 組別管理模組
- `teacher_analysis_agent.py` - 教師分析 Agent

### 核心邏輯
- `background_tool.py` - 背景工具模組
- `projectflow_graph.py` - Agent 流程圖與核心邏輯
- `prompts/` - 提示詞與設定

### 設定檔
- `pyproject.toml`, `uv.lock` - 依賴套件列表

## 資料儲存結構

```
groups_data/
├── groups.json              # 組別清單
├── group_A/                 # 第一組資料
│   ├── state_xxx.pkl        # 對話狀態
│   └── 專案計畫書_xxx.md   # 專案文件
├── group_B/                 # 第二組資料
│   ├── state_xxx.pkl
│   └── 專案計畫書_xxx.md
└── ...
```

## 使用流程

### 學生使用流程
1. 開啟學生介面
2. 輸入組別代碼（例如：group_A）
3. 點選「開始使用」
4. 與 AI 助理進行對話，完成專案學習

### 教師使用流程
1. 開啟教師介面
2. 在「整體概覽」查看所有組別狀態
3. 在「組別詳情」查看特定組別的詳細資訊
4. 在「AI 分析建議」取得介入建議
5. 在「組別管理」建立新組別

## 文件

- [使用指南](USAGE_GUIDE.md) - 詳細的使用說明與常見問題
- [API 示範](demo_api_usage.py) - API 使用範例程式

## 範例

### 快速開始示範

執行 API 示範程式：

```bash
# 先啟動 API 伺服器
uv run api_server.py

# 在另一個終端執行示範
python3 demo_api_usage.py
```
=======
- `api_server.py`：API 伺服器
- `projectflow_web.py`：網頁介面
- `background_tool.py`、`projectflow_graph.py`：輔助模組
- `theme_setter.py`：主題設定工具（獨立程式）
- `prompts/`：提示詞與設定
- `pyproject.toml`、`uv.lock`：依賴套件列表
- `THEME_SETTER_GUIDE.md`：主題設定工具使用指南
>>>>>>> dev2

## 聯絡方式
如有問題或建議，歡迎聯絡專案維護者。
