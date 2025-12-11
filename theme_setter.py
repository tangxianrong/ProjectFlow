#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主題設定 Agent (Theme Setter Agent)

此程式允許教師透過互動式對話來訂定專案主題，並自動修改 projectflow_agent 的四個 agent prompts，
使其能夠引導學生在特定的專案主題下完成學習。

使用方式：
    python theme_setter.py

功能：
1. 接收教師輸入的課程資訊和專案要求
2. 使用 LLM 生成適合的主題設定
3. 修改四個 agent 的 prompts（Summary, Score, Decision, Response）
4. 儲存主題設定到 YAML 檔案
"""

from dotenv import load_dotenv
import os
import re
import yaml
from langchain_openai import ChatOpenAI
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, AIMessage
import logging

# 設定 logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment config
load_dotenv("./.env")

# Set Azure OpenAI API (支援地端部署的 OpenAI 模型)
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

# LLM will be initialized when needed
llm = None

def get_llm():
    """延遲初始化 LLM"""
    global llm
    if llm is None:
        if azure_endpoint and azure_api_key:
            endpoint = azure_endpoint
            if not endpoint.endswith("/v1"):
                endpoint = endpoint.rstrip("/") + "/v1"
            
            llm = ChatOpenAI(
                model=deployment_name,
                base_url=endpoint,
                api_key=azure_api_key,
                temperature=0.7,
                timeout=60,
                max_retries=2
            )
        else:
            llm = ChatVertexAI(model_name="gemini-2.5-flash", temperature=0.7)
    return llm

# 主題設定 Agent 的 Prompt
THEME_SETTER_PROMPT = """
你是一個專業的教學主題設計助理，負責協助教師為 Project-Based Learning (PBL) 課程訂定明確的專案主題。

教師會告訴你：
1. 這個 projectflow_agent 是為哪一門課程設計的
2. 希望學生進行什麼樣的專題

你的任務是根據教師的描述，生成一個完整的主題設定，包含：

1. **課程名稱**：課程的正式名稱
2. **課程描述**：課程的簡短描述（1-2句話）
3. **專案主題**：學生應該探索的專案主題
4. **專案目標**：學生完成專案後應達成的學習目標（3-5個要點）
5. **專案範圍**：專案的範圍限制和具體要求
6. **建議的探索方向**：給學生的探索方向建議（3-5個方向）
7. **評估重點**：評估學生專案的重點項目（3-5個項目）
8. **SDGs 連結**：與此專案相關的聯合國永續發展目標（SDGs）

請以 YAML 格式回傳結果，格式如下：

```yaml
course_name: "課程名稱"
course_description: "課程描述"
project_theme: "專案主題"
project_goals:
  - "目標1"
  - "目標2"
  - "目標3"
project_scope: "專案範圍說明"
exploration_directions:
  - "方向1"
  - "方向2"
  - "方向3"
evaluation_points:
  - "評估重點1"
  - "評估重點2"
  - "評估重點3"
related_sdgs:
  - "SDG X: 目標名稱"
  - "SDG Y: 目標名稱"
```

教師的輸入：
{teacher_input}

請生成主題設定（只需要回傳 YAML，不需要其他說明文字）：
"""

# 修改 Prompt 的模板
PROMPT_MODIFICATION_TEMPLATE = """
你是一個專業的教學內容調整助理，負責根據特定的課程主題修改 AI agent 的系統提示詞。

當前的課程主題設定：
{theme_config}

原始的 Agent Prompt：
{original_prompt}

請根據課程主題設定，修改這個 agent 的 prompt，使其能夠：
1. 引導學生在指定的專案主題範圍內進行探索
2. 評估學生是否符合課程的專案目標
3. 提供與課程主題相關的引導和建議
4. 確保學生的專案符合課程要求的範圍

修改原則：
- 保持原有 prompt 的結構和格式
- 在適當的地方加入課程主題相關的說明
- 將原本關於 SDGs 的通用引導，調整為符合特定專案主題的引導
- 保留所有原有的功能和限制條件
- 使用繁體中文

請回傳修改後的完整 prompt（不需要其他說明）：
"""


def collect_teacher_input():
    """收集教師輸入的課程和專案資訊"""
    print("\n" + "="*60)
    print("歡迎使用 ProjectFlow Agent 主題設定工具")
    print("="*60 + "\n")
    
    print("請回答以下問題，以設定專案主題：\n")
    
    # 收集課程名稱
    course_name = input("1. 這個 projectflow_agent 是為哪一門課程設計的？\n   課程名稱：").strip()
    
    # 收集專案主題
    project_theme = input("\n2. 希望學生進行什麼樣的專題？\n   專案主題：").strip()
    
    # 收集其他詳細資訊
    print("\n3. 請提供更多細節（可選，直接按 Enter 跳過）：")
    specific_requirements = input("   - 有什麼特定的要求或限制嗎？\n     ").strip()
    learning_objectives = input("   - 希望學生達成什麼學習目標？\n     ").strip()
    sdg_focus = input("   - 希望連結到哪些 SDGs 目標？（如果有的話）\n     ").strip()
    
    # 組合教師輸入
    teacher_input = f"""
課程名稱：{course_name}
專案主題：{project_theme}
"""
    
    if specific_requirements:
        teacher_input += f"特定要求：{specific_requirements}\n"
    if learning_objectives:
        teacher_input += f"學習目標：{learning_objectives}\n"
    if sdg_focus:
        teacher_input += f"SDGs 連結：{sdg_focus}\n"
    
    return teacher_input, course_name, project_theme


def generate_theme_config(teacher_input):
    """使用 LLM 生成主題設定"""
    logger.info("正在生成主題設定...")
    
    prompt = THEME_SETTER_PROMPT.format(teacher_input=teacher_input)
    response = get_llm().invoke([HumanMessage(content=prompt)])
    
    # 解析 YAML
    yaml_content = response.content
    
    # 移除可能的 markdown 標記
    if "```yaml" in yaml_content:
        yaml_content = yaml_content.split("```yaml")[1].split("```")[0].strip()
    elif "```" in yaml_content:
        yaml_content = yaml_content.split("```")[1].split("```")[0].strip()
    
    try:
        theme_config = yaml.safe_load(yaml_content)
        return theme_config
    except yaml.YAMLError as e:
        logger.error(f"無法解析 YAML: {e}")
        logger.info(f"原始回應：{yaml_content}")
        return None


def modify_agent_prompt(agent_name, original_prompt, theme_config):
    """使用 LLM 修改特定 agent 的 prompt"""
    logger.info(f"正在修改 {agent_name} 的 prompt...")
    
    # 將主題設定轉為易讀的格式
    theme_str = yaml.dump(theme_config, allow_unicode=True, sort_keys=False)
    
    prompt = PROMPT_MODIFICATION_TEMPLATE.format(
        theme_config=theme_str,
        original_prompt=original_prompt
    )
    
    response = get_llm().invoke([HumanMessage(content=prompt)])
    return response.content.strip()


def save_theme_config(theme_config, filename="prompts/theme_config.yaml"):
    """儲存主題設定到檔案"""
    # 確保目錄存在
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(theme_config, f, allow_unicode=True, sort_keys=False)
    logger.info(f"主題設定已儲存到 {filename}")


def backup_original_prompts():
    """備份原始的 prompts"""
    backup_file = "prompts/__init__.py.backup"
    original_file = "prompts/__init__.py"
    
    if not os.path.exists(backup_file):
        with open(original_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"原始 prompts 已備份到 {backup_file}")
    else:
        logger.info(f"備份檔案已存在：{backup_file}")


def replace_prompt_in_content(content, prompt_name, new_prompt):
    """
    替換內容中的特定 prompt
    
    使用更安全的替換邏輯，避免匹配到 prompt 內容中的三引號
    """
    start_marker = f'{prompt_name} = """'
    
    # 找到開始位置
    start_idx = content.find(start_marker)
    if start_idx == -1:
        logger.warning(f"找不到 {prompt_name}，跳過替換")
        return content
    
    # 從開始位置之後找結束的三引號
    # 為了避免匹配到內容中的三引號，我們尋找獨立一行的三引號
    search_start = start_idx + len(start_marker)
    
    # 使用正則表達式找到下一個獨立的三引號（前面可能有空白）
    end_pattern = r'\n"""'
    match = re.search(end_pattern, content[search_start:])
    
    if not match:
        logger.warning(f"找不到 {prompt_name} 的結束標記，跳過替換")
        return content
    
    end_idx = search_start + match.start() + 1  # +1 包含換行符
    
    # 替換內容
    new_content = (
        content[:start_idx + len(start_marker)] + 
        "\n" + new_prompt + "\n" + 
        content[end_idx:]
    )
    
    return new_content


def update_prompts_file(modified_prompts):
    """更新 prompts/__init__.py 檔案"""
    # 讀取原始檔案
    with open("prompts/__init__.py", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替換各個 prompt
    for prompt_name, new_prompt in modified_prompts.items():
        content = replace_prompt_in_content(content, prompt_name, new_prompt)
    
    # 寫回檔案
    with open("prompts/__init__.py", 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info("Prompts 檔案已更新")


def main():
    """主程式流程"""
    try:
        # 1. 收集教師輸入
        teacher_input, course_name, project_theme = collect_teacher_input()
        
        # 2. 生成主題設定
        print("\n正在分析您的需求並生成主題設定...")
        theme_config = generate_theme_config(teacher_input)
        
        if not theme_config:
            print("❌ 無法生成主題設定，請重試。")
            return
        
        # 3. 顯示生成的主題設定
        print("\n" + "="*60)
        print("生成的主題設定：")
        print("="*60)
        print(yaml.dump(theme_config, allow_unicode=True, sort_keys=False))
        
        # 4. 確認是否繼續
        confirm = input("\n是否要使用此主題設定更新 agent prompts？(y/n): ").strip().lower()
        
        if confirm != 'y':
            print("操作已取消。")
            return
        
        # 5. 備份原始 prompts
        backup_original_prompts()
        
        # 6. 儲存主題設定
        save_theme_config(theme_config)
        
        # 7. 讀取原始 prompts
        import prompts
        original_prompts = {
            "SUMMARY_AGENT_PROMPT": prompts.SUMMARY_AGENT_PROMPT,
            "SCORE_AGENT_PROMPT": prompts.SCORE_AGENT_PROMPT,
            "DECISION_AGENT_PROMPT": prompts.DECISION_AGENT_PROMPT,
            "RESPONSE_AGENT_PROMPT": prompts.RESPONSE_AGENT_PROMPT,
        }
        
        # 8. 修改各個 agent 的 prompts
        print("\n正在修改 agent prompts...")
        modified_prompts = {}
        
        for agent_name, original_prompt in original_prompts.items():
            modified_prompt = modify_agent_prompt(
                agent_name, 
                original_prompt, 
                theme_config
            )
            modified_prompts[agent_name] = modified_prompt
            print(f"✓ {agent_name} 已修改")
        
        # 9. 更新 prompts 檔案
        update_prompts_file(modified_prompts)
        
        # 10. 完成
        print("\n" + "="*60)
        print("✅ 主題設定完成！")
        print("="*60)
        print(f"\n課程名稱：{theme_config.get('course_name', course_name)}")
        print(f"專案主題：{theme_config.get('project_theme', project_theme)}")
        print(f"\n主題設定已儲存到：prompts/theme_config.yaml")
        print(f"原始 prompts 備份：prompts/__init__.py.backup")
        print(f"\n您現在可以啟動 projectflow_agent，它會根據新的主題引導學生。")
        
    except KeyboardInterrupt:
        print("\n\n操作已取消。")
    except Exception as e:
        logger.error(f"發生錯誤：{e}", exc_info=True)
        print(f"\n❌ 發生錯誤：{e}")


if __name__ == "__main__":
    main()
