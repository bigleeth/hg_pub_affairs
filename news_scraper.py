# news_scraper.py

import os
import urllib.request
import pandas as pd
import json
import re
from datetime import datetime, timedelta
import subprocess

# === Naver OpenAPI credentials ===
client_id = "pfLKc2NgWoanoRnRDBgx"
client_secret = "efT6rgzJRG"

# === Keywords to search ===
keywords = [
    "국정기획위원회", "이재명", "국회", "기재위", "임이자",
    "기재부", "금융위", "수출입은행", "산업은행", "기업은행", "무역보험공사", "ODA", "EDCF"
]

# === Time range: from 18:00 yesterday to now ===
now = datetime.now()
start_time = (now - timedelta(days=1)).replace(hour=18, minute=0, second=0, microsecond=0)

# === Function to clean HTML tags ===
def clean_html(text):
    return re.sub(re.compile('<.*?>'), '', text)

# === Create empty DataFrame ===
news_df = pd.DataFrame(columns=["Keyword", "Title", "Original Link", "Link", "Description", "Publication Date"])

# === Scrape Naver News API for each keyword ===
for keyword in keywords:
    query = urllib.parse.quote(keyword)
    display = 50
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

                if pub_datetime.replace(tzinfo=None) >= start_time:
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
file_path = os.path.join(output_dir, f"{today_str}_pub_affair_articles.csv")

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
