"""
測試地端部署 OpenAI 模型的簡單程式
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

def test_local_openai():
    """
    測試地端部署的 OpenAI 模型連線與基本對話功能
    """
    # 載入環境變數
    load_dotenv()
    
    # 從環境變數讀取地端模型設定
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "not-needed")
    model_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    
    # 確保 endpoint 有 /v1 路徑
    if not endpoint.endswith("/v1"):
        endpoint = endpoint.rstrip("/") + "/v1"
    
    print("=" * 50)
    print("🔍 地端 OpenAI 模型連線測試")
    print("=" * 50)
    print(f"Endpoint: {endpoint}")
    print(f"Model: {model_name}")
    print("=" * 50)
    
    try:
        # 建立地端 OpenAI 客戶端（使用 ChatOpenAI 而非 AzureChatOpenAI）
        llm = ChatOpenAI(
            model=model_name,
            base_url=endpoint,
            api_key=api_key,
            temperature=0.7,
            timeout=60,  # 增加超時時間
            max_retries=2
        )
        
        print("\n✅ 成功建立地端 OpenAI 客戶端\n")
        
        # 測試 1: 簡單問答
        print("📝 測試 1: 簡單問答")
        print("-" * 50)
        messages = [
            SystemMessage(content="你是一個友善的AI助手。"),
            HumanMessage(content="請用一句話介紹你自己。")
        ]
        
        response = llm.invoke(messages)
        print(f"問題: 請用一句話介紹你自己。")
        print(f"回答: {response.content}")
        print("-" * 50)
        
        # 測試 2: 數學問題
        print("\n📝 測試 2: 數學問題")
        print("-" * 50)
        messages = [
            HumanMessage(content="123 + 456 等於多少？請直接回答數字。")
        ]
        
        response = llm.invoke(messages)
        print(f"問題: 123 + 456 等於多少？")
        print(f"回答: {response.content}")
        print("-" * 50)
        
        # 測試 3: 串流回應
        print("\n📝 測試 3: 串流回應")
        print("-" * 50)
        messages = [
            HumanMessage(content="請說一個笑話。")
        ]
        
        print(f"問題: 請說一個笑話。")
        print(f"回答: ", end="")
        for chunk in llm.stream(messages):
            print(chunk.content, end="", flush=True)
        print("\n" + "-" * 50)
        
        print("\n✅ 所有測試完成！\n")
        
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_local_openai()