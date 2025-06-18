from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
import fugashi

app = FastAPI()

class AnalyzeRequest(BaseModel):
    app_name: str
    app_id: str  # Google Play のパッケージ名（例：com.example.app）

@app.post("/analyze")
def analyze_api(req: AnalyzeRequest):
    # 口コミ取得（上位100件）
    result, _ = reviews(
        req.app_id,
        lang='ja',  # 日本語
        country='jp',
        sort=Sort.NEWEST,
        count=100
    )

    # MeCab（fugashi）で形態素解析
    tagger = fugashi.Tagger()
    word_scores = {}

    # 仮のポジネガ辞書（実際はもっと充実させられる）
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
        words = [word.surface for word in tagger(text)]
        for w in words:
            if w in polarity_dict:
                score = polarity_dict[w]
                if w not in word_scores:
                    word_scores[w] = 0
                word_scores[w] += score

    # スコアで分類
    pos_keywords = [w for w, s in word_scores.items() if s > 0]
    neg_keywords = [w for w, s in word_scores.items() if s < 0]

    response = {
        "app_name": req.app_name,
        "positive_keywords": pos_keywords,
        "negative_keywords": neg_keywords
    }

    return response
