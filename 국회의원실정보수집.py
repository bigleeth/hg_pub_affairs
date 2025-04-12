import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

cookies = {
    '_fwb': '224GIbJbv3W2VKbiHHpHIKa.1736910833680',
    '_ga': 'GA1.1.1553764147.1736910835',
    'PCID': '756e904c-0b66-a4a7-6836-589756f10a6e-1736910838628',
    'JSESSIONID': 'KHYMbxRBf39S41H5IaF3ItGp1lVaTFrc5Oa6tAm7pU1kWVnovMhmrtaSEBvSagwl.amV1c19kb21haW4vbmFob21lNA==',
    'PHAROSVISITOR': '00006eb50196285f2f296cc80ac965a6',
    'NetFunnel_ID': '',
    'wcs_bt': '1a0c69697fe3410:1744434067',
    '_ga_8FY090CL6Y': 'GS1.1.1744434048.5.1.1744434067.0.0.0',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

# 수집할 국회의원 목록
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
    ("박수민", "PARKSOOMIN")
]

# 정당 정보 매핑
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
    "송언석": "국민의힘",
    "박수영": "국민의힘",
    "구자근": "국민의힘",
    "박대출": "국민의힘",
    "박성훈": "국민의힘",
    "박수민": "국민의힘",
    "이인선": "국민의힘",
    "이종욱": "국민의힘",
    "최은석": "국민의힘",
    "차규근": "조국혁신당",
    "천하람": "개혁신당"
}

# 데이터 추출 함수
def extract_member_data(soup, name):
    try:
        # 의원명 추출 (sr-only 클래스를 가진 span 태그에서 추출)
        name_element = soup.find('span', class_='sr-only')
        name = name_element.text.strip() if name_element else "정보 없음"
        
        # 정당 정보 설정 (하드코딩된 매핑 사용)
        party = party_mapping.get(name, "정보 없음")
        
        # 당선횟수 정보 추출
        election_count_element = soup.find('dt', text='당선횟수')
        if election_count_element:
            election_count_text = election_count_element.find_next('dd').text.strip()
            # "제22대)"까지의 텍스트만 추출
            election_count = election_count_text.split('제22대)')[0] + '제22대)'
        else:
            election_count = "정보 없음"
            
        # 선거구 정보 추출
        district_element = soup.find('dt', text='선거구')
        district = district_element.find_next('dd').text.strip() if district_element else "정보 없음"
        
        # 소속위원회 정보 추출
        committee_element = soup.find('dt', text='소속위원회')
        committee = committee_element.find_next('dd').text.strip() if committee_element else "정보 없음"
        
        # 보좌관, 선임비서관, 비서관 정보 추출
        staff_list = soup.find_all('li')
        chief_staff = []
        senior_secretary = []
        secretary = []
        
        for item in staff_list:
            dt = item.find('dt')
            dd = item.find('dd')
            if dt and dd:
                title = dt.text.strip()
                names = [name.strip() for name in dd.text.split(',')]
                
                if '보좌관' in title:
                    chief_staff = names
                elif '선임비서관' in title:
                    senior_secretary = names
                elif '비서관' in title:
                    secretary = names
        
        return {
            "국회의원": {
                "이름": name,
                "정당": party,  # 하드코딩된 정당 정보 사용
                "당선횟수": election_count,
                "선거구": district,
                "소속위원회": committee
            },
            "보좌관": chief_staff,
            "선임비서관": senior_secretary,
            "비서관": secretary,
            "메타데이터": {
                "url": f"https://www.assembly.go.kr/members/22nd/{member_id}",
                "status_code": response.status_code,
                "수집일시": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
        }
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return {
            "국회의원": {
                "이름": "정보 없음",
                "정당": party_mapping.get(name, "정보 없음"),  # 오류 발생 시에도 하드코딩된 정당 정보 사용
                "당선횟수": "정보 없음",
                "선거구": "정보 없음",
                "소속위원회": "정보 없음"
            },
            "보좌관": [],
            "선임비서관": [],
            "비서관": [],
            "메타데이터": {
                "url": f"https://www.assembly.go.kr/members/22nd/{member_id}",
                "status_code": response.status_code,
                "수집일시": datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")
            }
        }

# 모든 의원의 데이터 수집
all_member_data = []
for name, member_id in members:
    try:
        response = requests.get(f'https://www.assembly.go.kr/members/22nd/{member_id}', cookies=cookies, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        member_data = extract_member_data(soup, name)
        all_member_data.append(member_data)
        print(f"{name} 의원 정보 수집 완료")
    except Exception as e:
        print(f"{name} 의원 정보 수집 중 오류 발생: {str(e)}")

# JSON 파일로 저장
with open('assembly_member_data.json', 'w', encoding='utf-8') as f:
    json.dump(all_member_data, f, ensure_ascii=False, indent=4)