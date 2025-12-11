"""
資料模型定義
支援多組學生與教師介面的資料結構
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class Group(BaseModel):
    """學生組別資料模型"""
    group_id: str = Field(..., description="組別唯一識別碼")
    group_name: str = Field(..., description="組別名稱")
    students: List[str] = Field(default_factory=list, description="學生名單")
    created_at: datetime = Field(default_factory=datetime.now, description="建立時間")
    session_id: Optional[str] = Field(None, description="當前對話 session ID")


class GroupProgress(BaseModel):
    """組別進度資訊"""
    group_id: str = Field(..., description="組別 ID")
    group_name: str = Field(..., description="組別名稱")
    stage_number: int = Field(default=1, description="當前階段編號")
    project_content: str = Field(default="", description="專案內容")
    action_plan: str = Field(default="", description="行動計畫")
    current_progress: str = Field(default="", description="當前進度與評分")
    last_updated: datetime = Field(default_factory=datetime.now, description="最後更新時間")
    message_count: int = Field(default=0, description="對話訊息數")


class TeacherAnalysis(BaseModel):
    """教師分析結果"""
    group_id: str = Field(..., description="組別 ID")
    difficulties: List[str] = Field(default_factory=list, description="識別的困難點")
    suggestions: List[str] = Field(default_factory=list, description="介入建議")
    analysis_summary: str = Field(default="", description="分析摘要")
    generated_at: datetime = Field(default_factory=datetime.now, description="分析時間")
