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
    ("김상훈", "KIMSANGHOON"),
    ("윤한홍", "YOONHANHONG"),
    ("강훈식", "KANGHOONSIK"),
    ("김영환", "KIMYOUNGWHAN"),
    ("김태년", "KIMTAENYEON"),
    ("박홍근", "PARKHONGKEUN"),
    ("신영대", "SHINYEONGDAE"),
    ("안도걸", "AHNDOGEOL"),
    ("오기형", "OHGIHYOUNG"),
    ("윤호중", "YUNHOJUNG"),
    ("임광현", "LIMKWANGHYUN"),
    ("정성호", "JUNGSUNGHO"),
    ("정일영", "CHUNGILYOUNG"),
    ("진성준", "JINSUNGJOON"),
    ("손언서", "SONGEONSEOG"),
    ("박수영", "PARKSOOYOUNG"),
    ("구자근", "KUJAKEUN"),
    ("박대출", "PARKDAECHUL"),
    ("박성훈", "PARKSUNGHOON"),
    ("신동욱", "SHINDONGUK"),
    ("이인선", "LEEINSEON"),
    ("이종훤", "LEEJONHWOOK"),
    ("최은석", "CHOIEUNSEOK"),
    ("차규근", "CHAGYUGEUN"),
    ("천하람", "CHUNHARAM"),
    ("황명선", "HWANGMYEONGSEON"),
    ("최기상", "CHOIKISANG"),
    ("유동수", "YOODONGSOO"),
    ("이은주", "LEEUNJU"),
    ("박수민", "PARKSOOMIN"),
    ("권영세", "KWONYOUNGSE"),
    ("윤영석", "YOONYOUNGSEOK")
    # ... Add the rest
]
party_mapping = {
    "정태호": "더불어민주당",
    "김영진": "더불어민주당",
    "김영환": "더불어민주당",
    "김태년": "더불어민주당",
    "박홍근": "더불어민주당",
    "신영대": "더불어민주당",
    "안도걸": "더불어민주당",
    "오기형": "더불어민주당",
    "윤호중": "더불어민주당",
    "임광현": "더불어민주당",
    "정성호": "더불어민주당",
    "정일영": "더불어민주당",
    "진성준": "더불어민주당",
    "황명선": "더불어민주당",
    "최기상": "더불어민주당",
    "이언주": "더불어민주당",
    "유동수": "더불어민주당",
    "강훈식": "더불어민주당",
    "김상훈": "국민의힘",
    "윤한홍": "국민의힘",
    "신동욱": "국민의힘",
    "송언석": "국민의힘",
    "박수영": "국민의힘",
    "구자근": "국민의힘",
    "박대출": "국민의힘",
    "박성훈": "국민의힘",
    "박수민": "국민의힘",
    "이인선": "국민의힘",
    "이종욱": "국민의힘",
    "최은석": "국민의힘",
    "권영세": "국민의힘",
    "윤영석": "국민의힘",
    "차규근": "조국혁신당",
    "천하람": "개혁신당"
    # ... Add all
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


### =============== 의안 정보 수집 ===============
def collect_bill_info(bill_name):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://likms.assembly.go.kr',
        'Referer': 'https://likms.assembly.go.kr/bill/main.do',
        'User-Agent': 'Mozilla/5.0'
    }
    data = {
        'tabMenuType': 'billSimpleSearch',
        'hjNm': '', 'ageFrom': '22', 'ageTo': '22',
        'billKind': '전체', 'billName': bill_name
    }
    response = requests.post('https://likms.assembly.go.kr/bill/BillSearchResult.do', headers=headers, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    bills = []
    table = soup.find('table', {'summary': '검색결과의 의안번호, 의안명, 제안자구분, 제안일자, 의결일자, 의결결과, 주요내용, 심사진행상태 정보'})
    if table:
        rows = table.find_all('tr')[1:]
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:
                bill_a_tag = cols[1].find('a')
                bill_id = bill_a_tag.get('onclick', '').split("'")[1] if bill_a_tag and 'onclick' in bill_a_tag.attrs else ''

                content_a_tag = cols[6].find('a')
                content_id = content_a_tag.get('onclick', '').split("'")[1] if content_a_tag and 'onclick' in content_a_tag.attrs else ''

                bills.append({
                    '의안번호': cols[0].text.strip(),
                    '의안명': {
                        'text': cols[1].text.strip(),
                        'link': f"javascript:fGoDetail('{bill_id}', 'billSimpleSearch')" if bill_id else ''
                    },
                    '제안자구분': cols[2].text.strip(),
                    '제안일자': cols[3].text.strip(),
                    '의결일자': cols[4].text.strip(),
                    '의결결과': cols[5].text.strip(),
                    '주요내용': {
                        'text': '주요내용 보기',
                        'link': f"javascript:ajaxShowListSummaryLayerPopup('{content_id}')" if content_id else ''
                    },
                    '심사진행상태': cols[7].text.strip(),
                    "수집일시": datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")
                })
    return bills

bill_names = [
    "한국수출입은행법 일부개정법률안",
    "경제안보를 위한 공급망 안정화 지원 기본법 일부개정법률안",
    "첨단조선업의 경쟁력 강화 및 지원에 관한 특별법안",
    "공공기관의 운영에 관한 법률 일부개정법률안",
    "한국산업은행법 일부개정법률안",
    "2025년도에 발행하는 첨단전략산업기금채권에 대한 국가보증동의안",
    "중소기업은행법 일부개정법률안",
    "정부조직법 일부개정법률안"
]

all_bills = []
for bill_name in bill_names:
    all_bills.extend(collect_bill_info(bill_name))

with open('의안정보검색결과.json', 'w', encoding='utf-8') as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=4)
print("✅ 의안 정보 저장 완료")

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
