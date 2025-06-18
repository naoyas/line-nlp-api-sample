from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
from janome.tokenizer import Tokenizer

app = FastAPI()

class AnalyzeRequest(BaseModel):
    app_name: str
    app_id: str

@app.post("/analyze")
def analyze_api(req: AnalyzeRequest):
    result, _ = reviews(
        req.app_id,
        lang='ja',
        country='jp',
        sort=Sort.NEWEST,
        count=100
    )

    tokenizer = Tokenizer()
    word_scores = {}

    polarity_dict = {
        "便利": 1,
        "使いやすい": 1,
        "最高": 1,
        "簡単": 1,
        "楽しい": 1,
        "おすすめ": 1,
        "バグ": -1,
        "遅い": -1,
        "落ちる": -1,
        "強制終了": -1,
        "最悪": -1
    }

    for r in result:
        text = r['content']
        tokens = tokenizer.tokenize(text, wakati=True)
        for w in tokens:
            if w in polarity_dict:
                score = polarity_dict[w]
                if w not in word_scores:
                    word_scores[w] = 0
                word_scores[w] += score

    pos_keywords = [w for w, s in word_scores.items() if s > 0]
    neg_keywords = [w for w, s in word_scores.items() if s < 0]

    response = {
        "app_name": req.app_name,
        "positive_keywords": pos_keywords,
        "negative_keywords": neg_keywords
    }

    return response
