# 貢獻指南

感謝您對 ProjectFlow 專案的關注！我們歡迎各種形式的貢獻。

## 目錄
- [行為準則](#行為準則)
- [如何貢獻](#如何貢獻)
- [開發流程](#開發流程)
- [程式碼規範](#程式碼規範)
- [提交規範](#提交規範)
- [問題回報](#問題回報)

## 行為準則

### 我們的承諾

為了營造開放且友善的環境，我們承諾：
- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員展現同理心

### 我們的標準

**正面行為包括**：
- 使用友善和包容的語言
- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員展現同理心

**不可接受的行為包括**：
- 使用帶有性暗示的語言或圖像
- 惡意評論、人身攻擊或政治攻擊
- 公開或私下騷擾
- 未經許可發布他人的私人資訊
- 其他在專業環境中被認為不適當的行為

## 如何貢獻

### 回報 Bug

如果發現 Bug，請在 [GitHub Issues](https://github.com/AldoTang/projectflow_agent/issues) 中建立新的 issue，並包含：

- **清晰的標題**：簡短描述問題
- **詳細描述**：說明問題的詳細情況
- **重現步驟**：如何重現這個問題
- **預期行為**：你期望發生什麼
- **實際行為**：實際發生了什麼
- **環境資訊**：
  - 作業系統
  - Python 版本
  - 相關依賴版本
- **截圖**：如果適用
- **錯誤訊息**：完整的錯誤堆疊

**範例**：
```markdown
### Bug 描述
Summary Agent 在處理包含特殊字元的輸入時會崩潰

### 重現步驟
1. 啟動 Web 介面
2. 輸入包含 emoji 的訊息：「我想解決 🌍 環境問題」
3. 系統返回 500 錯誤

### 預期行為
應該能正常處理 emoji 字元

### 實際行為
伺服器崩潰並返回錯誤

### 環境
- OS: Ubuntu 22.04
- Python: 3.12
- ProjectFlow: 0.1.0

### 錯誤訊息
```
UnicodeEncodeError: ...
```
```

### 建議新功能

如果有功能建議，請：

1. 在 [Discussions](https://github.com/AldoTang/projectflow_agent/discussions) 中發起討論
2. 說明為什麼需要這個功能
3. 描述預期的使用情境
4. 提供可能的實作想法（可選）

### 改進文檔

文檔改進非常歡迎！包括：
- 修正錯字或文法錯誤
- 改進說明的清晰度
- 新增範例或教學
- 翻譯文檔

直接提交 Pull Request 即可。

### 貢獻程式碼

請遵循以下流程：

1. **Fork 專案**
2. **建立分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **進行修改**
4. **執行測試**
   ```bash
   python tests.py
   ```
5. **提交變更**
   ```bash
   git commit -m "feat: add amazing feature"
   ```
6. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **建立 Pull Request**

## 開發流程

### 設定開發環境

```bash
# 1. Fork 並 clone 專案
git clone https://github.com/YOUR_USERNAME/projectflow_agent.git
cd projectflow_agent

# 2. 安裝依賴
uv sync

# 3. 建立 .env 檔案
cp .env.example .env
# 編輯 .env 填入你的設定

# 4. 執行測試
python tests.py
```

### 分支策略

- `main` - 穩定版本
- `develop` - 開發版本
- `feature/*` - 新功能
- `fix/*` - Bug 修復
- `docs/*` - 文檔更新

### Pull Request 流程

1. **確保 PR 針對正確的分支**（通常是 `develop`）
2. **清晰的標題**：使用 [Conventional Commits](#提交規範) 格式
3. **詳細的描述**：
   - 變更內容
   - 為什麼需要這個變更
   - 如何測試
4. **通過所有測試**
5. **更新相關文檔**
6. **等待 Code Review**

### Code Review

- 所有 PR 需要至少一位維護者審核
- 請耐心等待，我們會盡快回覆
- 根據回饋進行修改
- 保持討論友善和建設性

## 程式碼規範

### Python 風格

遵循 **PEP 8** 風格指南：

```python
# 好的範例
def calculate_score(student_response: str, rubric: dict) -> float:
    """
    計算學生回應的分數
    
    Args:
        student_response: 學生的回應內容
        rubric: 評分標準
        
    Returns:
        分數 (0.0 - 5.0)
    """
    # 實作...
    return score

# 避免
def calc(r,rb):  # 缺乏型別提示和文檔
    return r*rb  # 不清楚的變數名稱
```

### 型別提示

使用型別提示提高程式碼可讀性：

```python
from typing import List, Dict, Optional

def process_messages(
    messages: List[str],
    config: Optional[Dict[str, any]] = None
) -> List[Dict[str, str]]:
    """處理訊息列表"""
    # ...
```

### 文檔字串

使用 Google 風格的文檔字串：

```python
def complex_function(param1: int, param2: str) -> bool:
    """
    簡短的一行描述
    
    更詳細的說明（如需要）。可以多行。
    
    Args:
        param1: 第一個參數的說明
        param2: 第二個參數的說明
        
    Returns:
        返回值的說明
        
    Raises:
        ValueError: 何時會拋出這個錯誤
        
    Examples:
        >>> complex_function(42, "test")
        True
    """
    # 實作...
```

### 命名規範

- **變數和函式**：`snake_case`
- **類別**：`PascalCase`
- **常數**：`UPPER_SNAKE_CASE`
- **私有成員**：`_leading_underscore`

### 測試

為新功能添加測試：

```python
import unittest

class TestNewFeature(unittest.TestCase):
    def test_basic_case(self):
        """測試基本情況"""
        result = new_feature("input")
        self.assertEqual(result, "expected")
    
    def test_edge_case(self):
        """測試邊界情況"""
        result = new_feature("")
        self.assertEqual(result, "")
```

## 提交規範

使用 **Conventional Commits** 格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type（類型）

- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文檔變更
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置或輔助工具變動
- `perf`: 效能改進

### 範例

```bash
# 新功能
git commit -m "feat(agents): add context caching for summary agent"

# Bug 修復
git commit -m "fix(web): resolve session state sync issue"

# 文檔
git commit -m "docs(readme): update installation instructions"

# 重構
git commit -m "refactor(utils): extract common token counting logic"
```

### 詳細訊息範例

```
feat(export): add PDF export functionality

- Implement PDF generation using ReportLab
- Add export button to web interface
- Include conversation history and project summary
- Add unit tests for PDF generation

Closes #123
```

## 問題回報

### 安全漏洞

**請勿在公開 issue 中回報安全漏洞**。

請透過私人管道聯絡維護者。

### 提問

- 先查看 [文檔](README.md)、[開發者指南](DEVELOPER_GUIDE.md)
- 搜尋現有的 [Issues](https://github.com/AldoTang/projectflow_agent/issues)
- 在 [Discussions](https://github.com/AldoTang/projectflow_agent/discussions) 提問

## 社群

- **GitHub Issues**: Bug 回報和功能請求
- **GitHub Discussions**: 問題討論和想法分享
- **Pull Requests**: 程式碼貢獻

## 授權

貢獻的程式碼將採用與專案相同的授權條款（MIT License）。

---

**再次感謝您的貢獻！** 🎉

每一個貢獻，無論大小，都讓 ProjectFlow 變得更好！
