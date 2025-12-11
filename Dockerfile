# ProjectFlow Agent Dockerfile
# 支援 Web 介面和 API 服務的容器化部署

FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安裝 uv（快速的 Python 套件管理器）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 複製專案檔案
COPY pyproject.toml uv.lock ./
COPY . .

# 安裝 Python 依賴
RUN uv sync --frozen

# 建立資料目錄
RUN mkdir -p session_data groups_data

# 設定環境變數
ENV SESSION_DIR=/app/session_data \
    LOG_LEVEL=INFO \
    MODULE_LOG_LEVEL=INFO

# 暴露埠口
# 7860: Gradio Web 介面
# 8000: FastAPI 服務
EXPOSE 7860 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# 預設啟動 Web 介面
# 可以透過 docker run 命令覆寫來啟動不同服務
CMD ["uv", "run", "projectflow_web.py"]
