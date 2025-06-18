from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AnalyzeRequest(BaseModel):
    app_name: str

@app.post("/analyze")
def analyze_api(req: AnalyzeRequest):
    # 仮のNLP分析結果をここで返す
    keywords_positive = ["使いやすい", "便利", "かわいい"]
    keywords_negative = ["バグ", "遅い", "強制終了"]

    result = {
        "app_name": req.app_name,
        "positive_keywords": keywords_positive,
        "negative_keywords": keywords_negative
    }

    return result
