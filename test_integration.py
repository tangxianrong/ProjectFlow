"""
測試 API Server 的基本功能
"""
import os
import sys
import tempfile

# 設定測試環境
test_dir = tempfile.mkdtemp()
os.environ["GROUPS_DIR"] = test_dir

def test_api_imports():
    """測試 API Server 的 import"""
    print("=" * 50)
    print("測試: API Server Imports")
    print("=" * 50)
    
    try:
        # 測試 FastAPI 應用程式能否被 import
        from api_server import app
        print("✅ 成功 import API server app")
        
        # 檢查路由
        routes = [route.path for route in app.routes]
        print(f"\n已註冊的路由:")
        for route in routes:
            print(f"   - {route}")
        
        # 驗證關鍵路由存在
        assert "/background_update" in routes
        assert "/groups/create" in routes
        assert "/groups/list" in routes
        assert "/teacher/overview" in routes
        assert "/teacher/analyze" in routes
        
        print("\n✅ 所有關鍵路由已註冊")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Import 失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_models_imports():
    """測試資料模型"""
    print("\n" + "=" * 50)
    print("測試: 資料模型")
    print("=" * 50)
    
    try:
        from models import Group, GroupProgress, TeacherAnalysis
        from datetime import datetime
        
        # 測試建立 Group
        group = Group(
            group_id="test_group",
            group_name="測試組別",
            students=["學生1", "學生2"]
        )
        print(f"✅ 成功建立 Group: {group.group_name}")
        
        # 測試建立 GroupProgress
        progress = GroupProgress(
            group_id="test_group",
            group_name="測試組別",
            stage_number=1
        )
        print(f"✅ 成功建立 GroupProgress: 階段 {progress.stage_number}")
        
        # 測試建立 TeacherAnalysis
        analysis = TeacherAnalysis(
            group_id="test_group",
            difficulties=["困難1"],
            suggestions=["建議1"],
            analysis_summary="測試摘要"
        )
        print(f"✅ 成功建立 TeacherAnalysis")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_teacher_agent_imports():
    """測試教師分析 Agent"""
    print("\n" + "=" * 50)
    print("測試: 教師分析 Agent")
    print("=" * 50)
    
    try:
        from teacher_analysis_agent import TeacherAnalysisAgent
        print("✅ 成功 import TeacherAnalysisAgent")
        
        # 檢查方法存在
        methods = ['analyze_group', 'analyze_all_groups', 'compare_groups']
        for method in methods:
            assert hasattr(TeacherAnalysisAgent, method)
            print(f"   - 方法 {method} 存在")
        
        print("\n✅ TeacherAnalysisAgent 結構正確")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interfaces_imports():
    """測試介面檔案"""
    print("\n" + "=" * 50)
    print("測試: 使用者介面")
    print("=" * 50)
    
    try:
        # 測試學生介面
        from student_interface import create_student_interface
        print("✅ 成功 import student_interface")
        
        # 測試教師介面
        from teacher_interface import create_teacher_interface
        print("✅ 成功 import teacher_interface")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """執行所有測試"""
    print("\n" + "=" * 50)
    print("API Server 與介面整合測試")
    print("=" * 50 + "\n")
    
    results = []
    
    results.append(("API Imports", test_api_imports()))
    results.append(("Models", test_models_imports()))
    results.append(("Teacher Agent", test_teacher_agent_imports()))
    results.append(("Interfaces", test_interfaces_imports()))
    
    # 總結
    print("\n" + "=" * 50)
    print("測試總結")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n" + "=" * 50)
        print("✅ 所有整合測試通過！")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ 部分測試失敗")
        print("=" * 50)
    
    # 清理
    import shutil
    try:
        shutil.rmtree(test_dir)
    except:
        pass
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
