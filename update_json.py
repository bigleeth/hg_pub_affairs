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

import re
import unicodedata

def normalize_bill_title(title: str) -> str:
    if not title:
        return ""
    t = unicodedata.normalize("NFKC", title).strip()
    # 괄호 블록 전부 제거: ( ... ) 여러 번 있어도 반복 제거
    t = re.sub(r"\s*\([^)]*\)", "", t).strip()
    # 연속 공백 정리
    t = re.sub(r"\s+", " ", t).strip()
    return t

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import re

SEARCH_URL = "https://likms.assembly.go.kr/bill/bi/bill/sch/findSchPaging.do"
REFERER = "https://likms.assembly.go.kr/bill/bi/bill/sch/detailedSchPage.do"

def collect_bill_info(bill_name: str, session: requests.Session):
    # ✅ bill_name은 "정확 제목" (화이트리스트)
    target = normalize_bill_title(bill_name)

    data = {
        "reqPageId": "billSrch",
        "detailedTab": "billDtl",
        "billNm": bill_name,          # 또는 키워드(짧게) 넣고 아래에서 매칭
        "ageFrom": "22",
        "ageTo": "22",
        "billKind": "전체",
        "proposerKind": "전체",
        "procGbnCd": "전체",
        "page": "1",
        "rows": "50",
        "schSorting": "score",
        "ordCd": "DESC",
    }

    r = session.post(SEARCH_URL, data=data, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.select_one("table")
    if not table:
        return []

    results = []
    for tr in table.select("tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        # ✅ 여기! 의안명 칸(td[1])만 사용
        title_td = tds[1]
        raw_title = title_td.get_text(" ", strip=True)
        norm_title = normalize_bill_title(raw_title)

        if norm_title != target:
            continue

        bill_no = tds[0].get_text(strip=True)

        bill_id = ""
        a = title_td.find("a")
        if a and a.has_attr("onclick"):
            m = re.search(r"fGoDetail\('([^']+)'", a["onclick"])
            if m:
                bill_id = m.group(1)

        proposer_kind = tds[2].get_text(strip=True) if len(tds) > 2 else ""
        propose_date = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        status = tds[-1].get_text(strip=True) if len(tds) >= 8 else ""

        results.append({
            "의안번호": bill_no,
            "의안ID": bill_id,
            "의안명": raw_title,  # 원문 유지(괄호 포함)
            "제안자구분": proposer_kind,
            "제안일자": propose_date,
            "심사진행상태": status,
            "상세URL": f"https://likms.assembly.go.kr/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else "",
            "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return results


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
















