from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn
from projectflow_graph import background_graph, AIMessage, HumanMessage, logger
import background_tool

# 初始化工具（若未在 import 時 setup）
background_tool.setup(background_graph, AIMessage, HumanMessage, logger=logger)

# API_KEY = "YOUR_INTERNAL_KEY"  # 放環境變數更安全

class BackgroundUpdateRequest(BaseModel):
    session_id: str
    prev_ai_prompt: str
    user_prompt: str

app = FastAPI(title="projectflow Agent Background Tool", version="1.0.0")

@app.post("/background_update")
def background_update(req: BackgroundUpdateRequest):
    # if x_api_key != API_KEY:
    #     raise HTTPException(status_code=401, detail="Unauthorized")
    return background_tool.background_update_tool(
        session_id=req.session_id,
        prev_ai_prompt=req.prev_ai_prompt,
        user_prompt=req.user_prompt
    )

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8000)