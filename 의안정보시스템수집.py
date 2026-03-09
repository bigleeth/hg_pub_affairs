import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

URL = "https://likms.assembly.go.kr/bill/bi/bill/sch/detailedSchPage.do"

def collect_bill_info(keyword: str):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": URL,
    })

    # 🔹 검색어를 쿼리로 전달 (실제 서버 동작 방식)
    params = {
        "billName": keyword
    }

    r = session.get(URL, params=params, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("tr.mono")
    results = []

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 4:
            continue

        # 의안번호
        bill_no = tds[0].get("title", "").strip()

        # 의안명 + billId
        title_td = tds[1]
        bill_name = title_td.get_text(strip=True)

        bill_id = ""
        a = title_td.find("a")
        if a and "onclick" in a.attrs:
            m = re.search(r"fGoDetail\('(\d+)'", a["onclick"])
            if m:
                bill_id = m.group(1)

        # 제안자 / 날짜 / 상태
        proposer = tds[2].get_text(strip=True)
        propose_date = tds[3].get_text(strip=True)
        status = tds[4].get_text(strip=True) if len(tds) > 4 else ""

        results.append({
            "의안번호": bill_no,
            "의안ID": bill_id,
            "의안명": bill_name,
            "제안자": proposer,
            "제안일자": propose_date,
            "심사진행상태": status,
            "상세URL": f"https://likms.assembly.go.kr/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else "",
            "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

    return results


# ✅ 사용 예시
bill_names = [
    "한국수출입은행법 일부개정법률안",
    "경제안보를 위한 공급망 안정화 지원 기본법 일부개정법률안",
    "첨단조선업의 경쟁력 강화 및 지원에 관한 특별법안",
    "공공기관의 운영에 관한 법률 일부개정법률안",
    "한국산업은행법 일부개정법률안",
    "2025년도에 발행하는 첨단전략산업기금채권에 대한 국가보증동의안",
    "중소기업은행법 일부개정법률안",
    "정부조직법 일부개정법률안",
    "전략수출금융지원에 관한 법률안",
    "한미 조선산업 협력 및 지원 특별법안",
    "한미 전략적 투자 관리를 위한 특별법안"
]

all_data = []
for name in bill_names:
    all_data.extend(collect_bill_info(name))

df = pd.DataFrame(all_data)
print(df)
df.to_json("의안정보검색결과.json", orient="records", force_ascii=False, indent=2)


