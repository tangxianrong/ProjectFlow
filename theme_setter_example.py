#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主題設定工具範例與測試

此腳本展示如何使用主題設定工具，並提供一個模擬的執行流程（不需要實際的 LLM API）
"""

import yaml
import os

# 範例主題設定
example_theme_config = {
    'course_name': '永續發展專題',
    'course_description': '引導學生探究社區環境議題，並設計可行的解決方案',
    'project_theme': '社區環境議題探究與解決方案設計',
    'project_goals': [
        '能夠發現並定義學校周邊的真實環境問題',
        '學會蒐集與分析環境相關資料',
        '設計符合永續發展理念的解決方案',
        '培養社區參與和公民意識',
    ],
    'project_scope': '專案必須聚焦在學校周邊可觀察的環境議題，如空氣品質、廢棄物、水資源等',
    'exploration_directions': [
        '觀察記錄社區環境現況',
        '訪談社區居民了解環境問題',
        '蒐集環境監測數據',
        '研究類似案例的解決方案',
    ],
    'evaluation_points': [
        '問題定義的明確性和重要性',
        '資料蒐集的完整性和可信度',
        '解決方案的可行性和創新性',
        '與 SDGs 目標的連結程度',
    ],
    'related_sdgs': [
        'SDG 11: 永續城市與社區',
        'SDG 13: 氣候行動',
    ],
}

def display_theme_config(config):
    """顯示主題設定"""
    print("\n" + "="*60)
    print("範例主題設定")
    print("="*60)
    print(yaml.dump(config, allow_unicode=True, sort_keys=False))
    print("="*60)

def save_example_config():
    """儲存範例主題設定"""
    output_file = 'prompts/theme_config_example.yaml'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(example_theme_config, f, allow_unicode=True, sort_keys=False)
    
    print(f"\n✓ 範例主題設定已儲存到: {output_file}")
    return output_file

def show_workflow():
    """展示主題設定工具的工作流程"""
    print("\n" + "="*60)
    print("主題設定工具工作流程")
    print("="*60)
    
    steps = [
        "1. 收集教師輸入",
        "   - 課程名稱",
        "   - 專案主題",
        "   - 特定要求（可選）",
        "   - 學習目標（可選）",
        "   - SDGs 連結（可選）",
        "",
        "2. 生成主題設定",
        "   - 使用 LLM 根據教師輸入生成完整的主題設定",
        "   - 包含課程描述、專案目標、評估重點等",
        "",
        "3. 確認主題設定",
        "   - 顯示生成的主題設定供教師確認",
        "   - 教師可以選擇接受或重新生成",
        "",
        "4. 備份原始 Prompts",
        "   - 自動備份 prompts/__init__.py",
        "   - 備份檔案: prompts/__init__.py.backup",
        "",
        "5. 儲存主題設定",
        "   - 將主題設定儲存為 YAML 檔案",
        "   - 儲存位置: prompts/theme_config.yaml",
        "",
        "6. 修改 Agent Prompts",
        "   - 使用 LLM 修改四個 agent 的 prompts",
        "   - Summary Agent: 加入課程主題和專案範圍",
        "   - Score Agent: 調整評分標準",
        "   - Decision Agent: 加入專案目標和探索方向",
        "   - Response Agent: 調整回應語氣和引導方式",
        "",
        "7. 更新 Prompts 檔案",
        "   - 將修改後的 prompts 寫入 prompts/__init__.py",
        "",
        "8. 完成",
        "   - 顯示完成訊息和輸出檔案位置",
    ]
    
    for step in steps:
        print(step)
    
    print("="*60)

def show_modified_prompt_example():
    """展示 Prompt 修改的範例"""
    print("\n" + "="*60)
    print("Prompt 修改範例")
    print("="*60)
    
    print("\n原始 Summary Agent Prompt (部分):")
    print("-" * 60)
    print("""
你是摘要小助手 SummaryG，負責協助用戶記錄、彙整與更新整體專案資料。
主要帶領用戶完成的專案的進程是：
階段1：階段一 PBL 問題探索，主要議題：用戶是否能有脈絡的知道要解決與SDGs有關的某項特定問題
    """.strip())
    
    print("\n\n修改後 Summary Agent Prompt (部分) - 針對「社區環境議題探究」主題:")
    print("-" * 60)
    print("""
你是摘要小助手 SummaryG，負責協助用戶記錄、彙整與更新整體專案資料。
本課程為「永續發展專題」，專案主題為「社區環境議題探究與解決方案設計」。

專案範圍：專案必須聚焦在學校周邊可觀察的環境議題，如空氣品質、廢棄物、水資源等

主要帶領用戶完成的專案的進程是：
階段1：階段一 PBL 問題探索，主要議題：用戶是否能發現並定義學校周邊的真實環境問題
    """.strip())
    
    print("\n\n✓ 可以看到 Prompt 已經針對課程主題進行了客製化調整")
    print("="*60)

def main():
    """主程式"""
    print("\n" + "="*70)
    print(" "*15 + "主題設定工具 - 範例與說明")
    print("="*70)
    
    # 1. 展示範例主題設定
    display_theme_config(example_theme_config)
    
    # 2. 儲存範例設定
    save_example_config()
    
    # 3. 展示工作流程
    show_workflow()
    
    # 4. 展示 Prompt 修改範例
    show_modified_prompt_example()
    
    # 5. 使用說明
    print("\n" + "="*60)
    print("如何使用主題設定工具")
    print("="*60)
    print("""
1. 確保已設定 .env 檔案中的 LLM API 金鑰

2. 執行主題設定工具：
   python theme_setter.py

3. 按照提示輸入課程資訊：
   - 課程名稱
   - 專案主題
   - 其他可選資訊

4. 確認生成的主題設定

5. 工具會自動：
   - 備份原始 prompts
   - 儲存主題設定
   - 修改四個 agent 的 prompts
   - 更新 prompts 檔案

6. 完成後即可啟動 projectflow_agent，
   agent 會根據新的主題引導學生

詳細說明請參考: THEME_SETTER_GUIDE.md
    """.strip())
    print("="*60)
    
    print("\n✅ 範例與說明展示完成！")

if __name__ == "__main__":
    main()
