# news_scraper.py

import os
import urllib.request
import pandas as pd
import json
import re
from datetime import datetime, timedelta
import subprocess
import pytz

# === Naver OpenAPI credentials ===
client_id = "pfLKc2NgWoanoRnRDBgx"
client_secret = "efT6rgzJRG"

# === Keywords to search ===
keywords = [
    "이재명", "정상순방", "국회", "본회의", "재경위", "재정경제기획위원회", "정무위", 
    "정태호", "김영진 의원", "김영환", "김태년", "박홍근", "박민규", "안규백", "안도걸", "오기형", "이소영 의원", "정성호", "정일영", "조승래", "진성준", "최기상",
    "송언석", "박수영", "박대출", "박성훈", "유상범", "윤영석", "이인선", "임이자", "최은석", "권영세", "차규근", "천하람",
    "오늘의 주요일정", "오늘의 국회일정", "세종풍향계", "세종25시", "관가는 지금", "관가", "관료", "관가뒷담", "관가 인사이드",
    "재경부", "기획처", "금융위", "수출입은행", "산업은행", "기업은행", "무역보험공사",
    "ODA", "EDCF", "공급망", "대미투자", "전략수출금융기금", "동남권투자공사", "지방이전", "총액인건비", "남북협력기금"
]

# === Time range: from 18:00 yesterday to now ===
now = datetime.now(pytz.timezone('Asia/Seoul'))  # 서울 타임존으로 현재 시간을 가져옵니다.
start_time = (now - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)

# === Function to clean HTML tags ===
def clean_html(text):
    return re.sub(re.compile('<.*?>'), '', text)

# === Create empty DataFrame ===
news_df = pd.DataFrame(columns=["Keyword", "Title", "Original Link", "Link", "Description", "Publication Date"])

# === Scrape Naver News API for each keyword ===
for keyword in keywords:
    query = urllib.parse.quote(keyword)
    display = 30
    start = 1
    sort = "date"

    url = f"https://openapi.naver.com/v1/search/news?query={query}&display={display}&start={start}&sort={sort}"

    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    try:
        response = urllib.request.urlopen(request)
        if response.getcode() == 200:
            data = json.loads(response.read().decode('utf-8'))
            for item in data['items']:
                pub_date_str = item['pubDate']
                pub_datetime = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %z")

                # 시간대가 있는 pub_datetime와 비교
                if pub_datetime >= start_time:
                    news_df.loc[len(news_df)] = [
                        keyword,
                        clean_html(item['title']),
                        item['originallink'],
                        item['link'],
                        clean_html(item['description']),
                        pub_date_str
                    ]
    except Exception as e:
        print(f"❌ Error with keyword '{keyword}':", e)

# === Reorder columns ===
news_df = news_df[["Keyword", "Title", "Description", "Original Link", "Link", "Publication Date"]]

# === Save to local CSV file ===
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
today_str = now.strftime("%Y%m%d")
file_path = os.path.join(output_dir, f"pub_affair_articles.csv")

news_df.to_csv(file_path, index=False, encoding="utf-8-sig")
print(f"\n✅ {len(news_df)} articles saved to: {file_path}")

# === Optional: Git auto-commit & push ===
auto_commit = True  # Set to False if you don't want git push

if auto_commit:
    try:
        subprocess.run(["git", "add", file_path], check=True)
        subprocess.run(["git", "commit", "-m", f"📄 Auto-update articles on {today_str}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("📤 Changes pushed to GitHub.")
    except Exception as e:
        print("❌ Git push failed:", e)
ㅍㅍ
