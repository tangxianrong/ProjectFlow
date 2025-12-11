# ProjectFlow 多組學生使用指南

## 快速開始

### 學生使用流程

1. **啟動學生介面**
   ```bash
   # Windows
   start_student.bat
   
   # Linux/Mac
   uv run student_interface.py
   ```

2. **輸入組別代碼**
   - 在介面上輸入你的組別代碼（例如：`group_A`）
   - 點選「開始使用」

3. **開始對話**
   - 與 AI 助理討論你的專案想法
   - 系統會引導你完成 PBL 各個階段

### 教師使用流程

1. **啟動教師介面**
   ```bash
   # Windows
   start_teacher.bat
   
   # Linux/Mac  
   uv run teacher_interface.py
   ```

2. **查看整體概覽**
   - 在「整體概覽」頁籤查看所有組別狀態
   - 了解各組的階段分布

3. **查看組別詳情**
   - 在「組別詳情」頁籤選擇特定組別
   - 查看該組的專案內容、行動計畫、進度評分

4. **使用 AI 分析**
   - 在「AI 分析建議」頁籤選擇組別
   - AI 會分析該組的困難點並提供介入建議

5. **管理組別**
   - 在「組別管理」頁籤建立新組別
   - 輸入組別代碼、名稱、學生名單

## API 使用範例

### 建立組別

```python
import requests

response = requests.post("http://localhost:8000/groups/create", json={
    "group_id": "group_A",
    "group_name": "第一組",
    "students": ["張三", "李四", "王五"]
})
print(response.json())
```

### 查詢組別進度

```python
response = requests.get("http://localhost:8000/groups/group_A/progress")
print(response.json())
```

### 取得教師總覽

```python
response = requests.get("http://localhost:8000/teacher/overview")
print(response.json())
```

### 分析組別

```python
response = requests.post("http://localhost:8000/teacher/analyze", json={
    "group_id": "group_A"
})
print(response.json())
```

## 資料儲存

### 目錄結構

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

### 資料隔離

- 每組擁有獨立目錄
- 對話歷史完全分離
- 狀態檔案互不影響

## 常見問題

### Q1: 如何重置某組的對話？

刪除該組的狀態檔案：
```bash
rm groups_data/group_A/state_*.pkl
```

### Q2: 如何備份某組的資料？

複製該組的整個目錄：
```bash
cp -r groups_data/group_A groups_data/group_A_backup
```

### Q3: 如何匯出所有組別的進度？

使用 API 取得所有進度後匯出：
```python
import requests
import json

response = requests.get("http://localhost:8000/teacher/overview")
with open("progress_report.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=2)
```

### Q4: 學生介面和教師介面可以同時運作嗎？

可以。它們使用不同的 port：
- 學生介面：7860
- 教師介面：7861
- API 伺服器：8000

### Q5: 如何修改組別名稱或成員？

直接編輯 `groups_data/groups.json` 檔案，或使用程式：

```python
from group_manager import get_group_manager

manager = get_group_manager()
group = manager.get_group("group_A")
group.group_name = "新名稱"
group.students.append("新成員")
manager._save_groups()
```

## 進階設定

### 環境變數

- `GROUPS_DIR`: 組別資料目錄（預設：`groups_data`）
- `SESSION_DIR`: Session 資料目錄（預設：`session_data`）
- `LOG_LEVEL`: 日誌等級（預設：`INFO`）

### 自訂組別初始訊息

編輯 `student_interface.py` 中的 `get_initial_state` 函式。

### 自訂教師分析提示

編輯 `teacher_analysis_agent.py` 中的 `TEACHER_ANALYSIS_PROMPT` 常數。

## 疑難排解

### 問題：組別列表無法更新

**解決方法**：點選「更新組別列表」按鈕

### 問題：教師分析返回預設結果

**原因**：該組對話數太少或 LLM 回應格式異常

**解決方法**：
1. 確認該組有足夠的對話紀錄
2. 檢查 LLM 設定是否正確
3. 查看日誌檔案了解詳細錯誤

### 問題：無法建立組別

**可能原因**：
1. 組別代碼已存在
2. 權限不足

**解決方法**：
1. 使用不同的組別代碼
2. 檢查 `groups_data` 目錄權限

## 技術支援

如有其他問題，請：
1. 查看日誌檔案
2. 聯絡專案維護者
3. 提交 Issue 到 GitHub
