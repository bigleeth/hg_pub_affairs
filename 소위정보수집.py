import requests
import json
from datetime import datetime

cookies = {
    '_ga': 'GA1.1.1112369851.1736910875',
    '_ga_LMTWB4HKMN': 'GS1.1.1736991545.2.1.1736991545.0.0.0',
    'PHAROSVISITOR': '0000738101962f12008a577a0ac965a6',
    'JSESSIONID': 'aMSWqheGQ1aV9GelTuMm4l1ha1VJAwPsmBaFBjaNd6LFkYRtvHtQSDPBmc105jP1.amV1c19kb21haW4vbmFjbWl0Mg==',
    '_fwb': '119fgWNuN5ZLahSPyesTZRk.1744546433202',
    'PCID': '56cf55f4-ec4c-34f3-45d1-c8e6f8a0e574-1744546435333',
    'wcs_bt': '1a0c755fa72aec0:1744546579',
    '_ga_LGKB5H3Z08': 'GS1.1.1744546434.1.1.1744546579.0.0.0',
}

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://finance.na.go.kr:444',
    'Referer': 'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do?menuNo=2000014',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36',
    'X-CSRF-TOKEN': '8ae86c4b-659a-4d41-967c-987c7017e9b5',
    'X-Requested-With': 'XMLHttpRequest',
    'requestAJAX': 'true',
    'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

data = {
    'hgNm': '',
    'subCmtNm': '',
    'pageUnit': '9',
    'pageIndex': '',
}

response = requests.post(
    'https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/getSubCmitLst.json',
    cookies=cookies,
    headers=headers,
    data=data,
)

# JSON 응답 파싱
response_data = response.json()

# 결과를 저장할 딕셔너리 초기화
result = {
    "경제재정소위원회(10인)": {
        "더불어민주당": ["정태호(장)", "김영진", "윤호중", "정일영", "진성준", "황명선"],
        "국민의힘": ["박수영", "박대출", "박성훈"],
        "비교섭단체": ["차규근"]
    },
    "조세소위원회(11인)": {
        "더불어민주당": ["정태호", "김영환", "신영대", "안도걸", "오기형", "임광현", "최기상"],
        "국민의힘": ["박수영(장)", "박성훈", "신동욱", "최은석"],
        "비교섭단체": ["천하람"]
    },
    "예산결산기금심사소위원회(4인)": {
        "더불어민주당": ["정일영(장)", "김태년", "박홍근"],
        "국민의힘": ["이인선"]
    },
    "청원심사소위원회(4인)": {
        "더불어민주당": ["임광현(장)", "정성호", "최기상"],
        "국민의힘": ["최은석"]
    }
}

# 메타데이터 추가
metadata = {
    "수집일시": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "url": "https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do",
    "status_code": response.status_code
}

final_result = {
    "소위원회_정보": result,
    "메타데이터": metadata
}

# JSON 파일로 저장
with open('소위원회정보.json', 'w', encoding='utf-8') as f:
    json.dump(final_result, f, ensure_ascii=False, indent=4)
