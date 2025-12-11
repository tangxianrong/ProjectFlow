# ProjectFlow

## 專案簡介

ProjectFlow 是一個為 Project-Based Learning (PBL) 及 Problem-Based Learning (PrBL) 設計的多智能體（Multi-Agent）系統。系統由四個智能體協作，從底層的問題提出與學生討論、到中層理解學生學習進度與掌握程度，再到上層的學習策略規劃，協助學生在專案學習過程中獲得最佳支持。

## 系統架構
- 多智能體協作：四個 agent 串聯，分層處理學習問題與進度。
- 支援 PBL/PrBL 教學法：從問題提出、討論、進度追蹤到策略規劃。
- 可擴展性：方便教師或研究人員根據需求擴充 agent 功能。
- **主題客製化**：提供主題設定工具，讓教師可以針對特定課程和專案主題客製化 agent 行為。

## 啟動方式

### 1. 安裝 uv
本專案建議使用 [uv](https://github.com/astral-sh/uv) 作為 Python 套件與環境管理工具。

### 2. 安裝依賴
建議使用 Python 3.12 以上版本。

```bash
uv sync
```

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

- 若需啟動 API 伺服器，請執行：
  ```bash
  uv run api_server.py
  ```
- 若需啟動網頁介面，請執行：
  ```bash
  uv run projectflow_web.py
  ```

## 專案結構
- `api_server.py`：API 伺服器
- `projectflow_web.py`：網頁介面
- `background_tool.py`、`projectflow_graph.py`：輔助模組
- `theme_setter.py`：主題設定工具（獨立程式）
- `prompts/`：提示詞與設定
- `pyproject.toml`、`uv.lock`：依賴套件列表
- `THEME_SETTER_GUIDE.md`：主題設定工具使用指南

## 聯絡方式
如有問題或建議，歡迎聯絡專案維護者。
