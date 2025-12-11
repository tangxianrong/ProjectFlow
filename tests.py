"""
ProjectFlow 測試套件

簡單的測試框架，用於驗證核心功能
"""

import sys
import os
from pathlib import Path

# 將專案根目錄加入路徑
sys.path.insert(0, str(Path(__file__).parent))

import unittest
from unittest.mock import Mock, patch
import json

# 導入要測試的模組
from utils import (
    extract_first_json_list,
    safe_json_parse,
    count_tokens,
    TokenStats,
    validate_state,
    merge_states,
    truncate_text,
    clean_whitespace
)


class TestJSONParsing(unittest.TestCase):
    """測試 JSON 解析功能"""
    
    def test_extract_simple_json_list(self):
        """測試解析簡單的 JSON list"""
        text = '[{"key": "value"}]'
        result = extract_first_json_list(text)
        self.assertEqual(result, [{"key": "value"}])
    
    def test_extract_json_with_text(self):
        """測試從包含文字的內容中提取 JSON"""
        text = '這是一些文字 [{"key": "value"}] 更多文字'
        result = extract_first_json_list(text)
        self.assertEqual(result, [{"key": "value"}])
    
    def test_extract_invalid_json(self):
        """測試處理無效的 JSON"""
        text = '這不是 JSON'
        result = extract_first_json_list(text)
        self.assertEqual(result, [])
    
    def test_safe_json_parse_valid(self):
        """測試安全解析有效的 JSON"""
        text = '{"key": "value"}'
        result = safe_json_parse(text)
        self.assertEqual(result, {"key": "value"})
    
    def test_safe_json_parse_invalid(self):
        """測試安全解析無效的 JSON 返回預設值"""
        text = 'invalid json'
        result = safe_json_parse(text, default={})
        self.assertEqual(result, {})


class TestTokenCounting(unittest.TestCase):
    """測試 Token 計數功能"""
    
    def test_count_tokens_basic(self):
        """測試基本的 token 計數"""
        text = "Hello world"
        result = count_tokens(text)
        self.assertGreater(result, 0)
    
    def test_token_stats_initialization(self):
        """測試 TokenStats 初始化"""
        stats = TokenStats()
        self.assertEqual(stats.get_total(), 0)
    
    def test_token_stats_add_input(self):
        """測試添加輸入 token"""
        stats = TokenStats()
        stats.add_input("summary_agent", 100)
        self.assertEqual(stats.get_total_input(), 100)
    
    def test_token_stats_add_output(self):
        """測試添加輸出 token"""
        stats = TokenStats()
        stats.add_output("score_agent", 50)
        self.assertEqual(stats.get_total_output(), 50)
    
    def test_token_stats_total(self):
        """測試總計 token"""
        stats = TokenStats()
        stats.add_input("summary_agent", 100)
        stats.add_output("score_agent", 50)
        self.assertEqual(stats.get_total(), 150)
    
    def test_token_stats_reset(self):
        """測試重設統計"""
        stats = TokenStats()
        stats.add_input("summary_agent", 100)
        stats.reset()
        self.assertEqual(stats.get_total(), 0)


class TestStateManagement(unittest.TestCase):
    """測試狀態管理功能"""
    
    def test_validate_state_valid(self):
        """測試驗證有效的狀態"""
        state = {
            "messages": [],
            "project_content": "",
            "session_id": "test"
        }
        required = ["messages", "project_content", "session_id"]
        self.assertTrue(validate_state(state, required))
    
    def test_validate_state_invalid(self):
        """測試驗證無效的狀態"""
        state = {
            "messages": []
        }
        required = ["messages", "project_content", "session_id"]
        self.assertFalse(validate_state(state, required))
    
    def test_merge_states(self):
        """測試合併狀態"""
        base = {"a": 1, "b": 2}
        update = {"b": 3, "c": 4}
        result = merge_states(base, update)
        expected = {"a": 1, "b": 3, "c": 4}
        self.assertEqual(result, expected)


class TestTextProcessing(unittest.TestCase):
    """測試文字處理功能"""
    
    def test_truncate_text_short(self):
        """測試截斷短文字（不應截斷）"""
        text = "短文字"
        result = truncate_text(text, max_length=10)
        self.assertEqual(result, "短文字")
    
    def test_truncate_text_long(self):
        """測試截斷長文字"""
        text = "這是一段很長的文字" * 10
        result = truncate_text(text, max_length=20)
        self.assertEqual(len(result), 20)
        self.assertTrue(result.endswith("..."))
    
    def test_clean_whitespace(self):
        """測試清理空白字元"""
        text = """
        第一行  
        
        第二行
        
        第三行  
        """
        result = clean_whitespace(text)
        expected = "第一行\n第二行\n第三行"
        self.assertEqual(result, expected)


class TestConfiguration(unittest.TestCase):
    """測試配置管理"""
    
    def test_import_config(self):
        """測試導入配置模組"""
        try:
            import config
            self.assertTrue(hasattr(config, 'LLMConfig'))
            self.assertTrue(hasattr(config, 'LogConfig'))
            self.assertTrue(hasattr(config, 'APIConfig'))
        except ImportError as e:
            self.fail(f"無法導入 config 模組: {e}")
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'http://test.com',
        'AZURE_OPENAI_API_KEY': 'test-key'
    })
    def test_llm_config_use_openai(self):
        """測試 LLM 配置判斷使用 OpenAI"""
        # 重新導入以讀取新的環境變數
        import importlib
        import config as cfg
        importlib.reload(cfg)
        
        self.assertTrue(cfg.LLMConfig.use_openai())


class TestPrompts(unittest.TestCase):
    """測試 Prompt 模板"""
    
    def test_import_prompts(self):
        """測試導入 prompts 模組"""
        try:
            import prompts
            self.assertTrue(hasattr(prompts, 'SUMMARY_AGENT_PROMPT'))
            self.assertTrue(hasattr(prompts, 'SCORE_AGENT_PROMPT'))
            self.assertTrue(hasattr(prompts, 'DECISION_AGENT_PROMPT'))
            self.assertTrue(hasattr(prompts, 'RESPONSE_AGENT_PROMPT'))
        except ImportError as e:
            self.fail(f"無法導入 prompts 模組: {e}")
    
    def test_prompt_not_empty(self):
        """測試 Prompt 不為空"""
        import prompts
        self.assertGreater(len(prompts.SUMMARY_AGENT_PROMPT), 0)
        self.assertGreater(len(prompts.SCORE_AGENT_PROMPT), 0)
        self.assertGreater(len(prompts.DECISION_AGENT_PROMPT), 0)
        self.assertGreater(len(prompts.RESPONSE_AGENT_PROMPT), 0)


def run_tests(verbosity=2):
    """執行所有測試"""
    # 建立測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有測試
    suite.addTests(loader.loadTestsFromTestCase(TestJSONParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestTokenCounting))
    suite.addTests(loader.loadTestsFromTestCase(TestStateManagement))
    suite.addTests(loader.loadTestsFromTestCase(TestTextProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestPrompts))
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # 返回測試結果
    return result.wasSuccessful()


if __name__ == "__main__":
    # 執行測試並根據結果設定退出碼
    success = run_tests()
    sys.exit(0 if success else 1)
