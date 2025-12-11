from dotenv import load_dotenv
import os
import json
import yaml
import threading
import pickle
import uuid
import logging
import re

from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import HumanMessage, AIMessage
from typing import TypedDict, List, Optional

import prompts

# 新增: 導入模組化背景工具
import background_tool


logger = logging.getLogger(__name__)
# === Logging 設定，確保在直接執行時能輸出到 Terminal ===
if not logging.getLogger().handlers:  # 根 logger 無 handler 時才設定，避免重複
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)-8s | %(threadName)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
# 個別 logger 層級（可透過環境變數調整）
logger.setLevel(os.getenv("MODULE_LOG_LEVEL", "INFO").upper())

# 若需要顯示 langchain / httpx 詳細內容，可自行解除註解
# logging.getLogger("langchain").setLevel("WARNING")
# logging.getLogger("httpx").setLevel("WARNING")


# --- JSON 解析輔助：容錯處理模型輸出夾雜文字情況 ---
def extract_first_json_list(text: str):
    """嘗試從文字中擷取第一個 JSON list 並回傳其物件列表。失敗回 []."""
    # 先嘗試直接解析
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    # 正則尋找第一組 [ ... ]
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        snippet = match.group(0)
        try:
            data = json.loads(snippet)
            if isinstance(data, list):
                return data
        except Exception:
            return []
    return []


# Define state
class AgentState(TypedDict):
    messages: List
    project_content: str  # 修正為 str
    action_plan: str
    historical_log: str
    current_progress: str
    guidance_strategy: str
    score: str
    next_response: Optional[dict]
    session_id: str
    next_agent: Optional[str]
    stage_number: Optional[int]
    group_id: Optional[str]  # 新增組別 ID 支援


# Load environment config
load_dotenv("./.env")

# Set Azure OpenAI API (支援地端部署的 OpenAI 模型)
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# Init LLM
if azure_endpoint and azure_api_key:
    # 地端 OpenAI 模型使用 ChatOpenAI
    # 確保 endpoint 有 /v1 路徑
    endpoint = azure_endpoint
    if not endpoint.endswith("/v1"):
        endpoint = endpoint.rstrip("/") + "/v1"
    
    llm = ChatOpenAI(
        model=deployment_name,
        base_url=endpoint,
        api_key=azure_api_key,
        temperature=0,
        timeout=60,
        max_retries=2
    )
else:
    llm = ChatVertexAI(model_name="gemini-2.5-flash")

# Summary agent
# 依據新prompt，需傳遞更多欄位，並解析新格式


def build_current_progress(stage_number, messages, stage_settings):
    # 取得對應階段資訊
    stage_key = f"stage_{stage_number}"
    stage = stage_settings.get(stage_key, {})
    stage_name = stage.get("name", f"階段{stage_number}")
    score_list = stage.get("score_list", [])
    # 取最近一則對話摘要
    dialog_summary = messages[-1].content if messages else ""
    # 組合評分表格
    score_rows = "\n".join([f"| {item} | /5 |  |" for item in score_list])
    # 組合 current_progress
    current_progress = f"""
## 當前狀態與評分

### 當前階段
- 階段名稱：{stage_name}
- 對話摘要：{dialog_summary}

### 評分項目

| 評分項目 | 分數 | 說明 |
|----------|------|------|
{score_rows}
"""
    return current_progress


def summary_agent(state: AgentState) -> AgentState:
    logger.info(f"[summary_agent] state id: {id(state)}")
    logger.info(f"[summary_agent] state: {state}")
    prompt = prompts.SUMMARY_AGENT_PROMPT.format(
        current_dialog="\n".join([m.content for m in state["messages"][-3:]]),
        project_content=state.get("project_content", ""),
        action_plan=state.get("action_plan", ""),
        historical_log=state.get("historical_log", ""),
        current_progress=state.get("current_progress", ""),
    )
    input_tokens = count_tokens(prompt)
    TOKEN_STATS["summary_agent"]["input"] += input_tokens
    logger.info(
        f"[summary_agent] 輸入 tokens: {input_tokens}, 累計輸入: {TOKEN_STATS['summary_agent']['input']}"
    )
    logger.info(f"📝 SummaryAgent 輸入prompt：{prompt}")
    response = llm.invoke([HumanMessage(content=prompt)])
    output_tokens = count_tokens(response.content)
    TOKEN_STATS["summary_agent"]["output"] += output_tokens
    logger.info(
        f"[summary_agent] 輸出 tokens: {output_tokens}, 累計輸出: {TOKEN_STATS['summary_agent']['output']}"
    )
    logger.info(f"result(raw): {response.content}")
    parsed_list = extract_first_json_list(response.content)
    result = parsed_list[0] if parsed_list else {}
    with open("prompts/stage_setting.yaml", encoding="utf-8") as f:
        stage_settings = yaml.safe_load(f)
    prev_stage = state.get("stage_number", None)
    new_stage = result.get("stage_number")
    if isinstance(new_stage, str) and new_stage.isdigit():
        new_stage = int(new_stage)
    if new_stage is None:
        new_stage = prev_stage if prev_stage is not None else 1
    if new_stage != prev_stage or not state.get("current_progress"):
        state["current_progress"] = build_current_progress(
            new_stage, state["messages"], stage_settings
        )
    if result.get("project_content"):
        state["project_content"] = result["project_content"]
    if result.get("ACTION_PLAN"):
        state["action_plan"] = result["ACTION_PLAN"]
    if result.get("HISTORICAL_LOG"):
        state["historical_log"] = result["HISTORICAL_LOG"]
    state["stage_number"] = new_stage
    return state


# Score agent
# 需傳遞 action_plan, current_progress


def score_agent(state: AgentState) -> AgentState:
    logger.info(f"[score_agent] state id: {id(state)}")
    logger.info(f"[score_agent] state: {state}")
    prompt = prompts.SCORE_AGENT_PROMPT.format(
        current_dialog="\n".join([m.content for m in state["messages"][-3:]]),
        project_content=state.get("project_content", ""),
        action_plan=state.get("action_plan", ""),
        current_progress=state.get("current_progress", ""),
    )
    # 計算與累計 input token 數量
    input_tokens = count_tokens(prompt)
    TOKEN_STATS["score_agent"]["input"] += input_tokens
    logger.info(
        f"[score_agent] 輸入 tokens: {input_tokens}, 累計輸入: {TOKEN_STATS['score_agent']['input']}"
    )
    logger.info(f"📝 ScoreAgent 輸入prompt：{prompt}")
    response = llm.invoke([HumanMessage(content=prompt)])
    logger.info(f"result(raw): {response.content}")
    # 計算與累計 output token 數量
    output_tokens = count_tokens(response.content)
    TOKEN_STATS["score_agent"]["output"] += output_tokens
    logger.info(
        f"[score_agent] 輸出 tokens: {output_tokens}, 累計輸出: {TOKEN_STATS['score_agent']['output']}"
    )

    try:
        parsed_list = extract_first_json_list(response.content)
        result = parsed_list[0] if parsed_list else {}
    except Exception:
        result = {}
    state["current_progress"] = result.get(
        "current_progress", state.get("current_progress", "")
    )
    return state


# Decision agent
# 需傳遞更多欄位，並解析 Guidance_and_Strategy


def decision_agent(state: AgentState) -> AgentState:
    logger.info(f"[decision_agent] state id: {id(state)}")
    logger.info(f"[decision_agent] state: {state}")
    prompt = prompts.DECISION_AGENT_PROMPT.format(
        current_dialog="\n".join([m.content for m in state["messages"][-3:]]),
        project_content=state.get("project_content", ""),
        action_plan=state.get("action_plan", ""),
        historical_log=state.get("historical_log", ""),
        current_progress=state.get("current_progress", ""),
    )
    _state_copy = state.copy()
    thread = threading.Thread(target=run_background_graph, args=(_state_copy,))
    thread.start()
    # 計算與累計 input token 數量
    input_tokens = count_tokens(prompt)
    TOKEN_STATS["decision_agent"]["input"] += input_tokens
    logger.info(
        f"[decision_agent] 輸入 tokens: {input_tokens}, 累計輸入: {TOKEN_STATS['decision_agent']['input']}"
    )
    logger.info(f"📝 DecisionAgent 輸入prompt：{prompt}")
    response = llm.invoke([HumanMessage(content=prompt)])
    logger.info(f"result(raw): {response.content}")
    # 計算與累計 output token 數量
    output_tokens = count_tokens(response.content)
    TOKEN_STATS["decision_agent"]["output"] += output_tokens
    logger.info(
        f"[decision_agent] 輸出 tokens: {output_tokens}, 累計輸出: {TOKEN_STATS['decision_agent']['output']}"
    )

    try:
        parsed_list = extract_first_json_list(response.content)
        result = parsed_list[0] if parsed_list else {}
    except Exception:
        result = {}
    state["guidance_strategy"] = result.get("Guidance_and_Strategy", "")
    return state


# PBL response agent
# 需傳遞 guidance_strategy


def response_agent(state: AgentState) -> AgentState:
    logger.info(f"[response_agent] state id: {id(state)}")
    logger.info(f"state: {state}")

    prompt = prompts.RESPONSE_AGENT_PROMPT.format(
        all_dialogs="\n".join([m.content for m in state["messages"][-10:]]),
        guidance_strategy=state.get("guidance_strategy", ""),
        project_content=state.get("project_content", ""),
        action_plan=state.get("action_plan", ""),
    )
    logger.info(f"📝 ResponseAgent 輸入prompt：{prompt}")
    if "[CURRENT_PROJECT_CONTENT]" in prompt:
        current_project_content = state.get("project_content", "")
        prompt = prompt.replace("[CURRENT_PROJECT_CONTENT]", current_project_content)
    # 計算與累計 input token 數量
    input_tokens = count_tokens(prompt)
    TOKEN_STATS["response_agent"]["input"] += input_tokens
    logger.info(
        f"[response_agent] 輸入 tokens: {input_tokens}, 累計輸入: {TOKEN_STATS['response_agent']['input']}"
    )
    logger.info(f"📝 ResponseAgent 輸入prompt：{prompt}")
    response = llm.invoke([HumanMessage(content=prompt)])
    # 計算與累計 output token 數量
    output_tokens = count_tokens(response.content)
    TOKEN_STATS["response_agent"]["output"] += output_tokens
    logger.info(
        f"[response_agent] 輸出 tokens: {output_tokens}, 累計輸出: {TOKEN_STATS['response_agent']['output']}"
    )
    logger.info(f"📝 ResponseAgent 回覆：{response.content}")
    state["messages"].append(AIMessage(content=response.content))
    state["next_agent"] = None
    return state


# Workflow definition
# 主 workflow： decision_agent 和 response_agent
main_graph_builder = StateGraph(AgentState)
main_graph_builder.add_node("decision_agent", decision_agent)
main_graph_builder.add_node("response_agent", response_agent)
main_graph_builder.set_entry_point("decision_agent")
main_graph_builder.add_edge("decision_agent", "response_agent")

main_graph = main_graph_builder.compile()

# 背景 workflow：summary/score agent
background_graph_builder = StateGraph(AgentState)
background_graph_builder.add_node("summary_agent", summary_agent)
background_graph_builder.add_node("score_agent", score_agent)

background_graph_builder.set_entry_point("summary_agent")
background_graph_builder.add_edge("summary_agent", "score_agent")

background_graph = background_graph_builder.compile()

# 建立 background_tool (模組化) 並設定
background_tool.setup(background_graph, AIMessage, HumanMessage, logger=logger)


def run_background_graph(state):
    logger.info(f"[run_background_graph] state id: {id(state)}")
    session_id = state.get("session_id")
    group_id = state.get("group_id")
    
    for event in background_graph.stream(state):
        if isinstance(event, dict):
            state.update(event)
    
    if session_id:
        # 如果有 group_id，儲存到組別目錄
        if group_id:
            import os
            group_dir = os.path.join(os.getenv("GROUPS_DIR", "groups_data"), group_id)
            os.makedirs(group_dir, exist_ok=True)
            state_path = os.path.join(group_dir, f"state_{session_id}.pkl")
        else:
            # 否則儲存到預設目錄
            state_path = f"state_{session_id}.pkl"
        
        with open(state_path, "wb") as f:
            pickle.dump(state, f)
    
    logger.info("[Thread] 背景 workflow 狀態已更新，已儲存 state")


def run_graph(state):
    logger.info(f"[run_graph] state id: {id(state)}")
    logger.info(f"[run_graph] state: {state}")

    ai_reply = ""
    for event in main_graph.stream(state):
        if isinstance(event, dict):
            state.update(event)
        if "messages" in event:
            for msg in event["messages"]:
                if hasattr(msg, "type") and msg.type == "ai":
                    ai_reply = msg.content
    return ai_reply


# 新增 token 統計與計數函式
TOKEN_STATS = {
    "summary_agent": {"input": 0, "output": 0},
    "score_agent": {"input": 0, "output": 0},
    "decision_agent": {"input": 0, "output": 0},
    "response_agent": {"input": 0, "output": 0},
}


def count_tokens(text: str) -> int:
    try:
        import tiktoken

        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except ImportError:
        logger.warning(
            "tiktoken library not installed, falling back to basic token count."
        )
        return len(text.split())


if __name__ == "__main__":
    from sample_buddy_G import HumanMessage, AIMessage

    def get_initial_state():
        initial_message = AIMessage(
            content="嗨~ 我是你的 SDGs 專案助理。讓我們一起探索世界，了解 SDGs，為我們的地球盡一份心吧！"
        )
        return {
            "messages": [initial_message],
            "next_agent": None,
            "project_content": "",
            "action_plan": "",
            "historical_log": "",
            "current_progress": "",
            "guidance_strategy": "",
            "score": None,
            "next_response": None,
        }

    messages = [HumanMessage(content="我想解決社區的剩食問題。")]
    session_id = str(uuid.uuid4())
    initial_state = {
        "messages": messages,
        "next_agent": None,
        "project_content": "",
        "action_plan": "",
        "historical_log": "",
        "current_progress": "",
        "guidance_strategy": "",
        "score": None,
        "next_response": None,
        "session_id": session_id,
    }
    for event in main_graph.stream(initial_state):
        for agent_state in event.values():
            if "messages" in agent_state:
                for msg in agent_state["messages"]:
                    print(f"{msg.__class__.__name__}: {msg.content}")
    while True:
        user_input = input("你：")
        if user_input.lower() in {"exit", "quit", "結束"}:
            logger.info("✅ 對話結束。")
            break
        messages.append(HumanMessage(content=user_input))
        initial_state["messages"] = messages
        ai_reply = run_graph(initial_state)
        if ai_reply:
            logger.info(f"AI: {ai_reply}")
