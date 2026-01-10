import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

### =============== 국회의원 정보 수집 ===============
cookies_members = {
    '_fwb': '224GIbJbv3W2VKbiHHpHIKa.1736910833680',
    '_ga': 'GA1.1.1553764147.1736910835',
    'PCID': '756e904c-0b66-a4a7-6836-589756f10a6e-1736910838628',
    'JSESSIONID': 'your_valid_session',
    'PHAROSVISITOR': '00006eb50196285f2f296cc80ac965a6',
}
headers_members = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive'
}
members = [
    ("김영진", "KIMYOUNGJIN"),
    ("정태호", "JUNGTAEHO"),
    ("김영환", "KIMYOUNGWHAN"),
    ("김태년", "KIMTAENYEON"),
    ("박홍근", "PARKHONGKEUN"),
    ("박민규", "PARKMINKYU"),
    ("안규백", "AHNGYUBACK"),
    ("안도걸", "AHNDOGEOL"),
    ("오기형", "OHGIHYOUNG"),
    ("이소영", "LEESOYOUNG"),
    ("정성호", "JUNGSUNGHO"),
    ("정일영", "CHUNGILYOUNG"),
    ("조승래", "JOSEOUNGLAE"),
    ("진성준", "JINSUNGJOON"),
    ("송언석", "SONGEONSEOG"),
    ("박수영", "PARKSOOYOUNG"),
    ("박대출", "PARKDAECHUL"),
    ("박성훈", "PARKSUNGHOON"),
    ("유상범", "YOOSANGBUM"),
    ("윤영석", "YOONYOUNGSEOK"),
    ("이인선", "LEEINSEON"),
    ("임이자", "LIMLEEJA"),
    ("최은석", "CHOIEUNSEOK"),
    ("차규근", "CHAGYUGEUN"),
    ("천하람", "CHUNHARAM"),
    ("최기상", "CHOIKISANG"),
    ("권영세", "KWONYOUNGSE"),

]

# 정당 정보 매핑
party_mapping = {
    "정태호": "더불어민주당",
    "김영진": "더불어민주당",
    "김영환": "더불어민주당",
    "김태년": "더불어민주당",
    "박홍근": "더불어민주당",
    "박민규": "더불어민주당",
    "안규백": "더불어민주당",
    "안도걸": "더불어민주당",
    "오기형": "더불어민주당",
    "이소영": "더불어민주당",
    "정성호": "더불어민주당",
    "정일영": "더불어민주당",
    "조승래": "더불어민주당",
    "진성준": "더불어민주당",
    "최기상": "더불어민주당",
    "송언석": "국민의힘",
    "박수영": "국민의힘",
    "박대출": "국민의힘",
    "박성훈": "국민의힘",
    "유상범": "국민의힘",
    "윤영석": "국민의힘",
    "이인선": "국민의힘",
    "임이자": "국민의힘",
    "최은석": "국민의힘",
    "권영세": "국민의힘",
    "차규근": "조국혁신당",
    "천하람": "개혁신당"
}




def extract_member_data(soup, name, member_id, response):
    try:
        name_el = soup.find('span', class_='sr-only')
        name = name_el.text.strip() if name_el else name
        party = party_mapping.get(name, "정보 없음")
        election_count, district, committee = "정보 없음", "정보 없음", "정보 없음"
        for dt in soup.find_all('dt'):
            if dt.text == '당선횟수':
                election_count = dt.find_next('dd').text.strip()[:2]
            elif dt.text == '선거구':
                district = dt.find_next('dd').text.strip()
            elif dt.text == '소속위원회':
                committee = dt.find_next('dd').text.strip()
        chief, senior, secretary = [], [], []
        for li in soup.find_all('li'):
            title = li.find('dt')
            value = li.find('dd')
            if not title or not value:
                continue
            role = title.text.strip()
            names = [n.strip() for n in value.text.split(',')]
            if '보좌관' in role:
                chief = names
            elif '선임비서관' in role:
                senior = names
            elif '비서관' in role:
                secretary = names
        return {
            "국회의원": {
                "이름": name,
                "정당": party,
                "당선횟수": election_count,
                "선거구": district,
                "소속위원회": committee
            },
            "보좌관": chief,
            "선임비서관": senior,
            "비서관": secretary,
            "메타데이터": {
                "url": f"https://www.assembly.go.kr/members/22nd/{member_id}",
                "status_code": response.status_code,
                "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    except Exception as e:
        return {
            "국회의원": {
                "이름": name,
                "정당": party_mapping.get(name, "정보 없음"),
                "당선횟수": "정보 없음",
                "선거구": "정보 없음",
                "소속위원회": "정보 없음"
            },
            "보좌관": [], "선임비서관": [], "비서관": [],
            "메타데이터": {
                "url": f"https://www.assembly.go.kr/members/22nd/{member_id}",
                "status_code": 500,
                "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
            }
        }

all_member_data = []
for name, member_id in members:
    try:
        url = f'https://www.assembly.go.kr/members/22nd/{member_id}'
        response = requests.get(url, cookies=cookies_members, headers=headers_members)
        soup = BeautifulSoup(response.text, 'html.parser')
        data = extract_member_data(soup, name, member_id, response)
        all_member_data.append(data)
    except Exception as e:
        print(f"[ERROR] {name} failed: {e}")

with open('assembly_member_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_member_data, f, ensure_ascii=False, indent=4)
print("✅ 국회의원 정보 저장 완료")

import requests
import json
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ### =============== 의안 정보 수집 (리뉴얼 XHR 방식) ===============
import json
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = "https://likms.assembly.go.kr"
PAGE_URL = f"{BASE}/bill/bi/bill/sch/detailedSchPage.do"
API_URL  = f"{BASE}/bill/bi/bill/sch/findSchPaging.do"

def normalize_title(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).strip()
    s = re.split(r"\s*\(", s, maxsplit=1)[0].strip()
    s = re.sub(r"\s+", " ", s)
    return s

def extract_csrf_token(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # meta csrf
    meta = soup.find("meta", {"name": re.compile("csrf", re.I)})
    if meta and meta.get("content"):
        return meta["content"].strip()

    # hidden input
    inp = soup.find("input", {"name": re.compile("csrf", re.I)})
    if inp and inp.get("value"):
        return inp["value"].strip()

    # UUID fallback
    m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", html, re.I)
    return m.group(1) if m else ""

def parse_rows_from_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # ✅ 지금 응답 구조에 맞는 selector
    rows = soup.select("#sch_list_sect table tbody tr")
    if not rows:
        return []

    parsed = []
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        bill_no = (tds[0].get("title") or tds[0].get_text(strip=True) or "").strip()

        title_td = tds[1]
        title_full = title_td.get_text(" ", strip=True)

        bill_id = ""
        a = title_td.find("a")
        if a and a.has_attr("onclick"):
            m = re.search(r"fGoDetail\('([^']+)'", a["onclick"])
            if m:
                bill_id = m.group(1)

        proposer_kind = tds[2].get_text(strip=True) if len(tds) > 2 else ""
        propose_date  = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        vote_date     = tds[4].get_text(strip=True) if len(tds) > 4 else ""
        vote_result   = tds[5].get_text(strip=True) if len(tds) > 5 else ""
        status        = tds[-1].get_text(strip=True) if len(tds) >= 2 else ""

        parsed.append({
            "bill_no": bill_no,
            "bill_id": bill_id,
            "bill_title": title_full,
            "proposer_kind": proposer_kind,
            "propose_date": propose_date,
            "vote_date": vote_date,
            "vote_result": vote_result,
            "status": status,
        })

    return parsed

def collect_bill_info_xhr(bill_name_exact: str, keyword: str, age="22", page=1, rows=50):
    """
    - keyword: billNm에 넣을 '짧은 검색어'(curl처럼)
    - bill_name_exact: 저장할 정확 법안명(화이트리스트)
    """
    target = normalize_title(bill_name_exact)

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Referer": PAGE_URL,
        "Origin": BASE,
    })

    # 1) 세션/CSRF 확보
    r0 = s.get(PAGE_URL, timeout=30)
    r0.raise_for_status()
    csrf = extract_csrf_token(r0.text)

    headers = {
        "Accept": "text/html, */*",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": PAGE_URL,
        "Origin": BASE,
    }
    if csrf:
        headers["X-CSRF-TOKEN"] = csrf

    # 2) ✅ 필터를 최대한 풀어서(전체/빈값) 우선 결과가 나오게
    data = {
        "reqPageId": "billSrch",
        "detailedTab": "billDtl",
        "billNm": keyword,             # ✅ 핵심: 짧은 키워드
        "ageFrom": age,
        "ageTo": age,
        "billKind": "전체",
        "proposerKind": "전체",
        "procGbnCd": "전체",
        "jntPrpslYn": "전체",
        "cmtResultCd": "전체",
        "mainResultCd": "전체",
        "mainUpdateYn": "전체",
        "expAddiYn": "전체",
        "budgetSubbillCd": "전체",
        "reexamYn": "전체",
        "lawStatus": "전체",

        # ❌ 대표발의 고정은 처음엔 빼기 (0건 원인 가능)
        # "representKindCd": "대표발의",
        "representKindCd": "전체",

        "page": str(page),
        "rows": str(rows),
        "schSorting": "score",
        "ordCd": "DESC",
    }

    r = s.post(API_URL, headers=headers, data=data, timeout=30)
    r.raise_for_status()

    parsed = parse_rows_from_html(r.text)

    if not parsed:
        # ✅ “화이트리스트 불일치”가 아니라 “검색 결과 자체가 없음”으로 메시지 분리
        print(f"ℹ️ [{bill_name_exact}] 검색 결과(행)가 없습니다. (keyword='{keyword}', HTTP {r.status_code})")
        # 디버그: 응답 앞부분 저장(로컬/액션 로그용)
        print(r.text[:400])
        return []

    now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
    out = []

    # 3) ✅ 결과가 여러 개일 수 있으니, 여기서 정확 제목만 저장
    for it in parsed:
        title_full = it["bill_title"]
        if normalize_title(title_full) != target:
            continue

        bill_id = it["bill_id"]
        out.append({
            "의안번호": it["bill_no"],
            "의안ID": bill_id,
            "의안명": {"text": title_full, "link": f"javascript:fGoDetail('{bill_id}', 'billSimpleSearch')" if bill_id else ""},
            "제안자구분": it["proposer_kind"],
            "제안일자": it["propose_date"],
            "의결일자": it["vote_date"],
            "의결결과": it["vote_result"],
            "주요내용": {"text": "주요내용 보기", "link": ""},
            "심사진행상태": it["status"],
            "상세URL": f"{BASE}/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else "",
            "수집일시": now,
        })

    # 정확 매칭이 너무 빡세서 0건이면, 어떤 제목이 내려오는지 로그로 확인할 수 있게 후보 몇 개 출력
    if not out:
        sample_titles = [x["bill_title"] for x in parsed[:5]]
        print(f"ℹ️ [{bill_name_exact}] 검색은 됐지만(행 {len(parsed)}개) 정확제목 매칭 0건. 예시: {sample_titles}")

    return out


# ✅ 법안명(저장 대상) -> 검색 키워드(billNm) 매핑 (curl 방식)
BILL_KEYWORDS = {
    "한국수출입은행법 일부개정법률안": "수출입은행",
    "경제안보를 위한 공급망 안정화 지원 기본법 일부개정법률안": "공급망 안정화",
    "첨단조선업의 경쟁력 강화 및 지원에 관한 특별법안": "첨단조선",
    "공공기관의 운영에 관한 법률 일부개정법률안": "공공기관 운영",
    "한국산업은행법 일부개정법률안": "산업은행",
    "2025년도에 발행하는 첨단전략산업기금채권에 대한 국가보증동의안": "국가보증동의",
    "중소기업은행법 일부개정법률안": "중소기업은행",
    "정부조직법 일부개정법률안": "정부조직법",
    "신용보증기금법 일부개정법률안": "신용보증기금",
    "동남권산업투자공사 설립 및 운영에 관한 법률안": "동남권산업투자공사",
    "충청권산업투자공사 설립 및 운영에 관한 법률안": "충청권산업투자공사",
    "기후위기 대응을 위한 탄소중립ㆍ녹색성장 기본법 일부개정법률안": "탄소중립",
}

bill_names = list(BILL_KEYWORDS.keys())

all_bills = []
for exact in bill_names:
    kw = BILL_KEYWORDS[exact]
    try:
        rows = collect_bill_info_xhr(bill_name_exact=exact, keyword=kw, age="22", page=1, rows=50)
        print(f"✅ [{exact}] {len(rows)}건 저장")
        all_bills.extend(rows)
    except Exception as e:
        print(f"⚠️ [{exact}] 실패: {type(e).__name__} - {e}")

with open("의안정보검색결과.json", "w", encoding="utf-8") as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=2)

print(f"✅ 의안 정보 저장 완료: {len(all_bills)}건")


### =============== 소위원회 정보 수집 ===============
# 세션 객체 생성
session = requests.Session()

# 메인 페이지 URL
main_url = 'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do?menuNo=2000014'

# 헤더 정의
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
}

try:
    # 메인 페이지 요청
    main_response = session.get(main_url, headers=headers)
    main_response.raise_for_status()

    # CSRF 메타 태그 추출
    soup = BeautifulSoup(main_response.text, 'html.parser')
    csrf_parameter = soup.find('meta', {'name': '_csrf_parameter'})
    csrf_header = soup.find('meta', {'name': '_csrf_header'})
    csrf_token = soup.find('meta', {'name': '_csrf'})

    if not all([csrf_parameter, csrf_header, csrf_token]):
        raise ValueError("CSRF 메타 태그를 찾을 수 없습니다.")

    csrf_parameter_value = csrf_parameter['content']
    csrf_header_value = csrf_header['content']
    csrf_token_value = csrf_token['content']

    # POST 요청 헤더 설정
    api_headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://finance.na.go.kr:444',
        'Referer': main_url,
        'User-Agent': headers['User-Agent'],
        'X-Requested-With': 'XMLHttpRequest',
        csrf_header_value: csrf_token_value
    }

    data = {
        'hgNm': '',
        'subCmtNm': '',
        'pageUnit': '9',
        'pageIndex': '',
        csrf_parameter_value: csrf_token_value
    }

    response = session.post(
        'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/getSubCmitLst.json',
        headers=api_headers,
        data=data
    )
    response.raise_for_status()
    response_data = response.json()

except requests.exceptions.RequestException as e:
    print(f"요청 실패: {e}")
    exit(1)
except json.JSONDecodeError as e:
    print(f"JSON 파싱 실패: {e}")
    print("응답 원문:", response.text)
    exit(1)
except Exception as e:
    print(f"오류 발생: {e}")
    exit(1)

# ◈이름 → 이름(長)으로 변환하는 함수
def parse_members(member_str):
    members = []
    for m in member_str.split(','):
        m = m.strip()
        if m.startswith('◈'):
            m = m.lstrip('◈')  # remove diamond
            if '(長)' not in m:
                name_part, sep, han_part = m.partition('(')
                m = f"(長){name_part}{sep}{han_part}"  # insert "(長)" before names
        members.append(m)
    return members

# 결과 딕셔너리 구성
result = {}

for item in response_data.get("resultList", []):
    committee_name = item["sbcmtNm"]
    count = item["naasCnt"]
    key = f"{committee_name}({count}인)"
    
    parties = {}
    if item.get("poly1NaasNm") and item.get("poly1NaasCn"):
        parties[item["poly1NaasNm"]] = parse_members(item["poly1NaasCn"])
    if item.get("poly2NaasNm") and item.get("poly2NaasCn"):
        parties[item["poly2NaasNm"]] = parse_members(item["poly2NaasCn"])
    if item.get("poly99NaasNm") and item.get("poly99NaasCn"):
        parties[item["poly99NaasNm"]] = parse_members(item["poly99NaasCn"])
    
    result[key] = parties

# 메타데이터 구성
metadata = {
    "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
    "url": main_url,
    "status_code": response.status_code
}

# 최종 결과 저장
final_result = {
    "소위원회_정보": result,
    "메타데이터": metadata
}

with open('소위원회정보.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)
print("✅ 소위원회 정보 저장 완료")















