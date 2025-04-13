import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def collect_bill_info(bill_name):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://likms.assembly.go.kr',
        'Referer': 'https://likms.assembly.go.kr/bill/main.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    data = {
        'tabMenuType': 'billSimpleSearch',
        'billKindExclude': '',
        'hjNm': '',
        'ageFrom': '22',
        'ageTo': '22',
        'billKind': '전체',
        'generalResult': '',
        'proposerKind': '전체',
        'proposeGubn': '전체',
        'proposer': '',
        'empNo': '',
        'billNo': '',
        'billName': bill_name,
    }

    response = requests.post('https://likms.assembly.go.kr/bill/BillSearchResult.do', headers=headers, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    bills = []
    table = soup.find('table', {'summary': '검색결과의 의안번호, 의안명, 제안자구분, 제안일자, 의결일자, 의결결과, 주요내용, 심사진행상태 정보'})
    
    if table:
        rows = table.find_all('tr')[1:]  # 헤더 행 제외
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 8:
                # 의안명 링크에서 billId 추출
                bill_name_link = cols[1].find('a')
                bill_id = ''
                if bill_name_link and 'onclick' in bill_name_link.attrs:
                    onclick_text = bill_name_link['onclick']
                    if 'fGoDetail' in onclick_text:
                        bill_id = onclick_text.split("'")[1]
                
                # 주요내용 링크에서 billId 추출
                content_link = cols[6].find('a')
                content_bill_id = ''
                if content_link and 'onclick' in content_link.attrs:
                    onclick_text = content_link['onclick']
                    if 'ajaxShowListSummaryLayerPopup' in onclick_text:
                        content_bill_id = onclick_text.split("'")[1]
                
                bill = {
                    '의안번호': cols[0].text.strip(),
                    '의안명': {
                        'text': cols[1].text.strip(),
                        'link': f'javascript:fGoDetail(\'{bill_id}\', \'billSimpleSearch\')' if bill_id else ''
                    },
                    '제안자구분': cols[2].text.strip(),
                    '제안일자': cols[3].text.strip(),
                    '의결일자': cols[4].text.strip(),
                    '의결결과': cols[5].text.strip(),
                    '주요내용': {
                        'text': '주요내용 보기',
                        'link': f'javascript:ajaxShowListSummaryLayerPopup(\'{content_bill_id}\')' if content_bill_id else ''
                    },
                    '심사진행상태': cols[7].text.strip()
                }
                bills.append(bill)
    
    return bills

# 예시 사용
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
    bills = collect_bill_info(bill_name)
    all_bills.extend(bills)

# 결과를 JSON 파일로 저장
with open('의안정보검색결과.json', 'w', encoding='utf-8') as f:
    json.dump(all_bills, f, ensure_ascii=False, indent=4)

# 결과를 DataFrame으로 변환하여 출력
df = pd.DataFrame(all_bills)
print(df)
