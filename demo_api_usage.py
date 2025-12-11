#!/usr/bin/env python3
"""
示範多組學生架構的範例程式
展示如何使用 API 管理組別與查看進度
"""
import requests
import json
from typing import Dict, Any

# API 基礎 URL
BASE_URL = "http://localhost:8000"


def create_group(group_id: str, group_name: str, students: list) -> Dict[str, Any]:
    """建立新組別"""
    print(f"\n{'='*50}")
    print(f"建立組別: {group_name} ({group_id})")
    print(f"{'='*50}")
    
    response = requests.post(f"{BASE_URL}/groups/create", json={
        "group_id": group_id,
        "group_name": group_name,
        "students": students
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 成功建立組別")
        print(f"   組別代碼: {result['group_id']}")
        print(f"   組別名稱: {result['group_name']}")
        print(f"   學生名單: {', '.join(result['students'])}")
        return result
    else:
        print(f"❌ 建立失敗: {response.text}")
        return {}


def list_groups() -> Dict[str, Any]:
    """列出所有組別"""
    print(f"\n{'='*50}")
    print("列出所有組別")
    print(f"{'='*50}")
    
    response = requests.get(f"{BASE_URL}/groups/list")
    
    if response.status_code == 200:
        result = response.json()
        groups = result.get("groups", [])
        
        if groups:
            print(f"共有 {len(groups)} 個組別:")
            for group in groups:
                print(f"  - {group['group_name']} ({group['group_id']})")
                if group.get('students'):
                    print(f"    成員: {', '.join(group['students'])}")
        else:
            print("目前沒有組別")
        
        return result
    else:
        print(f"❌ 查詢失敗: {response.text}")
        return {}


def get_group_progress(group_id: str) -> Dict[str, Any]:
    """取得組別進度"""
    print(f"\n{'='*50}")
    print(f"查詢組別進度: {group_id}")
    print(f"{'='*50}")
    
    response = requests.get(f"{BASE_URL}/groups/{group_id}/progress")
    
    if response.status_code == 200:
        result = response.json()
        print(f"組別名稱: {result['group_name']}")
        print(f"當前階段: 階段 {result['stage_number']}")
        print(f"對話訊息數: {result['message_count']}")
        
        if result.get('project_content'):
            print(f"\n專案內容:")
            print(result['project_content'][:200] + "..." if len(result['project_content']) > 200 else result['project_content'])
        
        return result
    else:
        print(f"❌ 查詢失敗: {response.text}")
        return {}


def get_teacher_overview() -> Dict[str, Any]:
    """取得教師總覽"""
    print(f"\n{'='*50}")
    print("教師總覽")
    print(f"{'='*50}")
    
    response = requests.get(f"{BASE_URL}/teacher/overview")
    
    if response.status_code == 200:
        result = response.json()
        print(f"總組別數: {result['total_groups']}")
        print(f"階段分布: {result['stage_distribution']}")
        
        if result.get('needs_attention'):
            print(f"\n需要關注的組別:")
            for item in result['needs_attention']:
                print(f"  - {item}")
        
        print(f"\n組別列表:")
        for group in result.get('groups', []):
            print(f"  - {group['group_name']}: 階段 {group['stage_number']}, {group['message_count']} 訊息")
        
        return result
    else:
        print(f"❌ 查詢失敗: {response.text}")
        return {}


def analyze_group(group_id: str) -> Dict[str, Any]:
    """分析組別"""
    print(f"\n{'='*50}")
    print(f"AI 分析組別: {group_id}")
    print(f"{'='*50}")
    
    response = requests.post(f"{BASE_URL}/teacher/analyze", json={
        "group_id": group_id
    })
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n分析摘要:")
        print(result['analysis_summary'])
        
        print(f"\n識別的困難點:")
        for i, difficulty in enumerate(result['difficulties'], 1):
            print(f"  {i}. {difficulty}")
        
        print(f"\n介入建議:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
        
        return result
    else:
        print(f"❌ 分析失敗: {response.text}")
        return {}


def demo_scenario():
    """示範完整情境"""
    print("\n" + "="*50)
    print("ProjectFlow 多組學生架構示範")
    print("="*50)
    print("\n請確保 API 伺服器正在運行 (port 8000)")
    print("啟動方式: uv run api_server.py")
    
    input("\n按 Enter 繼續...")
    
    # 1. 建立組別
    print("\n\n【步驟 1】建立測試組別")
    create_group("demo_group_1", "示範第一組", ["張三", "李四", "王五"])
    create_group("demo_group_2", "示範第二組", ["趙六", "錢七", "孫八"])
    
    input("\n按 Enter 繼續...")
    
    # 2. 列出組別
    print("\n\n【步驟 2】列出所有組別")
    list_groups()
    
    input("\n按 Enter 繼續...")
    
    # 3. 查詢進度
    print("\n\n【步驟 3】查詢組別進度")
    get_group_progress("demo_group_1")
    
    input("\n按 Enter 繼續...")
    
    # 4. 教師總覽
    print("\n\n【步驟 4】教師總覽")
    get_teacher_overview()
    
    input("\n按 Enter 繼續...")
    
    # 5. AI 分析（這個會呼叫 LLM，需要正確設定）
    print("\n\n【步驟 5】AI 分析組別")
    print("（此步驟需要 LLM 設定，可能需要一些時間）")
    
    try:
        analyze_group("demo_group_1")
    except Exception as e:
        print(f"⚠️ AI 分析失敗（可能需要設定 LLM）: {e}")
    
    print("\n" + "="*50)
    print("示範完成！")
    print("="*50)
    print("\n你可以:")
    print("- 開啟學生介面 (port 7860) 使用組別代碼 'demo_group_1' 或 'demo_group_2'")
    print("- 開啟教師介面 (port 7861) 查看組別狀態")


if __name__ == "__main__":
    try:
        demo_scenario()
    except requests.exceptions.ConnectionError:
        print("\n❌ 錯誤: 無法連接到 API 伺服器")
        print("請先啟動 API 伺服器: uv run api_server.py")
    except KeyboardInterrupt:
        print("\n\n已中斷示範")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
