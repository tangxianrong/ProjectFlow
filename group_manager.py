"""
組別管理模組
負責管理多組學生的資料與狀態
"""
import os
import json
import pickle
from typing import Dict, List, Optional
from datetime import datetime, timezone
from models import Group, GroupProgress
import logging

logger = logging.getLogger(__name__)

# 儲存目錄
GROUPS_DIR = os.getenv("GROUPS_DIR", "groups_data")
os.makedirs(GROUPS_DIR, exist_ok=True)


class GroupManager:
    """組別管理器"""
    
    def __init__(self):
        self.groups_file = os.path.join(GROUPS_DIR, "groups.json")
        self._load_groups()
    
    def _load_groups(self):
        """載入組別資料"""
        if os.path.exists(self.groups_file):
            try:
                with open(self.groups_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.groups: Dict[str, Group] = {
                        k: Group(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.error(f"載入組別資料失敗: {e}")
                self.groups = {}
        else:
            self.groups = {}
    
    def _save_groups(self):
        """儲存組別資料"""
        try:
            data = {
                k: v.model_dump(mode='json') for k, v in self.groups.items()
            }
            with open(self.groups_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            logger.error(f"儲存組別資料失敗: {e}")
    
    def create_group(self, group_id: str, group_name: str, students: List[str] = None) -> Group:
        """建立新組別"""
        if group_id in self.groups:
            raise ValueError(f"組別 {group_id} 已存在")
        
        group = Group(
            group_id=group_id,
            group_name=group_name,
            students=students or []
        )
        self.groups[group_id] = group
        self._save_groups()
        logger.info(f"建立組別: {group_id} - {group_name}")
        return group
    
    def get_group(self, group_id: str) -> Optional[Group]:
        """取得組別資訊"""
        return self.groups.get(group_id)
    
    def list_groups(self) -> List[Group]:
        """列出所有組別"""
        return list(self.groups.values())
    
    def update_group_session(self, group_id: str, session_id: str):
        """更新組別的 session ID"""
        if group_id not in self.groups:
            raise ValueError(f"組別 {group_id} 不存在")
        
        self.groups[group_id].session_id = session_id
        self._save_groups()
    
    def get_group_state_path(self, group_id: str) -> str:
        """取得組別的狀態檔案路徑"""
        group_dir = os.path.join(GROUPS_DIR, group_id)
        os.makedirs(group_dir, exist_ok=True)
        return os.path.join(group_dir, "state.pkl")
    
    def get_group_progress(self, group_id: str) -> Optional[GroupProgress]:
        """取得組別進度"""
        state_path = self.get_group_state_path(group_id)
        group = self.get_group(group_id)
        
        if not group:
            return None
        
        # 讀取狀態檔案
        if os.path.exists(state_path):
            try:
                with open(state_path, "rb") as f:
                    state = pickle.load(f)
                
                # 提取進度資訊
                return GroupProgress(
                    group_id=group_id,
                    group_name=group.group_name,
                    stage_number=state.get("stage_number", 1),
                    project_content=state.get("project_content", ""),
                    action_plan=state.get("action_plan", ""),
                    current_progress=state.get("current_progress", ""),
                    last_updated=datetime.now(timezone.utc),
                    message_count=len(state.get("messages", []))
                )
            except Exception as e:
                logger.error(f"讀取組別 {group_id} 狀態失敗: {e}")
        
        # 如果沒有狀態檔案，返回初始進度
        return GroupProgress(
            group_id=group_id,
            group_name=group.group_name
        )
    
    def get_all_progress(self) -> List[GroupProgress]:
        """取得所有組別的進度"""
        progress_list = []
        for group_id in self.groups.keys():
            progress = self.get_group_progress(group_id)
            if progress:
                progress_list.append(progress)
        return progress_list


# 全域實例
_group_manager = None


def get_group_manager() -> GroupManager:
    """取得組別管理器單例"""
    global _group_manager
    if _group_manager is None:
        _group_manager = GroupManager()
    return _group_manager
