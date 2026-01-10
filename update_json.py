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


# ### =============== 의안 정보 수집 ===============
import json
import re
import unicodedata
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

SEARCH_URL = "https://likms.assembly.go.kr/bill/bi/bill/sch/detailedSchPage.do"

def normalize_bill_title(title: str) -> str:
    """
    - NFKC 정규화 (특수 공백/문자 변형 방지)
    - 괄호 이후 제거: "법률안(○○의원 등)" -> "법률안"
    - 양끝 공백 제거
    """
    if not title:
        return ""
    t = unicodedata.normalize("NFKC", title).strip()
    t = re.split(r"\s*\(", t, maxsplit=1)[0].strip()
    return t

def collect_bill_info(bill_name: str):
    # 상세검색(.detailedSchPage) 대신 간편검색(.billSimpleSearch) 사용
    # 간편검색이 키워드 매칭(GET방식)에 훨씬 안정적입니다.
    URL = "https://likms.assembly.go.kr/bill/bi/bill/sch/billSimpleSearch.do"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": URL,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })

    # 간편 검색 파라미터: searchStr
    params = {
        "searchStr": bill_name,
        "searchGubun": "1"  # 1: 의안명 검색
    }

    try:
        r = session.get(URL, params=params, timeout=30)
        r.raise_for_status()
    except Exception as e:
        print(f"⚠️ [요청 실패] {bill_name}: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    # 간편검색 결과 테이블의 행 선택자 (tableDisplay01 클래스 내부의 tbody tr)
    rows = soup.select("div.tableDisplay01 > table > tbody > tr")

    # 검색 결과 없음 처리
    if not rows:
        print(f"ℹ️ [{bill_name}] 검색 결과가 없습니다.")
        return []
        
    # '검색된 자료가 없습니다' 텍스트가 있는 행이 나오면 빈 리스트 반환
    if len(rows) == 1 and "자료가 없습니다" in rows[0].get_text():
        print(f"ℹ️ [{bill_name}] 검색 결과가 없습니다 (사이트 응답).")
        return []

    target = normalize_bill_title(bill_name)
    print(f"🔍 [{bill_name}] 검색 완료 (발견: {len(rows)}건)")

    bills = []
    
    for row in rows:
        tds = row.find_all("td")
        # 간편검색 결과 테이블 컬럼 개수 확인 (보통 6~7개)
        if len(tds) < 5:
            continue

        # 의안번호 (1번째 컬럼)
        bill_no = tds[0].get_text(strip=True)

        # 의안명 (2번째 컬럼)
        title_td = tds[1]
        bill_title_full = title_td.get_text(" ", strip=True)
        
        # billId 추출 (onclick 이벤트 파싱)
        bill_id = ""
        a = title_td.find("a")
        if a and a.has_attr("onclick"):
            # 예: fGoDetail('PRC_A1B2...', 'billSimpleSearch')
            m = re.search(r"fGoDetail\(['\"]([^'\"]+)['\"]", a["onclick"])
            if m:
                bill_id = m.group(1)

        # 제안자 (3번째 컬럼)
        proposer = tds[2].get_text(strip=True)
        
        # 제안일자 (4번째 컬럼)
        propose_date = tds[3].get_text(strip=True)
        
        # 심사진행상태 (6번째 컬럼) - 테이블 구조에 따라 인덱스 확인 필요
        # 보통: 번호 | 의안명 | 제안자 | 제안일자 | 의결일자 | 의결결과 | 심사진행상태
        # 따라서 tds[6]일 가능성이 높으나, 안전하게 맨 뒤에서 가져오거나 텍스트 매칭
        status = tds[-1].get_text(strip=True) 

        # 필터링: 검색어가 제목에 포함되는지 확인
        if bill_name.replace(" ", "") not in bill_title_full.replace(" ", ""):
            continue

        print(f"   ✅ 수집 성공: {bill_title_full}")

        bills.append({
            "의안번호": bill_no,
            "의안ID": bill_id,
            "의안명": {
                "text": bill_title_full,
                "link": f"https://likms.assembly.go.kr/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else ""
            },
            "제안자": proposer,
            "제안일자": propose_date,
            "심사진행상태": status,
            "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S"),
        })

    return bills


# ✅ 이 법률들만 저장(사용자 요구 반영)
bill_names = [
    "한국수출입은행법 일부개정법률안",
    "경제안보를 위한 공급망 안정화 지원 기본법 일부개정법률안",
    "첨단조선업의 경쟁력 강화 및 지원에 관한 특별법안",
    "공공기관의 운영에 관한 법률 일부개정법률안",
    "한국산업은행법 일부개정법률안",
    "2025년도에 발행하는 첨단전략산업기금채권에 대한 국가보증동의안",
    "중소기업은행법 일부개정법률안",
    "정부조직법 일부개정법률안",
    "신용보증기금법 일부개정법률안",
    "동남권산업투자공사 설립 및 운영에 관한 법률안",
    "충청권산업투자공사 설립 및 운영에 관한 법률안",
    "기후위기 대응을 위한 탄소중립ㆍ녹색성장 기본법 일부개정법률안"
]

all_bills = []
for name in bill_names:
    try:
        rows = collect_bill_info(name)
        all_bills.extend(rows)
        print(f"✅ [{name}] {len(rows)}건 수집")
    except Exception as e:
        print(f"⚠️ [{name}] 수집 실패: {e}")

with open("의안정보검색결과.json", "w", encoding="utf-8") as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=4)

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









