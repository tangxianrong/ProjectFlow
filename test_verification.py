"""
驗證多組學生架構的核心功能（不需要完整依賴）
"""
import os
import sys
import tempfile
import shutil

# 設定測試環境
test_dir = tempfile.mkdtemp()
os.environ["GROUPS_DIR"] = test_dir

def verify_file_structure():
    """驗證檔案結構"""
    print("=" * 50)
    print("驗證 1: 檔案結構")
    print("=" * 50)
    
    required_files = [
        "models.py",
        "group_manager.py",
        "teacher_analysis_agent.py",
        "student_interface.py",
        "teacher_interface.py",
        "api_server.py",
        "README.md"
    ]
    
    base_path = "/home/runner/work/projectflow_agent/projectflow_agent"
    
    for file in required_files:
        file_path = os.path.join(base_path, file)
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"{status} {file}")
        if not exists:
            return False
    
    print("\n✅ 所有核心檔案存在")
    return True

def verify_data_models():
    """驗證資料模型"""
    print("\n" + "=" * 50)
    print("驗證 2: 資料模型")
    print("=" * 50)
    
    try:
        from models import Group, GroupProgress, TeacherAnalysis
        
        # 建立測試資料
        group = Group(
            group_id="verify_group",
            group_name="驗證組別",
            students=["學生1", "學生2", "學生3"]
        )
        
        progress = GroupProgress(
            group_id="verify_group",
            group_name="驗證組別",
            stage_number=2,
            message_count=15
        )
        
        analysis = TeacherAnalysis(
            group_id="verify_group",
            difficulties=["困難1: 問題定義不清", "困難2: 資料收集方向不明確"],
            suggestions=["建議1: 協助聚焦問題", "建議2: 提供資料來源範例"],
            analysis_summary="組別在問題探索階段遇到困難，需要教師適度引導"
        )
        
        # 驗證資料
        assert group.group_id == "verify_group"
        assert len(group.students) == 3
        assert progress.stage_number == 2
        assert progress.message_count == 15
        assert len(analysis.difficulties) == 2
        assert len(analysis.suggestions) == 2
        
        print("✅ Group 模型運作正常")
        print("✅ GroupProgress 模型運作正常")
        print("✅ TeacherAnalysis 模型運作正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_group_manager():
    """驗證組別管理器"""
    print("\n" + "=" * 50)
    print("驗證 3: 組別管理器")
    print("=" * 50)
    
    try:
        from group_manager import GroupManager
        
        manager = GroupManager()
        
        # 建立組別
        group1 = manager.create_group("group_1", "第一組", ["A", "B"])
        group2 = manager.create_group("group_2", "第二組", ["C", "D"])
        group3 = manager.create_group("group_3", "第三組", ["E", "F"])
        
        # 驗證列表
        groups = manager.list_groups()
        assert len(groups) == 3
        print(f"✅ 成功建立並管理 {len(groups)} 個組別")
        
        # 驗證取得
        g1 = manager.get_group("group_1")
        assert g1.group_name == "第一組"
        print("✅ 組別查詢功能正常")
        
        # 驗證更新 session
        manager.update_group_session("group_1", "session_abc")
        g1_updated = manager.get_group("group_1")
        assert g1_updated.session_id == "session_abc"
        print("✅ Session 更新功能正常")
        
        # 驗證進度
        progress = manager.get_group_progress("group_1")
        assert progress.group_id == "group_1"
        print("✅ 進度查詢功能正常")
        
        # 驗證批量進度
        all_progress = manager.get_all_progress()
        assert len(all_progress) == 3
        print(f"✅ 批量進度查詢正常（{len(all_progress)} 組）")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_data_isolation():
    """驗證資料隔離"""
    print("\n" + "=" * 50)
    print("驗證 4: 資料隔離")
    print("=" * 50)
    
    try:
        from group_manager import GroupManager
        import os
        
        manager = GroupManager()
        
        # 檢查組別目錄
        group_ids = ["group_1", "group_2", "group_3"]
        
        for group_id in group_ids:
            path = manager.get_group_state_path(group_id)
            group_dir = os.path.dirname(path)
            
            # 確認每個組別都有獨立目錄
            assert group_id in group_dir
            print(f"✅ {group_id} 有獨立目錄: {group_dir}")
        
        # 確認目錄不同
        paths = [manager.get_group_state_path(gid) for gid in group_ids]
        unique_dirs = set(os.path.dirname(p) for p in paths)
        assert len(unique_dirs) == len(group_ids)
        print(f"✅ 各組資料完全隔離（{len(unique_dirs)} 個獨立目錄）")
        
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_readme():
    """驗證 README 更新"""
    print("\n" + "=" * 50)
    print("驗證 5: README 文件")
    print("=" * 50)
    
    try:
        with open("/home/runner/work/projectflow_agent/projectflow_agent/README.md", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 檢查關鍵內容
        required_sections = [
            "多組學生支援",
            "教師端架構",
            "student_interface.py",
            "teacher_interface.py",
            "TeacherAnalysisAgent",
            "groups_data"
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ README 包含: {section}")
            else:
                print(f"❌ README 缺少: {section}")
                return False
        
        print("\n✅ README 已完整更新")
        return True
        
    except Exception as e:
        print(f"❌ 驗證失敗: {e}")
        return False

def main():
    """執行所有驗證"""
    print("\n" + "=" * 50)
    print("多組學生架構核心功能驗證")
    print("=" * 50 + "\n")
    
    results = []
    
    results.append(("檔案結構", verify_file_structure()))
    results.append(("資料模型", verify_data_models()))
    results.append(("組別管理器", verify_group_manager()))
    results.append(("資料隔離", verify_data_isolation()))
    results.append(("README 文件", verify_readme()))
    
    # 清理
    try:
        shutil.rmtree(test_dir)
    except:
        pass
    
    # 總結
    print("\n" + "=" * 50)
    print("驗證總結")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "=" * 50)
        print("✅ 所有核心功能驗證通過！")
        print("=" * 50)
        print("\n功能摘要:")
        print("- ✅ 支援多組學生獨立使用")
        print("- ✅ 各組資料完全隔離")
        print("- ✅ 組別管理功能完整")
        print("- ✅ 資料模型定義清晰")
        print("- ✅ 文件已完整更新")
    else:
        print("\n" + "=" * 50)
        print("❌ 部分驗證失敗")
        print("=" * 50)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
