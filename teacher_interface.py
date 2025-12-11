# -- coding: utf-8 -*-
"""
教師介面 - 查看並分析各組學生進度
"""
import gradio as gr
import logging
from typing import List
from group_manager import get_group_manager
from teacher_analysis_agent import create_teacher_analysis_agent
from projectflow_graph import llm
import pandas as pd

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化教師分析 Agent
teacher_agent = create_teacher_analysis_agent(llm)


def get_all_groups_overview():
    """取得所有組別的概覽"""
    group_manager = get_group_manager()
    progress_list = group_manager.get_all_progress()
    
    if not progress_list:
        return "目前沒有組別資料", None
    
    # 建立表格資料
    data = []
    for progress in progress_list:
        data.append({
            "組別代碼": progress.group_id,
            "組別名稱": progress.group_name,
            "當前階段": f"階段 {progress.stage_number}",
            "對話數": progress.message_count,
            "最後更新": progress.last_updated.strftime("%Y-%m-%d %H:%M:%S") if progress.last_updated else "N/A"
        })
    
    df = pd.DataFrame(data)
    
    # 統計摘要
    comparison = teacher_agent.compare_groups(progress_list)
    summary = f"""
## 整體概覽

- **總組別數**: {comparison['total_groups']}
- **階段分布**: {comparison['stage_distribution']}
- **需要關注**: {len(comparison.get('needs_attention', []))} 組

### 需要關注的組別：
{chr(10).join(f"- {item}" for item in comparison.get('needs_attention', [])) if comparison.get('needs_attention') else "所有組別目前運作正常"}
"""
    
    return summary, df


def get_group_detail(group_id: str):
    """取得特定組別的詳細資訊"""
    if not group_id:
        return "請選擇組別", "", ""
    
    group_manager = get_group_manager()
    progress = group_manager.get_group_progress(group_id)
    
    if not progress:
        return f"找不到組別: {group_id}", "", ""
    
    # 組別基本資訊
    basic_info = f"""
## {progress.group_name} ({progress.group_id})

### 基本資訊
- **當前階段**: 階段 {progress.stage_number}
- **對話訊息數**: {progress.message_count}
- **最後更新**: {progress.last_updated.strftime("%Y-%m-%d %H:%M:%S") if progress.last_updated else "N/A"}
"""
    
    # 專案內容
    project_info = f"""
### 專案內容
{progress.project_content if progress.project_content else "尚未開始專案"}

### 行動計畫
{progress.action_plan if progress.action_plan else "尚未制定行動計畫"}
"""
    
    # 當前進度與評分
    progress_info = f"""
### 當前進度與評分
{progress.current_progress if progress.current_progress else "尚未評分"}
"""
    
    return basic_info, project_info, progress_info


def analyze_group(group_id: str):
    """分析特定組別並提供建議"""
    if not group_id:
        return "請選擇組別"
    
    group_manager = get_group_manager()
    progress = group_manager.get_group_progress(group_id)
    
    if not progress:
        return f"找不到組別: {group_id}"
    
    # 使用教師分析 Agent 進行分析
    analysis = teacher_agent.analyze_group(progress)
    
    result = f"""
## {progress.group_name} 分析報告

### 整體分析
{analysis.analysis_summary}

### 識別的困難點
{chr(10).join(f"{i+1}. {difficulty}" for i, difficulty in enumerate(analysis.difficulties))}

### 介入建議
{chr(10).join(f"{i+1}. {suggestion}" for i, suggestion in enumerate(analysis.suggestions))}

---
*分析時間: {analysis.generated_at.strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    return result


def analyze_all_groups():
    """分析所有組別"""
    group_manager = get_group_manager()
    progress_list = group_manager.get_all_progress()
    
    if not progress_list:
        return "目前沒有組別資料"
    
    analyses = teacher_agent.analyze_all_groups(progress_list)
    
    results = ["# 所有組別分析報告\n"]
    
    for analysis in analyses:
        progress = next((p for p in progress_list if p.group_id == analysis.group_id), None)
        if progress:
            results.append(f"""
## {progress.group_name} ({progress.group_id})

**當前階段**: 階段 {progress.stage_number} | **對話數**: {progress.message_count}

### 困難點
{chr(10).join(f"- {difficulty}" for difficulty in analysis.difficulties)}

### 建議
{chr(10).join(f"- {suggestion}" for suggestion in analysis.suggestions)}

---
""")
    
    return "\n".join(results)


def create_new_group(group_id: str, group_name: str, students: str):
    """建立新組別"""
    if not group_id or not group_name:
        return "請輸入組別代碼和名稱"
    
    try:
        group_manager = get_group_manager()
        student_list = [s.strip() for s in students.split(",") if s.strip()]
        group = group_manager.create_group(group_id, group_name, student_list)
        return f"成功建立組別: {group.group_name} ({group.group_id})"
    except ValueError as e:
        return f"建立失敗: {str(e)}"
    except Exception as e:
        logger.error(f"建立組別失敗: {e}")
        return f"發生錯誤: {str(e)}"


def get_group_list():
    """取得組別列表供選擇"""
    group_manager = get_group_manager()
    groups = group_manager.list_groups()
    return [g.group_id for g in groups]


def create_teacher_interface():
    """建立教師介面"""
    with gr.Blocks(title="教師介面 - ProjectFlow") as demo:
        gr.Markdown("# 教師介面 - 學生組別進度管理")
        
        with gr.Tabs():
            # Tab 1: 整體概覽
            with gr.Tab("整體概覽"):
                gr.Markdown("## 所有組別概覽")
                refresh_btn = gr.Button("重新整理", variant="primary")
                overview_text = gr.Markdown()
                overview_table = gr.Dataframe()
                
                refresh_btn.click(
                    get_all_groups_overview,
                    outputs=[overview_text, overview_table]
                )
                
                # 批量分析
                gr.Markdown("## 批量分析")
                analyze_all_btn = gr.Button("分析所有組別", variant="secondary")
                all_analysis_output = gr.Markdown()
                
                analyze_all_btn.click(
                    analyze_all_groups,
                    outputs=all_analysis_output
                )
            
            # Tab 2: 組別詳情
            with gr.Tab("組別詳情"):
                gr.Markdown("## 查看特定組別")
                
                with gr.Row():
                    group_dropdown = gr.Dropdown(
                        choices=get_group_list(),
                        label="選擇組別",
                        interactive=True
                    )
                    refresh_groups_btn = gr.Button("更新組別列表")
                
                detail_btn = gr.Button("查看詳情", variant="primary")
                
                basic_info_output = gr.Markdown()
                project_info_output = gr.Markdown()
                progress_info_output = gr.Markdown()
                
                refresh_groups_btn.click(
                    lambda: gr.Dropdown(choices=get_group_list()),
                    outputs=group_dropdown
                )
                
                detail_btn.click(
                    get_group_detail,
                    inputs=group_dropdown,
                    outputs=[basic_info_output, project_info_output, progress_info_output]
                )
            
            # Tab 3: AI 分析建議
            with gr.Tab("AI 分析建議"):
                gr.Markdown("## AI 教師助手分析")
                gr.Markdown("使用 AI 分析組別的學習狀況，並提供介入建議")
                
                with gr.Row():
                    analysis_group_dropdown = gr.Dropdown(
                        choices=get_group_list(),
                        label="選擇要分析的組別",
                        interactive=True
                    )
                    refresh_analysis_groups_btn = gr.Button("更新組別列表")
                
                analyze_btn = gr.Button("開始分析", variant="primary")
                analysis_output = gr.Markdown()
                
                refresh_analysis_groups_btn.click(
                    lambda: gr.Dropdown(choices=get_group_list()),
                    outputs=analysis_group_dropdown
                )
                
                analyze_btn.click(
                    analyze_group,
                    inputs=analysis_group_dropdown,
                    outputs=analysis_output
                )
            
            # Tab 4: 組別管理
            with gr.Tab("組別管理"):
                gr.Markdown("## 建立新組別")
                
                with gr.Row():
                    new_group_id = gr.Textbox(label="組別代碼", placeholder="例如: group_A")
                    new_group_name = gr.Textbox(label="組別名稱", placeholder="例如: 第一組")
                
                new_students = gr.Textbox(
                    label="學生名單 (用逗號分隔)",
                    placeholder="例如: 張三, 李四, 王五",
                    lines=2
                )
                
                create_btn = gr.Button("建立組別", variant="primary")
                create_output = gr.Textbox(label="建立結果")
                
                create_btn.click(
                    create_new_group,
                    inputs=[new_group_id, new_group_name, new_students],
                    outputs=create_output
                )
        
        # 頁面載入時顯示概覽
        demo.load(
            get_all_groups_overview,
            outputs=[overview_text, overview_table]
        )
    
    return demo


if __name__ == "__main__":
    demo = create_teacher_interface()
    demo.launch(server_name="0.0.0.0", server_port=7861, share=False)
