#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試主題設定工具的基本功能
"""

import os
import sys
import yaml
import tempfile

# 測試 1: 匯入模組
print("測試 1: 匯入 theme_setter 模組...")
try:
    import theme_setter
    print("✓ 模組匯入成功")
except Exception as e:
    print(f"✗ 模組匯入失敗: {e}")
    sys.exit(1)

# 測試 2: 檢查主要函數是否存在
print("\n測試 2: 檢查主要函數...")
required_functions = [
    'collect_teacher_input',
    'generate_theme_config',
    'modify_agent_prompt',
    'save_theme_config',
    'backup_original_prompts',
    'update_prompts_file',
    'get_llm',
]

for func_name in required_functions:
    if hasattr(theme_setter, func_name):
        print(f"✓ 函數 {func_name} 存在")
    else:
        print(f"✗ 函數 {func_name} 不存在")
        sys.exit(1)

# 測試 3: 測試 save_theme_config 函數
print("\n測試 3: 測試主題設定儲存功能...")
test_config = {
    'course_name': '測試課程',
    'course_description': '這是一個測試課程',
    'project_theme': '測試專案主題',
    'project_goals': ['目標1', '目標2', '目標3'],
    'project_scope': '測試範圍',
    'exploration_directions': ['方向1', '方向2'],
    'evaluation_points': ['評估1', '評估2'],
    'related_sdgs': ['SDG 1', 'SDG 2'],
}

# 使用 mkstemp 獲得臨時檔案
import tempfile as tmp
test_fd, test_file = tmp.mkstemp(suffix='.yaml', text=True)
try:
    # 先關閉檔案描述符
    os.close(test_fd)
    
    theme_setter.save_theme_config(test_config, test_file)
    
    # 驗證檔案是否存在
    if os.path.exists(test_file):
        print(f"✓ 主題設定檔案已建立: {test_file}")
        
        # 驗證內容
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_config = yaml.safe_load(f)
        
        if loaded_config == test_config:
            print("✓ 主題設定內容正確")
        else:
            print("✗ 主題設定內容不符")
            os.unlink(test_file)
            sys.exit(1)
    else:
        print(f"✗ 主題設定檔案未建立")
        sys.exit(1)
except Exception as e:
    print(f"✗ 儲存主題設定失敗: {e}")
    sys.exit(1)
finally:
    # 清理測試檔案
    if os.path.exists(test_file):
        os.unlink(test_file)

# 測試 4: 測試 backup_original_prompts 函數
print("\n測試 4: 測試備份功能...")
try:
    # 確保備份檔案不存在
    backup_file = "prompts/__init__.py.backup"
    if os.path.exists(backup_file):
        os.remove(backup_file)
        print(f"  移除現有備份檔案: {backup_file}")
    
    theme_setter.backup_original_prompts()
    
    if os.path.exists(backup_file):
        print(f"✓ 備份檔案已建立: {backup_file}")
    else:
        print("✗ 備份檔案未建立")
        sys.exit(1)
except Exception as e:
    print(f"✗ 備份功能失敗: {e}")
    sys.exit(1)

# 測試 5: 檢查 Prompt 模板
print("\n測試 5: 檢查 Prompt 模板...")
if hasattr(theme_setter, 'THEME_SETTER_PROMPT'):
    prompt = theme_setter.THEME_SETTER_PROMPT
    required_fields = ['{teacher_input}']
    
    all_found = True
    for field in required_fields:
        if field in prompt:
            print(f"✓ THEME_SETTER_PROMPT 包含 {field}")
        else:
            print(f"✗ THEME_SETTER_PROMPT 缺少 {field}")
            all_found = False
    
    if not all_found:
        sys.exit(1)
else:
    print("✗ THEME_SETTER_PROMPT 不存在")
    sys.exit(1)

if hasattr(theme_setter, 'PROMPT_MODIFICATION_TEMPLATE'):
    prompt = theme_setter.PROMPT_MODIFICATION_TEMPLATE
    required_fields = ['{theme_config}', '{original_prompt}']
    
    all_found = True
    for field in required_fields:
        if field in prompt:
            print(f"✓ PROMPT_MODIFICATION_TEMPLATE 包含 {field}")
        else:
            print(f"✗ PROMPT_MODIFICATION_TEMPLATE 缺少 {field}")
            all_found = False
    
    if not all_found:
        sys.exit(1)
else:
    print("✗ PROMPT_MODIFICATION_TEMPLATE 不存在")
    sys.exit(1)

# 測試 6: 驗證文件是否存在
print("\n測試 6: 檢查文件...")
doc_files = ['THEME_SETTER_GUIDE.md', 'README.md']
for doc_file in doc_files:
    if os.path.exists(doc_file):
        print(f"✓ 文件存在: {doc_file}")
    else:
        print(f"✗ 文件不存在: {doc_file}")
        sys.exit(1)

# 所有測試通過
print("\n" + "="*60)
print("✅ 所有測試通過！")
print("="*60)
print("\n主題設定工具已準備就緒。")
print("執行 'python theme_setter.py' 開始使用。")
