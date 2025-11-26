import os
import pickle
import json
import logging
from typing import Any, Dict, List, Optional

# 這個模組將 background_update_tool 模組化，並提供給 GPTs / LangChain 的工具介面

try:
    from pydantic import BaseModel, Field  # type: ignore
    from langchain.tools import StructuredTool  # type: ignore
except Exception:  # pragma: no cover - 若未安裝依賴
    BaseModel = object  # type: ignore
    Field = lambda *a, **k: None  # type: ignore
    StructuredTool = None  # type: ignore

# 將在 setup() 時注入
_background_graph = None
_AIMessage = None
_HumanMessage = None
_logger = logging.getLogger(__name__)

# === 新增：集中儲存目錄 ===
SESSION_DIR = os.getenv("SESSION_DIR", "session_data")
os.makedirs(SESSION_DIR, exist_ok=True)

BACKGROUND_UPDATE_TOOL_SPEC: Dict[str, Any] = {
    "name": "background_update_tool",
    "description": "根據 session_id 載入/建立歷史狀態，加入最新的 AI 與使用者訊息，執行背景 summary/score workflow，更新並儲存狀態後回傳精簡可序列化結果。",
    "parameters": {
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "對話 session 識別碼；若不存在會建立新的狀態檔。"},
            "prev_ai_prompt": {"type": "string", "description": "上一輪主流程(或模型)產生的助手回覆全文。"},
            "user_prompt": {"type": "string", "description": "本輪最新使用者輸入。"}
        },
        "required": ["session_id", "prev_ai_prompt", "user_prompt"]
    }
}

BACKGROUND_UPDATE_STRUCTURED_TOOL = None  # 在 setup 內建立

# ----------------- 輔助函式 -----------------

def _state_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"state_{session_id}.pkl")

def _default_state(session_id: str) -> Dict[str, Any]:
    return {
        "messages": [],
        "next_agent": None,
        "project_content": "",
        "action_plan": "",
        "historical_log": "",
        "current_progress": "",
        "guidance_strategy": "",
        "score": None,
        "next_response": None,
        "session_id": session_id
    }

def _flatten_graph_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """將 LangGraph stream 產生的 {node_name: {...}} 結構攤平成頂層。
    參考 buddy_web.py 讀取時會挑出 score_agent/summary_agent 內容更新至 root。"""
    node_keys = [k for k, v in state.items() if isinstance(v, dict) and k.endswith('_agent')]
    for k in node_keys:
        inner = state.get(k, {})
        if isinstance(inner, dict):
            for ik, iv in inner.items():
                # 不覆蓋已存在且有值的欄位 (保留最新)
                if ik not in state or state[ik] in (None, ""):
                    state[ik] = iv
    return state

def _load_state(session_id: str) -> Dict[str, Any]:
    path = _state_path(session_id)
    if os.path.exists(path):
        try:
            with open(path, "rb") as f:
                state = pickle.load(f)
            if not isinstance(state, dict):  # 防呆
                return _default_state(session_id)
            # 若是包在某個節點，例如 summary_agent/score_agent
            # 模仿 buddy_web 的做法：如果包含 score_agent 就取其值
            if "score_agent" in state and isinstance(state["score_agent"], dict):
                base = state["score_agent"].copy()
                base.update({k: v for k, v in state.items() if k not in ("score_agent", "summary_agent")})
                state = base
            elif "summary_agent" in state and isinstance(state["summary_agent"], dict):
                base = state["summary_agent"].copy()
                base.update({k: v for k, v in state.items() if k not in ("score_agent", "summary_agent")})
                state = base
            # 基本欄位補齊
            defaults = _default_state(session_id)
            for k, v in defaults.items():
                state.setdefault(k, v)
            return _flatten_graph_state(state)
        except Exception as e:  # pragma: no cover
            _logger.warning(f"讀取既有 state 失敗，重新建立。error={e}")
    return _default_state(session_id)

def _serialize_messages(messages: List[Any], tail: int = 12):
    out: List[Dict[str, str]] = []
    for m in messages[-tail:]:
        if _AIMessage and isinstance(m, _AIMessage):  # type: ignore
            role = 'assistant'
        elif _HumanMessage and isinstance(m, _HumanMessage):  # type: ignore
            role = 'user'
        else:
            role = getattr(m, 'type', 'unknown')
        out.append({"role": role, "content": getattr(m, 'content', '')})
    return out

# ----------------- 主工具函式 -----------------

def background_update_tool(session_id: str, prev_ai_prompt: str, user_prompt: str) -> Dict[str, Any]:
    if _background_graph is None:
        raise RuntimeError("background_update_tool 尚未經過 setup() 初始化背景圖。")
    state = _load_state(session_id)

    # 附加上一輪 AI（避免重複）
    if prev_ai_prompt and (not state["messages"] or state["messages"][-1].content != prev_ai_prompt):  # type: ignore
        state["messages"].append(_AIMessage(content=prev_ai_prompt))  # type: ignore
    # 新使用者輸入
    if user_prompt:
        state["messages"].append(_HumanMessage(content=user_prompt))  # type: ignore

    # 執行背景 graph：攤平每個節點輸出的內層 dict
    for event in _background_graph.stream(state):  # type: ignore
        if isinstance(event, dict):
            for node_name, node_state in event.items():
                if isinstance(node_state, dict):
                    # 合併 node_state 到 root
                    for k, v in node_state.items():
                        state[k] = v
                    # 也保留 node_name -> node_state 以便除錯
                    state[node_name] = node_state
    # 再次攤平
    state = _flatten_graph_state(state)

    # 儲存
    with open(_state_path(session_id), "wb") as f:
        pickle.dump(state, f)

    return {
        "session_id": session_id,
        "project_content": state.get("project_content", ""),
        "action_plan": state.get("action_plan", ""),
        "historical_log": state.get("historical_log", ""),
        "current_progress": state.get("current_progress", ""),
        "guidance_strategy": state.get("guidance_strategy", ""),
        "stage_number": state.get("stage_number"),
        "score": state.get("score"),
        "messages_tail": _serialize_messages(state.get("messages", []))
    }

# ----------------- LangChain / OpenAI 包裝 -----------------

class BackgroundUpdateInput(BaseModel):  # type: ignore
    session_id: str = Field(..., description="對話 session 識別碼")
    prev_ai_prompt: str = Field(..., description="上一輪 AI 回覆")
    user_prompt: str = Field(..., description="本輪使用者輸入")

def _background_update_run(session_id: str, prev_ai_prompt: str, user_prompt: str):
    result = background_update_tool(session_id=session_id, prev_ai_prompt=prev_ai_prompt, user_prompt=user_prompt)
    try:
        json.dumps(result)
    except Exception as e:  # pragma: no cover
        result = {"error": f"serialization failed: {e}"}
    return result

def setup(background_graph, AIMessage, HumanMessage, logger: Optional[logging.Logger] = None):
    global _background_graph, _AIMessage, _HumanMessage, _logger, BACKGROUND_UPDATE_STRUCTURED_TOOL
    _background_graph = background_graph
    _AIMessage = AIMessage
    _HumanMessage = HumanMessage
    if logger:
        _logger = logger
    if StructuredTool:
        BACKGROUND_UPDATE_STRUCTURED_TOOL = StructuredTool.from_function(  # type: ignore
            name=BACKGROUND_UPDATE_TOOL_SPEC["name"],
            description=BACKGROUND_UPDATE_TOOL_SPEC["description"],
            func=_background_update_run,
            args_schema=BackgroundUpdateInput,  # type: ignore
            return_direct=True
        )
    return {
        "spec": BACKGROUND_UPDATE_TOOL_SPEC,
        "structured_tool": BACKGROUND_UPDATE_STRUCTURED_TOOL,
        "run_function": background_update_tool
    }

def get_background_update_function_spec() -> Dict[str, Any]:
    return BACKGROUND_UPDATE_TOOL_SPEC

def list_available_tools():
    tools = []
    if BACKGROUND_UPDATE_STRUCTURED_TOOL:
        tools.append(BACKGROUND_UPDATE_STRUCTURED_TOOL)
    return tools
