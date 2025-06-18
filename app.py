from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    app_name: str

@app.post("/analyze")
def analyze_api(req: AnalyzeRequest):
    result = f"アプリ「{req.app_name}」のネガポジ分析結果です！（仮）"
    return {"result": result}
