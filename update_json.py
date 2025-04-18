import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime

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
    ("김영진", "KIMYOUNGJIN"), ("정태호", "JUNGTAEHO"), ("김상훈", "KIMSANGHOON"), ("윤한홍", "YOONHANHONG"),
    # ... Add the rest
]
party_mapping = {
    "김영진": "더불어민주당", "정태호": "더불어민주당", "김상훈": "국민의힘", "윤한홍": "국민의힘",
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
                "수집일시": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
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
                "수집일시": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
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
                    '수집일시': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
cookies_subcmt = {
    '_ga': 'GA1.1.1112369851.1736910875',
    'JSESSIONID': 'your_valid_session',
}
headers_subcmt = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://finance.na.go.kr:444',
    'Referer': 'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do?menuNo=2000014',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5)',
    'X-Requested-With': 'XMLHttpRequest',
}
data_subcmt = {
    'hgNm': '', 'subCmtNm': '', 'pageUnit': '9', 'pageIndex': ''
}
response = requests.post(
    'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/getSubCmitLst.json',
    cookies=cookies_subcmt,
    headers=headers_subcmt,
    data=data_subcmt,
)
result = {
    "경제재정소위원회(11인)": {
        "더불어민주당": ["정태호(장)", "김영진", "윤호중", "정일영", "진성준", "황명선"],
        "국민의힘": ["박수영", "박대출", "박성훈", "이종욱"],
        "비교섭단체": ["차규근"]
    },
    "조세소위원회(13인)": {
        "더불어민주당": ["정태호", "김영환", "신영대", "안도걸", "오기형", "임광현", "최기상"],
        "국민의힘": ["박수영(장)", "박성훈", "신동욱", "이종욱", "최은석"],
        "비교섭단체": ["천하람"]
    },
    "예산결산기금심사소위원회(5인)": {
        "더불어민주당": ["정일영(장)", "김태년", "박홍근"],
        "국민의힘": ["이인선", "이종욱"]
    },
    "청원심사소위원회(5인)": {
        "더불어민주당": ["임광현(장)", "정성호", "최기상"],
        "국민의힘": ["구자근", "최은석"]
    }
}
metadata = {
    "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "url": "https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do",
    "status_code": response.status_code
}
final_result = {
    "소위원회_정보": result,
    "메타데이터": metadata
}
with open('소위원회정보.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)
print("✅ 소위원회 정보 저장 완료")

