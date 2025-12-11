"""
ProjectFlow 工具函式模組

此模組提供各種輔助函式，包括：
- JSON 解析
- Token 計數
- 錯誤處理
- 狀態管理
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


# === JSON 處理工具 ===

def extract_first_json_list(text: str) -> List[Dict[str, Any]]:
    """
    從文字中提取第一個 JSON list
    
    容錯處理 LLM 輸出可能包含額外文字的情況
    
    Args:
        text: 包含 JSON 的文字
        
    Returns:
        解析後的 list，失敗時返回空 list
    
    Examples:
        >>> extract_first_json_list('[{"key": "value"}]')
        [{'key': 'value'}]
        
        >>> extract_first_json_list('一些文字 [{"key": "value"}] 更多文字')
        [{'key': 'value'}]
    """
    # 先嘗試直接解析
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        logger.warning(f"JSON 解析成功但不是 list 類型: {type(data)}")
    except json.JSONDecodeError as e:
        logger.debug(f"直接解析 JSON 失敗: {e}")
    
    # 使用正則表達式尋找第一組 [ ... ]
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        snippet = match.group(0)
        try:
            data = json.loads(snippet)
            if isinstance(data, list):
                logger.debug("成功從文字中提取 JSON list")
                return data
            logger.warning(f"提取的 JSON 不是 list 類型: {type(data)}")
        except json.JSONDecodeError as e:
            logger.error(f"提取的 JSON 片段無法解析: {e}")
    
    logger.error(f"無法從文字中提取有效的 JSON list。文字長度: {len(text)}")
    return []


def safe_json_parse(text: str, default: Any = None) -> Any:
    """
    安全地解析 JSON，失敗時返回預設值
    
    Args:
        text: JSON 文字
        default: 解析失敗時的預設值
        
    Returns:
        解析結果或預設值
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON 解析失敗: {e}")
        return default


# === Token 計數工具 ===

def count_tokens(text: str) -> int:
    """
    計算文字的 token 數量
    
    優先使用 tiktoken，若未安裝則使用簡單估算
    
    Args:
        text: 要計數的文字
        
    Returns:
        token 數量
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        logger.warning(
            "tiktoken 未安裝，使用簡單估算。建議安裝: pip install tiktoken"
        )
        # 簡單估算：中文 1.5 字元/token，英文 4 字元/token
        # 粗略平均約 2 字元/token
        return len(text) // 2
    except Exception as e:
        logger.error(f"Token 計數失敗: {e}")
        return len(text.split())  # 最後退回到單詞計數


class TokenStats:
    """Token 使用統計類別"""
    
    def __init__(self):
        self.stats: Dict[str, Dict[str, int]] = {
            "summary_agent": {"input": 0, "output": 0},
            "score_agent": {"input": 0, "output": 0},
            "decision_agent": {"input": 0, "output": 0},
            "response_agent": {"input": 0, "output": 0},
        }
    
    def add_input(self, agent: str, tokens: int) -> None:
        """記錄輸入 token"""
        if agent in self.stats:
            self.stats[agent]["input"] += tokens
        else:
            logger.warning(f"未知的 agent: {agent}")
    
    def add_output(self, agent: str, tokens: int) -> None:
        """記錄輸出 token"""
        if agent in self.stats:
            self.stats[agent]["output"] += tokens
        else:
            logger.warning(f"未知的 agent: {agent}")
    
    def get_total_input(self) -> int:
        """取得總輸入 token 數"""
        return sum(stat["input"] for stat in self.stats.values())
    
    def get_total_output(self) -> int:
        """取得總輸出 token 數"""
        return sum(stat["output"] for stat in self.stats.values())
    
    def get_total(self) -> int:
        """取得總 token 數"""
        return self.get_total_input() + self.get_total_output()
    
    def get_stats(self) -> Dict[str, Dict[str, int]]:
        """取得完整統計資料"""
        return self.stats.copy()
    
    def get_summary(self) -> str:
        """取得統計摘要"""
        total_input = self.get_total_input()
        total_output = self.get_total_output()
        total = self.get_total()
        
        summary = [
            f"Token 使用統計:",
            f"  總輸入: {total_input:,}",
            f"  總輸出: {total_output:,}",
            f"  總計: {total:,}",
            "\n各 Agent 統計:"
        ]
        
        for agent, stat in self.stats.items():
            summary.append(
                f"  {agent}: 輸入={stat['input']:,}, 輸出={stat['output']:,}"
            )
        
        return "\n".join(summary)
    
    def reset(self) -> None:
        """重設統計"""
        for agent in self.stats:
            self.stats[agent]["input"] = 0
            self.stats[agent]["output"] = 0


# === 狀態處理工具 ===

def validate_state(state: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    驗證狀態是否包含必要的欄位
    
    Args:
        state: 要驗證的狀態
        required_keys: 必要的欄位列表
        
    Returns:
        是否通過驗證
    """
    missing_keys = [key for key in required_keys if key not in state]
    
    if missing_keys:
        logger.error(f"狀態缺少必要欄位: {missing_keys}")
        return False
    
    return True


def merge_states(base: Dict[str, Any], update: Dict[str, Any]) -> Dict[str, Any]:
    """
    合併兩個狀態字典
    
    update 中的值會覆蓋 base 中的值
    
    Args:
        base: 基礎狀態
        update: 要更新的狀態
        
    Returns:
        合併後的狀態
    """
    result = base.copy()
    result.update(update)
    return result


# === 錯誤處理工具 ===

class ProjectFlowError(Exception):
    """ProjectFlow 專案的基礎例外類別"""
    pass


class LLMError(ProjectFlowError):
    """LLM 相關錯誤"""
    pass


class StateError(ProjectFlowError):
    """狀態管理相關錯誤"""
    pass


class ConfigError(ProjectFlowError):
    """配置相關錯誤"""
    pass


def safe_execute(func, *args, default=None, error_msg: str = "", **kwargs):
    """
    安全執行函式，捕獲例外並返回預設值
    
    Args:
        func: 要執行的函式
        *args: 函式參數
        default: 發生錯誤時的預設返回值
        error_msg: 自訂錯誤訊息
        **kwargs: 函式關鍵字參數
        
    Returns:
        函式執行結果或預設值
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = error_msg or f"執行 {func.__name__} 時發生錯誤"
        logger.error(f"{msg}: {e}", exc_info=True)
        return default


# === 檔案處理工具 ===

def ensure_dir(path: Union[str, Path]) -> Path:
    """
    確保目錄存在，不存在則建立
    
    Args:
        path: 目錄路徑
        
    Returns:
        Path 物件
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_read_file(path: Union[str, Path], encoding: str = "utf-8") -> Optional[str]:
    """
    安全讀取檔案
    
    Args:
        path: 檔案路徑
        encoding: 檔案編碼
        
    Returns:
        檔案內容或 None
    """
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        logger.error(f"讀取檔案失敗 {path}: {e}")
        return None


def safe_write_file(
    path: Union[str, Path],
    content: str,
    encoding: str = "utf-8"
) -> bool:
    """
    安全寫入檔案
    
    Args:
        path: 檔案路徑
        content: 要寫入的內容
        encoding: 檔案編碼
        
    Returns:
        是否成功
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        logger.error(f"寫入檔案失敗 {path}: {e}")
        return False


# === 文字處理工具 ===

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截斷文字到指定長度
    
    Args:
        text: 原始文字
        max_length: 最大長度
        suffix: 截斷後綴
        
    Returns:
        截斷後的文字
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_whitespace(text: str) -> str:
    """
    清理多餘的空白字元
    
    Args:
        text: 原始文字
        
    Returns:
        清理後的文字
    """
    # 移除行首行尾空白
    lines = [line.strip() for line in text.split("\n")]
    # 移除空行
    lines = [line for line in lines if line]
    return "\n".join(lines)
