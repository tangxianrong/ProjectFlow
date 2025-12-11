"""
教師分析 Agent
協助教師分析各組學生的學習狀況並提供介入建議
"""
import logging
from typing import Dict, List, Any
from langchain.schema import HumanMessage
from models import TeacherAnalysis, GroupProgress

logger = logging.getLogger(__name__)


TEACHER_ANALYSIS_PROMPT = """
你是教師分析助手 TeacherAnalysisAgent，專門協助教師了解學生組別在 PBL (Project-Based Learning) 專案學習中的困難與需求。

你的主要任務是：
1. 分析學生組別當前的學習狀態與進度
2. 識別學生可能遇到的困難點
3. 提供具體的教師介入建議

分析規則：
1. 困難點識別：
   - 檢查當前階段與預期進度是否匹配
   - 評估學生在各評分項目上的表現
   - 識別學生可能卡住或需要協助的地方
   - 分析對話內容中的猶豫、困惑或重複提問

2. 介入建議：
   - 提供具體、可執行的教師介入方式
   - 建議何時介入最為適當
   - 說明如何引導而不是直接給答案
   - 考慮學生的自主學習空間

3. 分析原則：
   - 關注學習過程而非結果
   - 尊重學生的探索過程
   - 提供支持性而非評價性的建議
   - 考慮組別的整體學習脈絡

輸入資訊：
- 組別名稱：{group_name}
- 當前階段：階段 {stage_number}
- 專案內容：{project_content}
- 行動計畫：{action_plan}
- 當前進度與評分：{current_progress}
- 對話訊息數：{message_count}

請回傳 JSON 格式的分析結果：
{{
    "difficulties": [
        "困難點1的具體描述",
        "困難點2的具體描述"
    ],
    "suggestions": [
        "建議1：具體的介入方式",
        "建議2：具體的介入方式"
    ],
    "analysis_summary": "整體分析摘要，包含組別目前的學習狀態、主要挑戰、以及教師可以提供的支持方向"
}}

請回覆：
"""


class TeacherAnalysisAgent:
    """教師分析 Agent"""
    
    def __init__(self, llm):
        """
        初始化教師分析 Agent
        
        Args:
            llm: Language model instance (來自 projectflow_graph)
        """
        self.llm = llm
    
    def analyze_group(self, progress: GroupProgress) -> TeacherAnalysis:
        """
        分析單一組別的學習狀況
        
        Args:
            progress: GroupProgress 物件，包含組別的進度資訊
            
        Returns:
            TeacherAnalysis 物件，包含分析結果
        """
        logger.info(f"[TeacherAnalysisAgent] 分析組別: {progress.group_name}")
        
        # 建構分析提示
        prompt = TEACHER_ANALYSIS_PROMPT.format(
            group_name=progress.group_name,
            stage_number=progress.stage_number,
            project_content=progress.project_content or "尚未開始",
            action_plan=progress.action_plan or "尚未制定",
            current_progress=progress.current_progress or "尚未評分",
            message_count=progress.message_count
        )
        
        try:
            # 呼叫 LLM 進行分析
            response = self.llm.invoke([HumanMessage(content=prompt)])
            logger.info(f"[TeacherAnalysisAgent] LLM 回應: {response.content}")
            
            # 解析回應
            import json
            import re
            
            # 嘗試提取 JSON
            json_match = re.search(r'\{[\s\S]*\}', response.content)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                # 如果無法解析，返回預設結果
                result = {
                    "difficulties": ["分析資料不足，建議與學生進行更多對話"],
                    "suggestions": ["持續關注學生的探索過程"],
                    "analysis_summary": "目前資料不足，需要更多對話紀錄才能進行深入分析。"
                }
            
            return TeacherAnalysis(
                group_id=progress.group_id,
                difficulties=result.get("difficulties", []),
                suggestions=result.get("suggestions", []),
                analysis_summary=result.get("analysis_summary", "")
            )
        
        except Exception as e:
            logger.error(f"[TeacherAnalysisAgent] 分析失敗: {e}")
            
            # 返回基本分析
            return TeacherAnalysis(
                group_id=progress.group_id,
                difficulties=["分析過程發生錯誤"],
                suggestions=["建議檢查系統設定或與技術支援聯繫"],
                analysis_summary=f"分析過程發生錯誤: {str(e)}"
            )
    
    def analyze_all_groups(self, progress_list: List[GroupProgress]) -> List[TeacherAnalysis]:
        """
        分析所有組別的學習狀況
        
        Args:
            progress_list: GroupProgress 列表
            
        Returns:
            TeacherAnalysis 列表
        """
        analyses = []
        for progress in progress_list:
            analysis = self.analyze_group(progress)
            analyses.append(analysis)
        return analyses
    
    def compare_groups(self, progress_list: List[GroupProgress]) -> Dict[str, Any]:
        """
        比較不同組別的進度與狀況
        
        Args:
            progress_list: GroupProgress 列表
            
        Returns:
            比較結果字典
        """
        if not progress_list:
            return {
                "total_groups": 0,
                "stage_distribution": {},
                "summary": "目前沒有組別資料"
            }
        
        # 統計各階段的組別數量
        stage_distribution = {}
        for progress in progress_list:
            stage = progress.stage_number
            stage_distribution[stage] = stage_distribution.get(stage, 0) + 1
        
        # 識別需要關注的組別
        needs_attention = []
        for progress in progress_list:
            # 如果對話數很少，可能需要關注
            if progress.message_count < 5:
                needs_attention.append(f"{progress.group_name} (對話數不足)")
            # 如果長時間停留在同一階段（這裡簡化處理）
            elif progress.stage_number == 1 and progress.message_count > 20:
                needs_attention.append(f"{progress.group_name} (可能在階段1遇到困難)")
        
        return {
            "total_groups": len(progress_list),
            "stage_distribution": stage_distribution,
            "needs_attention": needs_attention,
            "summary": f"共有 {len(progress_list)} 組。階段分布: {stage_distribution}。需要關注: {len(needs_attention)} 組。"
        }


def create_teacher_analysis_agent(llm):
    """
    建立教師分析 Agent 實例
    
    Args:
        llm: Language model instance
        
    Returns:
        TeacherAnalysisAgent 實例
    """
    return TeacherAnalysisAgent(llm)
