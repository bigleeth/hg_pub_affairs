import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

# 세션 객체 생성
session = requests.Session()

# 메인 페이지 URL
main_url = 'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do?menuNo=2000014'

# 기본 헤더
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    # 메인 페이지 접속
    main_response = session.get(main_url, headers=headers)
    main_response.raise_for_status()
    
    # CSRF 토큰 추출
    soup = BeautifulSoup(main_response.text, 'html.parser')
    csrf_parameter = soup.find('meta', {'name': '_csrf_parameter'})
    csrf_header = soup.find('meta', {'name': '_csrf_header'})
    csrf_token = soup.find('meta', {'name': '_csrf'})

    if not all([csrf_parameter, csrf_header, csrf_token]):
        raise ValueError("CSRF 메타 태그를 찾을 수 없습니다.")

    csrf_parameter_value = csrf_parameter['content']
    csrf_header_value = csrf_header['content']
    csrf_token_value = csrf_token['content']

    # API 요청 헤더 설정
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

    # POST 요청
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

# 결과 파싱
result = {}
for item in response_data["resultList"]:
    committee_name = item["sbcmtNm"]
    count = item["naasCnt"]
    key = f"{committee_name}({count}인)"
    
    parties = {}
    if item.get("poly1NaasNm") and item.get("poly1NaasCn"):
        parties[item["poly1NaasNm"]] = [x.strip(" ◈") for x in item["poly1NaasCn"].split(",")]
    if item.get("poly2NaasNm") and item.get("poly2NaasCn"):
        parties[item["poly2NaasNm"]] = [x.strip(" ◈") for x in item["poly2NaasCn"].split(",")]
    if item.get("poly99NaasNm") and item.get("poly99NaasCn"):
        parties[item["poly99NaasNm"]] = [x.strip(" ◈") for x in item["poly99NaasCn"].split(",")]

    result[key] = parties

# 메타데이터 추가
metadata = {
    "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "url": main_url,
    "status_code": response.status_code
}

# 최종 결과 구성
final_result = {
    "소위원회_정보": result,
    "메타데이터": metadata
}

# JSON 파일로 저장
output_path = '소위원회정보.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)

print(f"\n✅ JSON 저장 완료: {output_path}")
