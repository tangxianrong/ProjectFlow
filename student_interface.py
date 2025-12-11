# -- coding: utf-8 -*-
"""
學生介面 - 支援多組學生獨立使用
"""
import gradio as gr
import pickle
import uuid
import os
from projectflow_graph import run_graph, HumanMessage, AIMessage
import json
import logging
from group_manager import get_group_manager

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 使用 groups_data 目錄來區分不同組別
GROUPS_DIR = os.getenv("GROUPS_DIR", "groups_data")
os.makedirs(GROUPS_DIR, exist_ok=True)


def _get_group_state_path(group_id: str) -> str:
    """取得組別的狀態檔案路徑"""
    group_dir = os.path.join(GROUPS_DIR, group_id)
    os.makedirs(group_dir, exist_ok=True)
    session_id = get_group_manager().get_group(group_id).session_id if get_group_manager().get_group(group_id) else None
    if session_id:
        return os.path.join(group_dir, f"state_{session_id}.pkl")
    return os.path.join(group_dir, "state.pkl")


def _get_plan_path(group_id: str, session_id: str) -> str:
    """取得組別的計畫書路徑"""
    group_dir = os.path.join(GROUPS_DIR, group_id)
    os.makedirs(group_dir, exist_ok=True)
    return os.path.join(group_dir, f"專案計畫書_{session_id}.md")


def get_initial_state(group_id: str):
    """初始化對話狀態 - 根據組別"""
    session_id = str(uuid.uuid4())
    group_manager = get_group_manager()
    group = group_manager.get_group(group_id)
    
    if not group:
        # 如果組別不存在，自動建立
        group = group_manager.create_group(group_id, f"組別 {group_id}", [])
    
    # 更新組別的 session_id
    group_manager.update_group_session(group_id, session_id)
    
    # 重新取得更新後的 group (避免重複呼叫)
    group = group_manager.get_group(group_id)
    
    initial_message = AIMessage(
        content=f"嗨！{group.group_name}的同學們好！我是你的 SDGs 專案助理——專門協助你規劃與推動永續發展目標專案。讓我們攜手為世界帶來正向改變！請問你在工作或生活中有沒有碰到讓你關心的問題呢，或已經有具體的專案構想呢？\n\n"
    )
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
        "next_agent": "",
        "group_id": group_id
    }


def get_initial_history(group_id: str):
    """取得初始對話歷史"""
    state = get_initial_state(group_id)
    history = []
    for msg in state["messages"]:
        if hasattr(msg, "type") and msg.type == "ai":
            history.append({"role": "assistant", "content": msg.content})
        else:
            history.append({"role": "user", "content": msg.content})
    return history


def chat(user_msg, history, state):
    """處理對話"""
    logger.info(f"[chat] state id: {id(state)}")
    group_id = state.get("group_id")
    session_id = state.get("session_id")
    messages = state.get("messages", [])
    
    # 先讀取最新 state（從組別目錄）
    if group_id and session_id:
        try:
            state_path = _get_group_state_path(group_id)
            logger.info(f"[chat] loading state from file: {state_path}")
            with open(state_path, "rb") as f:
                loaded_state = pickle.load(f)
            if "score_agent" in loaded_state:
                state.update(loaded_state["score_agent"])
            else:
                state.update(loaded_state)
        except FileNotFoundError:
            logger.warning(f"[chat] state file not found: {state_path}, using initial state")
            pass
    
    if messages:
        state["messages"] = messages
    
    logger.info(f"[chat] state: {state}")
    logger.info(f"user_msg: {user_msg}")
    state["messages"].append(HumanMessage(content=user_msg))
    bot_msg = run_graph(state)
    
    # 儲存 state 到組別目錄
    if group_id:
        state_path = _get_group_state_path(group_id)
        with open(state_path, "wb") as f:
            pickle.dump(state, f)
    
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


def clear(group_id):
    """清除對話"""
    state = get_initial_state(group_id)
    return [], "", state


def download_example(state):
    """下載專案計畫書"""
    session_id = state.get("session_id")
    group_id = state.get("group_id")
    
    # 先讀取最新 state
    if group_id and session_id:
        try:
            state_path = _get_group_state_path(group_id)
            with open(state_path, "rb") as f:
                loaded_state = pickle.load(f)
            state.update(loaded_state)
        except FileNotFoundError:
            logger.warning(f"[download_example] state file not found: {state_path}")
            pass
        
        logger.info(f"key of state: {state.keys()}")
        logger.info(state.get("project_content", ""))
    
    plan_path = _get_plan_path(group_id, session_id)
    with open(plan_path, "w", encoding="utf-8") as f:
        f.write(state.get("decision_agent", {}).get("project_content", ""))
    
    return [_get_group_state_path(group_id), plan_path]


def create_student_interface():
    """建立學生介面"""
    with gr.Blocks() as demo:
        gr.Markdown("# SDGs PBL 對話助理 - 學生介面")
        
        # 組別選擇
        with gr.Row():
            group_id_input = gr.Textbox(
                label="組別代碼",
                placeholder="請輸入你的組別代碼 (例如: group_A)",
                value="group_A"
            )
            init_btn = gr.Button("開始使用")
        
        # 對話區域
        chatbox = gr.Chatbot(type='messages', label="對話記錄")
        user_input = gr.Textbox(
            label="請輸入你的問題或想法：",
            placeholder="例如：我想解決社區的剩食問題。",
            lines=2
        )
        
        with gr.Row():
            send_btn = gr.Button("送出", variant="primary")
            clear_btn = gr.Button("清除對話")
        
        # State
        state = gr.State({})
        current_group = gr.State("")
        
        # 下載功能
        with gr.Accordion("下載專案資料", open=False):
            download_btn = gr.Button("產生下載檔案")
            file_output = gr.File(label="下載檔案")
        
        # 初始化組別
        def init_group(group_id):
            state_data = get_initial_state(group_id)
            history = get_initial_history(group_id)
            return history, "", state_data, group_id
        
        init_btn.click(
            init_group,
            [group_id_input],
            [chatbox, user_input, state, current_group]
        )
        
        # 對話功能
        send_btn.click(chat, [user_input, chatbox, state], [chatbox, user_input, state])
        
        # 清除功能
        def clear_with_group(current_group_id):
            if not current_group_id:
                current_group_id = "group_A"
            return clear(current_group_id)
        
        clear_btn.click(clear_with_group, [current_group], [chatbox, user_input, state])
        
        # 下載功能
        download_btn.click(download_example, [state], outputs=file_output)
    
    return demo


if __name__ == "__main__":
    demo = create_student_interface()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
