from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn
from projectflow_graph import background_graph, AIMessage, HumanMessage, logger
import background_tool
from typing import Optional, List
from group_manager import get_group_manager
from teacher_analysis_agent import create_teacher_analysis_agent
from projectflow_graph import llm

# 初始化工具（若未在 import 時 setup）
background_tool.setup(background_graph, AIMessage, HumanMessage, logger=logger)

# 初始化教師分析 Agent
teacher_agent = create_teacher_analysis_agent(llm)

# API_KEY = "YOUR_INTERNAL_KEY"  # 放環境變數更安全

class BackgroundUpdateRequest(BaseModel):
    session_id: str
    prev_ai_prompt: str
    user_prompt: str
    group_id: Optional[str] = None  # 新增組別 ID 支援

class CreateGroupRequest(BaseModel):
    group_id: str
    group_name: str
    students: List[str] = []

class GroupAnalysisRequest(BaseModel):
    group_id: str

app = FastAPI(title="ProjectFlow Agent API", version="2.0.0")

@app.post("/background_update")
def background_update(req: BackgroundUpdateRequest):
    """背景更新工具 - 支援組別
    
    Note: group_id 用於前端識別，實際處理使用 session_id
    各組的 session 資料已在 projectflow_graph 中根據 group_id 獨立儲存
    """
    # if x_api_key != API_KEY:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return background_tool.background_update_tool(
        session_id=req.session_id,
        prev_ai_prompt=req.prev_ai_prompt,
        user_prompt=req.user_prompt
    )

@app.post("/groups/create")
def create_group(req: CreateGroupRequest):
    """建立新組別"""
    try:
        group_manager = get_group_manager()
        group = group_manager.create_group(
            group_id=req.group_id,
            group_name=req.group_name,
            students=req.students
        )
        return {
            "success": True,
            "group_id": group.group_id,
            "group_name": group.group_name,
            "students": group.students
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/groups/list")
def list_groups():
    """列出所有組別"""
    group_manager = get_group_manager()
    groups = group_manager.list_groups()
    return {
        "groups": [
            {
                "group_id": g.group_id,
                "group_name": g.group_name,
                "students": g.students,
                "session_id": g.session_id
            }
            for g in groups
        ]
    }

@app.get("/groups/{group_id}/progress")
def get_group_progress(group_id: str):
    """取得組別進度"""
    group_manager = get_group_manager()
    progress = group_manager.get_group_progress(group_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail=f"組別 {group_id} 不存在")
    
    return {
        "group_id": progress.group_id,
        "group_name": progress.group_name,
        "stage_number": progress.stage_number,
        "project_content": progress.project_content,
        "action_plan": progress.action_plan,
        "current_progress": progress.current_progress,
        "message_count": progress.message_count,
        "last_updated": progress.last_updated.isoformat() if progress.last_updated else None
    }

@app.get("/teacher/overview")
def get_teacher_overview():
    """取得教師總覽"""
    group_manager = get_group_manager()
    progress_list = group_manager.get_all_progress()
    
    comparison = teacher_agent.compare_groups(progress_list)
    
    return {
        "total_groups": comparison["total_groups"],
        "stage_distribution": comparison["stage_distribution"],
        "needs_attention": comparison.get("needs_attention", []),
        "summary": comparison["summary"],
        "groups": [
            {
                "group_id": p.group_id,
                "group_name": p.group_name,
                "stage_number": p.stage_number,
                "message_count": p.message_count
            }
            for p in progress_list
        ]
    }

@app.post("/teacher/analyze")
def analyze_group(req: GroupAnalysisRequest):
    """分析特定組別"""
    group_manager = get_group_manager()
    progress = group_manager.get_group_progress(req.group_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail=f"組別 {req.group_id} 不存在")
    
    analysis = teacher_agent.analyze_group(progress)
    
    return {
        "group_id": analysis.group_id,
        "difficulties": analysis.difficulties,
        "suggestions": analysis.suggestions,
        "analysis_summary": analysis.analysis_summary,
        "generated_at": analysis.generated_at.isoformat()
    }

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)