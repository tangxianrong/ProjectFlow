# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 完整的專案文檔體系
  - `ARCHITECTURE.md` - 系統架構詳細說明
  - `DEVELOPER_GUIDE.md` - 開發者指南
  - `DEPLOYMENT.md` - 部署指南  
  - `EXAMPLES.md` - 使用範例與教程
  - `OPTIMIZATION_ANALYSIS.md` - 程式碼分析與優化建議
- 新增配置管理模組 (`config.py`)
  - 集中管理所有配置
  - 支援環境變數
  - LLM、日誌、API、Web 等配置類別
  - Token 成本計算功能
- 新增工具函式模組 (`utils.py`)
  - JSON 解析增強函式
  - Token 統計類別 (TokenStats)
  - 狀態管理工具
  - 錯誤處理工具
  - 檔案操作工具
  - 文字處理工具
  - 完整的型別提示和文檔字串
- 新增測試框架 (`tests.py`)
  - JSON 解析測試
  - Token 計數測試
  - 狀態管理測試
  - 文字處理測試
  - 配置和 Prompt 測試
- 環境變數範例檔案 (`.env.example`)
  - 完整的配置說明
  - 多種 LLM 選項範例
- 使用範例與教程
  - 完整對話流程範例
  - API 使用範例 (Python & JavaScript)
  - 進階使用技巧
  - 教學建議

### Changed
- 更新 `README.md`
  - 重新組織結構
  - 新增快速開始指南
  - 新增使用方式說明
  - 新增技術棧介紹
  - 新增常見問題解答
  - 新增文檔導航
- 改進 `.gitignore`
  - 更完整的 Python 忽略規則
  - 虛擬環境目錄
  - IDE 設定檔
  - 日誌檔案
  - Session 資料
  - 臨時檔案

### Improved
- 程式碼可讀性
  - 提供完整的型別提示範例
  - 提供詳細的文檔字串範例
  - 提供程式碼重構建議
- 開發者體驗
  - 完整的開發環境設定指南
  - 程式碼風格規範
  - Git commit 規範
  - 除錯技巧文檔
- 部署流程
  - 多種部署方式說明
  - Docker 部署配置
  - 雲端部署指南
  - 監控與維運建議

### Security
- API 安全建議
  - 提供 API key 驗證範例
  - 速率限制建議
  - HTTPS 設定說明

## [0.1.0] - 初始版本

### Added
- 四個智能體協作系統
  - Summary Agent (摘要智能體)
  - Score Agent (評分智能體)
  - Decision Agent (決策智能體)
  - Response Agent (回應智能體)
- LangGraph 工作流程編排
- 主工作流程與背景工作流程
- Gradio Web 介面
- FastAPI API 服務
- 背景工具模組化
- Prompt 模板管理
- 學習階段配置 (YAML)
- Session 狀態持久化 (Pickle)
- Token 使用統計
- 支援 OpenAI 和 Vertex AI
- 地端模型支援
- 基本的環境測試

### Features
- 問題探索引導
- 進度評估與評分
- 引導策略決策
- 友善對話回應
- 專案內容摘要
- 行動計畫追蹤
- 歷史記錄管理
- 階段式學習流程
- SDGs 目標連結

---

## 未來計畫

### 短期 (1-3 個月)
- [ ] 改進錯誤處理機制
- [ ] 提升測試覆蓋率 (目標 80%+)
- [ ] 完善所有函式的型別提示
- [ ] 實作 API 速率限制
- [ ] 產生 requirements.txt

### 中期 (3-6 個月)
- [ ] 效能優化（快取、資料庫）
- [ ] 重構重複程式碼
- [ ] 增強匯出功能 (PDF, PPT)
- [ ] 學習分析儀表板
- [ ] 多階段擴展 (階段三、四)

### 長期 (6-12 個月)
- [ ] 多人協作功能
- [ ] 教師檢視與批註
- [ ] 多語言支援 (英文、簡中)
- [ ] 外部工具整合 (搜尋、圖片生成)
- [ ] 行動版應用

---

## 如何貢獻

請參考 [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) 了解如何為專案做出貢獻。

## 聯絡方式

如有問題或建議，歡迎透過 GitHub Issues 或 Discussions 聯絡我們。
