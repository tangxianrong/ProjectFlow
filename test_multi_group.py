"""
測試多組學生架構的基本功能
"""
import os
import sys
import tempfile
import shutil

# 設定測試環境
test_dir = tempfile.mkdtemp()
os.environ["GROUPS_DIR"] = test_dir
os.environ["SESSION_DIR"] = test_dir

from group_manager import GroupManager, get_group_manager
from models import Group, GroupProgress

def test_create_group():
    """測試建立組別"""
    print("=" * 50)
    print("測試 1: 建立組別")
    print("=" * 50)
    
    manager = GroupManager()
    
    # 建立組別
    group = manager.create_group(
        group_id="test_group_1",
        group_name="測試組別一",
        students=["學生A", "學生B", "學生C"]
    )
    
    assert group.group_id == "test_group_1"
    assert group.group_name == "測試組別一"
    assert len(group.students) == 3
    print(f"✅ 成功建立組別: {group.group_name}")
    print(f"   組別代碼: {group.group_id}")
    print(f"   學生名單: {', '.join(group.students)}")
    
    # 測試重複建立
    try:
        manager.create_group("test_group_1", "重複組別")
        assert False, "應該拋出 ValueError"
    except ValueError as e:
        print(f"✅ 正確阻止重複建立: {e}")
    
    print()

def test_list_groups():
    """測試列出組別"""
    print("=" * 50)
    print("測試 2: 列出組別")
    print("=" * 50)
    
    manager = GroupManager()
    
    # 建立多個組別
    manager.create_group("group_A", "第一組", ["張三", "李四"])
    manager.create_group("group_B", "第二組", ["王五", "趙六"])
    
    groups = manager.list_groups()
    assert len(groups) >= 2
    print(f"✅ 成功列出 {len(groups)} 個組別")
    for g in groups:
        print(f"   - {g.group_name} ({g.group_id})")
    
    print()

def test_get_group():
    """測試取得組別"""
    print("=" * 50)
    print("測試 3: 取得組別資訊")
    print("=" * 50)
    
    manager = GroupManager()
    
    # 取得存在的組別
    group = manager.get_group("group_A")
    assert group is not None
    assert group.group_name == "第一組"
    print(f"✅ 成功取得組別: {group.group_name}")
    
    # 取得不存在的組別
    group = manager.get_group("non_existent")
    assert group is None
    print("✅ 正確處理不存在的組別")
    
    print()

def test_update_session():
    """測試更新 session ID"""
    print("=" * 50)
    print("測試 4: 更新 Session ID")
    print("=" * 50)
    
    manager = GroupManager()
    
    # 更新 session ID
    manager.update_group_session("group_A", "test_session_123")
    
    group = manager.get_group("group_A")
    assert group.session_id == "test_session_123"
    print(f"✅ 成功更新 Session ID: {group.session_id}")
    
    print()

def test_group_progress():
    """測試組別進度"""
    print("=" * 50)
    print("測試 5: 組別進度")
    print("=" * 50)
    
    manager = GroupManager()
    
    # 取得進度（沒有狀態檔案時）
    progress = manager.get_group_progress("group_A")
    assert progress is not None
    assert progress.group_id == "group_A"
    assert progress.stage_number == 1  # 預設階段
    print(f"✅ 成功取得初始進度")
    print(f"   組別: {progress.group_name}")
    print(f"   階段: {progress.stage_number}")
    print(f"   訊息數: {progress.message_count}")
    
    print()

def test_get_all_progress():
    """測試取得所有組別進度"""
    print("=" * 50)
    print("測試 6: 取得所有組別進度")
    print("=" * 50)
    
    manager = GroupManager()
    
    all_progress = manager.get_all_progress()
    assert len(all_progress) >= 2
    print(f"✅ 成功取得 {len(all_progress)} 個組別的進度")
    for p in all_progress:
        print(f"   - {p.group_name}: 階段 {p.stage_number}, {p.message_count} 訊息")
    
    print()

def test_singleton():
    """測試單例模式"""
    print("=" * 50)
    print("測試 7: 單例模式")
    print("=" * 50)
    
    manager1 = get_group_manager()
    manager2 = get_group_manager()
    
    assert manager1 is manager2
    print("✅ 確認 GroupManager 為單例模式")
    
    print()

def cleanup():
    """清理測試資料"""
    print("=" * 50)
    print("清理測試資料")
    print("=" * 50)
    
    try:
        shutil.rmtree(test_dir)
        print(f"✅ 已清理測試目錄: {test_dir}")
    except Exception as e:
        print(f"⚠️ 清理失敗: {e}")
    
    print()

def main():
    """執行所有測試"""
    print("\n" + "=" * 50)
    print("開始測試多組學生架構")
    print("=" * 50 + "\n")
    
    try:
        test_create_group()
        test_list_groups()
        test_get_group()
        test_update_session()
        test_group_progress()
        test_get_all_progress()
        test_singleton()
        
        print("=" * 50)
        print("✅ 所有測試通過！")
        print("=" * 50)
        
    except AssertionError as e:
        print("\n" + "=" * 50)
        print(f"❌ 測試失敗: {e}")
        print("=" * 50)
        return False
    
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return False
    
    finally:
        cleanup()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
