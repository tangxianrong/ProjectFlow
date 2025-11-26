#-- coding: utf-8 -*-
import gradio as gr
import pickle
import uuid
import os
from projectflow_graph import run_graph, HumanMessage, AIMessage
import json
import logging  # 新增

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

SESSION_DIR = os.getenv("SESSION_DIR", "session_data")
os.makedirs(SESSION_DIR, exist_ok=True)

def _state_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"state_{session_id}.pkl")

def _plan_path(session_id: str) -> str:
    return os.path.join(SESSION_DIR, f"專案計畫書_{session_id}.md")

# 初始化對話狀態
def get_initial_state():
    session_id = str(uuid.uuid4())
    initial_message = AIMessage(content=f"{session_id}嗨！我是你的 SDGs 專案助理——專門協助你規劃與推動永續發展目標專案。讓我們攜手為世界帶來正向改變！請問你在工作或生活中有沒有碰到讓你關心的問題呢，或已經有具體的專案構想呢？\n\n")
    return {
        "messages": [initial_message],
        "project_content": "",
        "action_plan": "",
        "historical_log": "",
        "current_progress": "",
        "guidance_strategy": "",
        "score": "",
        "next_response": "",
        "session_id": session_id,
        "next_agent": ""
    }

def get_initial_history():
    state = get_initial_state()
    history = []
    for msg in state["messages"]:
        if hasattr(msg, "type") and msg.type == "ai":
            history.append({"role": "assistant", "content": msg.content})
        else:
            history.append({"role": "user", "content": msg.content})
    return history

def chat(user_msg, history, state):
    logger.info(f"[chat] state id: {id(state)}")
    session_id = state.get("session_id")
    messages = state.get("messages", [])
    # 先讀取最新 state
    if session_id:
        try:
            logger.info(f"[chat] loading state from file: {_state_path(session_id)}")
            with open(_state_path(session_id), "rb") as f:
                loaded_state = pickle.load(f)
            if "score_agent" in loaded_state:
                state.update(loaded_state["score_agent"])
            else:
                state.update(loaded_state)
        except FileNotFoundError:
            logger.warning(f"[chat] state file not found: {_state_path(session_id)}, using initial state")
            pass
    if messages:
        state["messages"] = messages
    logger.info(f"[chat] state: {state}")
    logger.info(f"user_msg: {user_msg}")
    state["messages"].append(HumanMessage(content=user_msg))
    bot_msg = run_graph(state)
    # 依據 state["messages"] 重新組合歷史
    history = []
    for msg in state["messages"]:
        if hasattr(msg, "type") and msg.type == "ai":
            logger.info(f"[chat] AI message: {msg.content}")
            history.append({"role": "assistant", "content": msg.content})
        else:
            logger.info(f"[chat] User message: {msg.content}")
            history.append({"role": "user", "content": msg.content})
    return history, "", state

def clear():
    state = get_initial_state()
    return [], "", state

# 下載 state 為 JSON 檔案
def download_state(state):
    # 轉換 messages 為可序列化格式
    serializable_state = state.copy()
    serializable_state["messages"] = [
        {"type": getattr(m, "type", "user"), "content": m.content} for m in state["messages"]
    ]
    json_str = json.dumps(serializable_state, ensure_ascii=False, indent=2)
    return json_str

# 上傳 JSON 檔案並更新 state
def upload_state(file):
    try:
        data = json.load(file)
        # 轉換 messages 回 AIMessage/HumanMessage
        messages = []
        for m in data.get("messages", []):
            if m.get("type") == "ai":
                messages.append(AIMessage(content=m["content"]))
            else:
                messages.append(HumanMessage(content=m["content"]))
        data["messages"] = messages
        # 產生新的 session_id
        session_id = str(uuid.uuid4())
        data["session_id"] = session_id
        return [], "", data
    except Exception as e:
        # 若格式錯誤，回傳初始 state
        state = get_initial_state()
        return [], f"上傳失敗: {e}", state



def download_example(state):
    session_id = state.get("session_id")
    # 先讀取最新 state
    if session_id:
        try:
            with open(_state_path(session_id), "rb") as f:
                loaded_state = pickle.load(f)
            state.update(loaded_state)
        except FileNotFoundError:
            logger.warning(f"[download_example] state file not found: {_state_path(session_id)}")
            pass
        logger.info(f"key of state: {state.keys()}")
        logger.info(state.get("project_content", ""))
    with open(_plan_path(session_id), "w", encoding="utf-8") as f:
        f.write(state.get("decision_agent", {}).get("project_content", ""))
    return [_state_path(session_id), _plan_path(session_id)]

with gr.Blocks() as demo:
    gr.Markdown("# SDGs PBL 對話助理")
    chatbox = gr.Chatbot(type='messages', value=get_initial_history())
    user_input = gr.Textbox(label="請輸入你的問題或想法：", placeholder="例如：我想解決社區的剩食問題。", lines=2)
    send_btn = gr.Button("送出")
    clear_btn = gr.Button("清除對話")
    state = gr.State(get_initial_state())


    upload_file = gr.File(label="上傳pickle", file_types=[".pkl"])

    send_btn.click(chat, [user_input, chatbox, state], [chatbox, user_input, state])
    clear_btn.click(clear, [], [chatbox, user_input, state])

    btn = gr.Button("點我產生下載檔案")
    file_output = gr.File()
    btn.click(download_example, [state], outputs=file_output)



    # 上傳 callback: 解析 JSON 並更新 state
    upload_file.change(upload_state, [upload_file], [chatbox, user_input, state])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
