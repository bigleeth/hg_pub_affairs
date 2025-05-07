import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

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

# ◈이름 → 이름(장)으로 변환하는 함수
def parse_members(member_str):
    members = []
    for m in member_str.split(','):
        m = m.strip()
        if m.startswith('◈'):
            m = m.lstrip('◈')  # remove diamond
            if '(장)' not in m:
                name_part, sep, han_part = m.partition('(')
                m = f"(장){name_part}{sep}{han_part}"  # insert "(장)" before names
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
    "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "url": main_url,
    "status_code": response.status_code
}

# 최종 결과 저장
final_result = {
    "소위원회_정보": result,
    "메타데이터": metadata
}

output_file = '소위원회정보.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)

print(f"\n✅ JSON 저장 완료: {output_file}")
