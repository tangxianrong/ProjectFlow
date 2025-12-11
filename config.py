"""
ProjectFlow 配置管理模組

此模組負責集中管理所有系統配置，包括：
- 環境變數載入
- LLM 設定
- 日誌設定
- 路徑設定
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# 載入環境變數 (自動搜尋 .env 檔案)
load_dotenv()

# === 路徑設定 ===
PROJECT_ROOT = Path(__file__).parent
SESSION_DIR = Path(os.getenv("SESSION_DIR", "session_data"))
SESSION_DIR.mkdir(exist_ok=True)

# === LLM 設定 ===
class LLMConfig:
    """LLM 相關配置"""
    
    # OpenAI 或相容 API 設定
    AZURE_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    
    # Google Vertex AI 設定
    GOOGLE_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    VERTEX_MODEL: str = os.getenv("VERTEX_MODEL", "gemini-2.5-flash")
    
    # LLM 通用設定
    TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "60"))
    MAX_RETRIES: int = int(os.getenv("LLM_MAX_RETRIES", "2"))
    
    @classmethod
    def use_openai(cls) -> bool:
        """判斷是否使用 OpenAI 或相容 API"""
        return bool(cls.AZURE_ENDPOINT and cls.AZURE_API_KEY)
    
    @classmethod
    def get_openai_endpoint(cls) -> str:
        """取得完整的 OpenAI API 端點 (確保有 /v1)"""
        if not cls.AZURE_ENDPOINT:
            return ""
        endpoint = cls.AZURE_ENDPOINT
        if not endpoint.endswith("/v1"):
            endpoint = endpoint.rstrip("/") + "/v1"
        return endpoint

# === 日誌設定 ===
class LogConfig:
    """日誌相關配置"""
    
    LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    MODULE_LEVEL: str = os.getenv("MODULE_LOG_LEVEL", "INFO").upper()
    FORMAT: str = "%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s"
    DATE_FORMAT: str = "%H:%M:%S"
    
    # 是否輸出到檔案
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "false").lower() == "true"
    LOG_FILE_PATH: Path = Path(os.getenv("LOG_FILE_PATH", "logs/projectflow.log"))
    
    @classmethod
    def setup_logging(cls) -> None:
        """設定全域日誌系統"""
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(cls.FORMAT, datefmt=cls.DATE_FORMAT)
        )
        handlers.append(console_handler)
        
        # File handler (可選)
        if cls.LOG_TO_FILE:
            cls.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(cls.LOG_FILE_PATH, encoding="utf-8")
            file_handler.setFormatter(
                logging.Formatter(cls.FORMAT, datefmt=cls.DATE_FORMAT)
            )
            handlers.append(file_handler)
        
        # 設定根 logger (僅在未設定時)
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=cls.LEVEL,
                format=cls.FORMAT,
                datefmt=cls.DATE_FORMAT,
                handlers=handlers
            )

# === API 設定 ===
class APIConfig:
    """API 伺服器相關配置"""
    
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    API_KEY: Optional[str] = os.getenv("API_KEY")  # 可選的 API 驗證金鑰
    ENABLE_AUTH: bool = os.getenv("ENABLE_API_AUTH", "false").lower() == "true"

# === Web 介面設定 ===
class WebConfig:
    """Web 介面相關配置"""
    
    HOST: str = os.getenv("WEB_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("WEB_PORT", "7860"))
    SHARE: bool = os.getenv("WEB_SHARE", "false").lower() == "true"
    MAX_THREADS: int = int(os.getenv("WEB_MAX_THREADS", "40"))
    SHOW_ERROR: bool = os.getenv("WEB_SHOW_ERROR", "true").lower() == "true"

# === Token 統計設定 ===
class TokenConfig:
    """Token 使用統計相關配置"""
    
    ENABLE_TRACKING: bool = os.getenv("ENABLE_TOKEN_TRACKING", "true").lower() == "true"
    
    # Token 價格 (USD per 1000 tokens)
    # 可根據實際使用的模型調整
    INPUT_PRICE_PER_1K: float = float(os.getenv("INPUT_TOKEN_PRICE", "0.01"))
    OUTPUT_PRICE_PER_1K: float = float(os.getenv("OUTPUT_TOKEN_PRICE", "0.03"))
    
    @classmethod
    def calculate_cost(cls, input_tokens: int, output_tokens: int) -> float:
        """計算 token 使用成本"""
        if not cls.ENABLE_TRACKING:
            return 0.0
        
        input_cost = (input_tokens / 1000) * cls.INPUT_PRICE_PER_1K
        output_cost = (output_tokens / 1000) * cls.OUTPUT_PRICE_PER_1K
        return input_cost + output_cost

# === 應用初始化 ===
def init_config() -> None:
    """初始化應用配置"""
    # 設定日誌
    LogConfig.setup_logging()
    
    # 確保必要目錄存在
    SESSION_DIR.mkdir(exist_ok=True)
    
    if LogConfig.LOG_TO_FILE:
        LogConfig.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

# 自動初始化
init_config()
