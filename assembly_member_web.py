import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import subprocess

# 페이지 설정
st.set_page_config(
    page_title="국회 모니터링(수은 대외팀)",
    page_icon="🏛️",
    layout="wide"
)

# 스타일 설정
st.markdown("""
    <style>
    /* 기본 폰트 크기 설정 */
    h1 {
        font-size: 1.5rem !important;
    }
    h2 {
        font-size: 1.2rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
    }
    .stDataFrame {
        width: 100%;
        font-size: 0.9rem;
    }
    .highlight {
        background-color: yellow;
    }
    .info-box {
        padding: 15px;
        margin-top: 20px;
        color: #666;
        font-size: 0.9rem;
    }
    .info-box h3 {
        color: #666;
        margin-bottom: 10px;
        font-size: 1rem;
    }
    .info-box ul {
        margin: 0;
        padding-left: 20px;
    }
    .info-box li {
        margin-bottom: 5px;
    }
    .copyright {
        text-align: center;
        color: #666;
        font-size: 0.8rem;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    /* 사이드바 폰트 크기 조정 */
    .sidebar .sidebar-content {
        font-size: 0.9rem;
    }
    .sidebar .sidebar-content .stSelectbox {
        font-size: 0.9rem;
    }
    .small-button {
        font-size: 0.8em;
        padding: 0.2em 0.5em;
        background-color: #f0f0f0;
        color: #666;
        border: 1px solid #ddd;
        border-radius: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
    <h1 style="margin-bottom: 1rem;">🚀국회 모니터링 - 수은 대외팀🚀</h1>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data(ttl=0)  # 24시간(86400초)마다 캐시 갱신
def load_data():
    try:
        # GitHub에서 최신 데이터 가져오기
        response = requests.get('https://raw.githubusercontent.com/your-repo/assembly_member_data.json')
        if response.status_code == 200:
            data = response.json()
            
            # 로컬 파일에 저장
            with open('assembly_member_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            # GitHub에서 가져오기 실패 시 로컬 파일 사용
            with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
        # 데이터프레임으로 변환
        df = pd.DataFrame([
            {
                '이름': member['국회의원']['이름'],
                '정당': member['국회의원'].get('정당', '정보 없음'),
                '당선횟수': member['국회의원']['당선횟수'][:2],
                '선거구': member['국회의원']['선거구'],
                '소속위원회': member['국회의원']['소속위원회'],
                '보좌관': ','.join(member['보좌관']),
                '선임비서관': ','.join(member['선임비서관']),
                '비서관': ','.join(member['비서관']),
                '변경사항': '',  # 변경사항 열 추가
                'URL': member['메타데이터']['url'],
                '수집일시': member['메타데이터']['수집일시']
            }
            for member in data
        ])
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")
        return None

# 스냅샷 리셋 함수
def reset_snapshot(password):
    if password == "0204":
        try:
            # 현재 데이터를 스냅샷으로 저장
            with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
                current_data = json.load(f)
            
            # 현재 시간을 메타데이터에 추가
            current_time = datetime.now().strftime("%Y년 %m월 %d일 %H시 %M분")
            for member in current_data:
                member['메타데이터']['스냅샷_생성일시'] = current_time
            
            # 스냅샷 파일에 저장
            with open('assembly_member_snapshot.json', 'w', encoding='utf-8') as f:
                json.dump(current_data, f, ensure_ascii=False, indent=4)
            
            st.success("스냅샷이 성공적으로 업데이트되었습니다.")
            st.rerun()
        except Exception as e:
            st.error(f"스냅샷 업데이트 중 오류 발생: {str(e)}")
    else:
        st.error("비밀번호가 올바르지 않습니다.")

# 스냅샷 데이터 로드 함수
@st.cache_data(ttl=0)
def load_snapshot():
    try:
        if os.path.exists('assembly_member_snapshot.json'):
            with open('assembly_member_snapshot.json', 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
                # 스냅샷 파일의 생성 시간 가져오기
                snapshot_time = snapshot_data[0]['메타데이터'].get('수집일시', '시간 정보 없음')
                # 날짜 형식 변환
                try:
                    date_obj = datetime.strptime(snapshot_time, "%a, %d %b %Y %H:%M:%S GMT")
                    formatted_date = date_obj.strftime("%Y년 %m월 %d일")
                except:
                    formatted_date = snapshot_time
                return snapshot_data, formatted_date
        else:
            st.warning("스냅샷 파일이 존재하지 않습니다.")
            return None, None
    except Exception as e:
        st.error(f"스냅샷 로드 중 오류 발생: {str(e)}")
        return None, None

# 데이터 비교 및 하이라이트 함수
def get_flat_string(value):
    if isinstance(value, list):
        return ','.join([str(x).strip() for x in value])
    return str(value).strip()

def compare_members(current, snapshot):
    diffs = []
    for key in ['이름', '정당', '당선횟수', '선거구', '소속위원회', '보좌관', '선임비서관', '비서관']:
        cur_val = get_flat_string(current.get(key, ''))
        snap_val = get_flat_string(snapshot.get(key, ''))
        if cur_val != snap_val:
            diffs.append(f"{key} 변경")
    return ', '.join(diffs)

def highlight_changes(df, snapshot_data):
    if snapshot_data is None:
        return df
        
    # 스냅샷 데이터를 빠른 조회를 위한 딕셔너리로 변환
    snapshot_dict = {
        member['메타데이터']['url']: {
            '이름': member['국회의원']['이름'],
            '정당': member['국회의원'].get('정당', ''),
            '당선횟수': member['국회의원'].get('당선횟수', ''),
            '선거구': member['국회의원'].get('선거구', ''),
            '소속위원회': member['국회의원'].get('소속위원회', ''),
            '보좌관': member.get('보좌관', []),
            '선임비서관': member.get('선임비서관', []),
            '비서관': member.get('비서관', [])
        }
        for member in snapshot_data
    }
    
    # 변경사항을 저장할 새로운 열 추가
    df['변경사항'] = ''
    
    # 각 행에 대해 변경사항 비교
    for idx, row in df.iterrows():
        url = row['URL']
        if url in snapshot_dict:
            current_flat = {
                '이름': row['이름'],
                '정당': row['정당'],
                '당선횟수': row['당선횟수'],
                '선거구': row['선거구'],
                '소속위원회': row['소속위원회'],
                '보좌관': row['보좌관'],
                '선임비서관': row['선임비서관'],
                '비서관': row['비서관']
            }
            snapshot_flat = snapshot_dict[url]
            df.at[idx, '변경사항'] = compare_members(current_flat, snapshot_flat)
    
    return df

def collect_bill_info(member_name):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://likms.assembly.go.kr',
        'Referer': 'https://likms.assembly.go.kr/bill/main.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    data = {
        'tabMenuType': 'billSimpleSearch',
        'billKindExclude': '',
        'hjNm': member_name,
        'ageFrom': '22',
        'ageTo': '22',
        'billKind': '전체',
        'generalResult': '',
        'proposerKind': '전체',
        'proposeGubn': '전체',
        'proposer': '',
        'empNo': '',
        'billNo': '',
        'billName': '',
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

import streamlit.components.v1 as components

def main():
    # 데이터 로드
    df = load_data()
    if df is None:
        return

    # 스냅샷 데이터 로드
    snapshot_data, snapshot_date = load_snapshot()
    
    # 데이터프레임 표시
    if snapshot_data:
        df = highlight_changes(df, snapshot_data)
        df = df.sort_values('이름', ascending=True)
        st.markdown("### 🏛️ 국회의원 정보 (변경 항목 표시)")
    else:
        df = df.sort_values('이름', ascending=True)
        st.markdown("### 🏛️ 국회의원 정보")
    
    # 필터링 옵션
    st.sidebar.header("필터")
    st.sidebar.subheader("국회의원 정보 필터")

    parties = ['전체'] + sorted(df['정당'].unique().tolist())
    selected_party = st.sidebar.selectbox('정당', parties)
    
    committees = ['전체'] + sorted(df['소속위원회'].unique().tolist())
    selected_committee = st.sidebar.selectbox('소속위원회', committees)
    
    districts = ['전체'] + sorted(df['선거구'].unique().tolist())
    selected_district = st.sidebar.selectbox('선거구', districts)

    # 필터 적용
    filtered_df = df.copy()
    if selected_party != '전체':
        filtered_df = filtered_df[filtered_df['정당'] == selected_party]
    if selected_committee != '전체':
        filtered_df = filtered_df[filtered_df['소속위원회'] == selected_committee]
    if selected_district != '전체':
        filtered_df = filtered_df[filtered_df['선거구'] == selected_district]

    # 국회의원 데이터 표시
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "URL": st.column_config.LinkColumn("URL"),
            "수집일시": st.column_config.DatetimeColumn("수집일시")
        }
    )

    # 국회 바로가기 링크
    st.markdown("""
    <div style="text-align: right; margin-top: 10px;">
        <a href="https://www.assembly.go.kr/" target="_blank">국회 바로가기</a>
    </div>
    """, unsafe_allow_html=True)

     # 법률안 발의내역 표시
    st.markdown("### 📜 법률안 발의내역")
    try:
        with open('의안정보검색결과.json', 'r', encoding='utf-8') as f:
            bill_data = json.load(f)
            
        # DataFrame으로 변환
        bill_df = pd.DataFrame([
            {
                '의안번호': bill['의안번호'],
                '의안명': bill['의안명']['text'],
                '제안자구분': bill['제안자구분'],
                '제안일자': bill['제안일자'],
                '의결일자': bill['의결일자'],
                '의결결과': bill['의결결과'],
                '심사진행상태': bill['심사진행상태'],
                '수집일시': bill.get('수집일시', '')
            }
            for bill in bill_data
        ])
        
        # 법률안 필터 적용
        if selected_bill != '전체':
            # 괄호 앞의 법률안 이름만 비교
            bill_df['의안명_순수'] = bill_df['의안명'].apply(lambda x: x.split('(')[0].strip() if '(' in x else x)
            bill_df = bill_df[bill_df['의안명_순수'] == selected_bill]
            bill_df = bill_df.drop('의안명_순수', axis=1)
        if selected_proposer != '전체':
            bill_df = bill_df[bill_df['제안자구분'] == selected_proposer]
        if selected_status != '전체':
            bill_df = bill_df[bill_df['심사진행상태'] == selected_status]
        
        # 제안일자 기준으로 내림차순 정렬
        bill_df['제안일자'] = pd.to_datetime(bill_df['제안일자']).dt.strftime('%Y-%m-%d')
        bill_df = bill_df.sort_values('제안일자', ascending=False)
        
        st.dataframe(
            bill_df,
            use_container_width=True,
            hide_index=True,
            height=350
        )
        
        # 의안정보시스템 링크 추가
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <a href="https://likms.assembly.go.kr/bill/main.do" target="_blank">의안정보시스템 바로가기</a>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning("법률안 발의내역 데이터를 불러오는 중 오류가 발생했습니다.")
    
    # 소위원회 정보 표시
    st.markdown("### 🐮 소위원회 정보")
    try:
        with open('소위원회정보.json', 'r', encoding='utf-8') as f:
            subcommittee_data = json.load(f)
            
        # 소위원회 정보를 DataFrame으로 변환
        subcommittee_rows = []
        for committee_name, parties in subcommittee_data['소위원회_정보'].items():
            row = {'소위원회': committee_name}
            for party, members in parties.items():
                row[party] = ', '.join(members)
            row['수집일시'] = subcommittee_data['메타데이터']['수집일시']
            subcommittee_rows.append(row)
        
        subcommittee_df = pd.DataFrame(subcommittee_rows)
        
        # 소위원회 필터를 왼쪽 사이드바로 이동
        st.sidebar.subheader("소위원회 필터")
        selected_subcommittee = st.sidebar.selectbox('소위원회', ['전체'] + sorted(subcommittee_df['소위원회'].unique().tolist()))
        
        # 필터링 적용
        if selected_subcommittee != '전체':
            subcommittee_df = subcommittee_df[subcommittee_df['소위원회'] == selected_subcommittee]
        
        # 열 순서 재정렬
        column_order = ['소위원회', '더불어민주당', '국민의힘', '비교섭단체', '수집일시']
        subcommittee_df = subcommittee_df.reindex(columns=column_order)
        
        st.dataframe(
            subcommittee_df,
            use_container_width=True,
            hide_index=True,
            height=177
        )
        
        # 기획재정위원회 링크 추가
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <a href="https://finance.na.go.kr/" target="_blank">기획재정위원회 바로가기</a>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning("소위원회 정보를 불러오는 중 오류가 발생했습니다.")
        st.exception(e)  # 상세 에러 표시
        
    # 알리오 공시정보
    st.markdown("""
    <div style="margin-top: 20px; margin-bottom: 10px;">
        <h3 style="text-align: left;">📊 알리오 공시정보</h3>
        <div style="text-align: right;">
            <a href="https://www.alio.go.kr/" target="_blank">알리오 공시 바로가기</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ✅ 주요 기사 스크랩
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 10px;">
        <h3 style="text-align: left;">📰 주요 기사 스크랩</h3>
        <div style="text-align: right;">
            <a href="https://docs.google.com/spreadsheets/d/1S6kHf5QTrSKUUraZs_zYujEt5569orB7m_CqYhC_siI/edit?usp=sharing" target="_blank">원본 보기</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    components.iframe(
        src="https://docs.google.com/spreadsheets/d/e/2PACX-1vRyMSJz7jKdfcfXxCyZO_PChyvF4RJneX0udD7blirttmnkCRdHo_oZK0LXe-KssExONv0TA9kNJGAg/pubhtml",
        height=500,
        scrolling=True
    )

    # 안내 메시지
    st.markdown(f"""
    <div class="info-box">
        <h3>📌 안내사항</h3>
        <ul>
            <li>수은 업무 관련 국회의원 및 법률안 발의내역 등 정보가 나타나 있습니다.</li>
            <li>국회의원 정보 변경사항은 기준일({snapshot_date}) 스냅샷 대비 현시점 달라진 내역을 나타냅니다.(예: 소속위원회 변경, 보좌진 변경 등)</li>
            <li>데이터는 매일 자동으로 업데이트됩니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 요청사항 메시지
    st.markdown("""
    <div class="info-box">
        <h3>💬 요청사항</h3>
        <ul>
            <li>요청사항은 쪽지로 보내주세요. (모니터링 국회의원, 법률안 추가 등)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # (You can continue with your snapshot viewer, etc. below...)



    # 스냅샷 데이터 보기
    with st.expander("📸 기준일 스냅샷 보기", expanded=False):
        if snapshot_data:
            # 스냅샷 데이터를 빠른 조회를 위한 딕셔너리로 변환
            snapshot_dict = {
                member['메타데이터']['url']: {
                    '이름': member['국회의원']['이름'],
                    '정당': member['국회의원'].get('정당', ''),
                    '당선횟수': member['국회의원'].get('당선횟수', ''),
                    '선거구': member['국회의원'].get('선거구', ''),
                    '소속위원회': member['국회의원'].get('소속위원회', ''),
                    '보좌관': member.get('보좌관', []),
                    '선임비서관': member.get('선임비서관', []),
                    '비서관': member.get('비서관', [])
                }
                for member in snapshot_data
            }
            
            # 스냅샷 데이터프레임 생성
            snapshot_df = pd.DataFrame([
                {
                    '이름': member['국회의원']['이름'],
                    '정당': member['국회의원'].get('정당', ''),
                    '당선횟수': member['국회의원'].get('당선횟수', '')[:2],
                    '선거구': member['국회의원'].get('선거구', ''),
                    '소속위원회': member['국회의원'].get('소속위원회', ''),
                    '보좌관': ','.join(member.get('보좌관', [])),
                    '선임비서관': ','.join(member.get('선임비서관', [])),
                    '비서관': ','.join(member.get('비서관', [])),
                    'URL': member['메타데이터']['url'],
                    '스냅샷 수집일시': member['메타데이터']['수집일시']
                }
                for member in snapshot_data
            ])
            
            # 변경사항 비교
            for idx, row in snapshot_df.iterrows():
                url = row['URL']
                if url in snapshot_dict:
                    current_flat = {
                        '이름': row['이름'],
                        '정당': row['정당'],
                        '당선횟수': row['당선횟수'],
                        '선거구': row['선거구'],
                        '소속위원회': row['소속위원회'],
                        '보좌관': row['보좌관'],
                        '선임비서관': row['선임비서관'],
                        '비서관': row['비서관']
                    }
                    snapshot_flat = snapshot_dict[url]
                    snapshot_df.at[idx, '변경사항'] = compare_members(current_flat, snapshot_flat)
            
            st.dataframe(
                snapshot_df,
                use_container_width=True,
                hide_index=True,
                height=400,
                column_config={
                    "변경사항": st.column_config.TextColumn("변경사항"),
                    "URL": st.column_config.LinkColumn("URL"),
                    "스냅샷 수집일시": st.column_config.DatetimeColumn("스냅샷 수집일시")
                }
            )
        else:
            st.warning("스냅샷 데이터가 없습니다.")

    # 저작권 정보
    st.markdown("""
    <div class="copyright">
        © 2025 Taehyun Lee. This dashboard is for non-commercial use only. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
