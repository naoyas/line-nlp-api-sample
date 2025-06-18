from fastapi import FastAPI, Request
from google_play_scraper import reviews, Sort
from janome.tokenizer import Tokenizer
from collections import Counter
import pandas as pd
import re

app = FastAPI()

# --- 辞書読み込み（1回だけ最初に読む）
df = pd.read_csv("pn.csv.m3.120408.trim", sep="\t", names=["term","sentiment","cat"], encoding="utf-8")
df = df[df['sentiment'].isin(['p','n'])]
polarity_dict = {row.term: (1 if row.sentiment=='p' else -1) for _,row in df.iterrows()}

# --- ストップワード
stopwords = set([
    "。", "、", "！", "？", "の", "に", "を", "が", "て", "は", "も", "で", "た", "し", "です", "ます", 
    "する", "ある", "いる", "そして", "それ", "この", "あの", "その", "など", "こと", "もの", 
    "よう", "ため", "ね", "よ", "から", "まで", "けど", "でも", "と", "な", "だ", "ー", "1", "2", "3", 
    "4", "5", "6", "7", "8", "9", "0", "•", "▪", "…", "・", "アプリ", "メルカリ"
])

@app.post("/")
async def analyze_api(request: Request):
    data = await request.json()
    app_id = data.get("app_id", "")
    app_name = data.get("app_name", "")

    # --- 口コミ取得
    result, _ = reviews(app_id, lang='ja', country='jp', sort=Sort.NEWEST, count=100)

    # --- 形態素解析
    tokenizer = Tokenizer()
    target_pos = ["名詞", "形容詞"]

    all_tokens = []
    polarity_counts = {}

    for r in result:
        for token in tokenizer.tokenize(r['content']):
            base = token.base_form
            pos = token.part_of_speech.split(',')[0]
            if pos in target_pos and base not in stopwords and not re.fullmatch(r'\d+|[^\wぁ-んァ-ン一-龥]', base):
                all_tokens.append(base)
                if base in polarity_dict:
                    polarity_counts[base] = polarity_counts.get(base,0) + 1

    # --- ランキング
    top5 = Counter(all_tokens).most_common(5)
    pos3 = sorted([(w,c) for w,c in polarity_counts.items() if polarity_dict[w]>0], key=lambda x: x[1], reverse=True)[:3]
    neg3 = sorted([(w,c) for w,c in polarity_counts.items() if polarity_dict[w]<0], key=lambda x: x[1], reverse=True)[:3]

    # --- ChatGPT用 TOP20
    top20 = Counter(all_tokens).most_common(20)
    top20_text = "\n".join([f"{i+1}. {word} ({count}回)" for i, (word, count) in enumerate(top20)])

    # --- レスポンス
    return {
        "app_name": app_name,
        "top5_keywords": [f"{w}({c}回)" for w,c in top5],
        "positive_keywords": [f"{w}({c}回)" for w,c in pos3],
        "negative_keywords": [f"{w}({c}回)" for w,c in neg3],
        "chatgpt_input": f"【口コミ単語出現ランキング TOP20】\n{top20_text}"
    }
