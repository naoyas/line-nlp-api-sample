from fastapi import FastAPI
from pydantic import BaseModel
from google_play_scraper import Sort, reviews
from janome.tokenizer import Tokenizer
from collections import Counter
import json

app = FastAPI()

# 辞書ファイルロード
with open("polarity_dict.json", encoding='utf-8') as f:
    polarity_dict = json.load(f)

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
    all_tokens = []

    for r in result:
        text = r['content']
        tokens = tokenizer.tokenize(text, wakati=True)
        all_tokens.extend(tokens)

        for w in tokens:
            if w in polarity_dict:
                score = polarity_dict[w]
                if w not in word_scores:
                    word_scores[w] = 0
                word_scores[w] += score

    # 出現頻度ランキング
    word_counter = Counter(all_tokens)
    top_keywords = word_counter.most_common(10)

    pos_keywords = [w for w, s in word_scores.items() if s > 0]
    neg_keywords = [w for w, s in word_scores.items() if s < 0]

    response = {
        "app_name": req.app_name,
        "top_keywords": top_keywords,
        "positive_keywords": pos_keywords,
        "negative_keywords": neg_keywords
    }

    return response
