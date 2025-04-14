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

# 실시간 데이터 조회 함수
@st.cache_data(ttl=3600)  # 1시간마다 캐시 갱신
def fetch_assembly_member_data():
    try:
        # 국회의원 정보 조회
        url = "https://www.assembly.go.kr/assm/memact/congressman/memCond/memCondListAjax.do"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "currentPage": 1,
            "rowPerPage": 300
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # JSON 데이터 파싱
        data = response.json()
        members = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for member in data.get('memberList', []):
            member_info = {
                '이름': member.get('empNm', ''),
                '정당': member.get('polyNm', ''),
                '당선횟수': member.get('reeleGbnNm', ''),
                '선거구': member.get('origNm', ''),
                '소속위원회': member.get('shrtNm', ''),
                'URL': f"https://www.assembly.go.kr/assm/memact/congressman/memCond/memCondListAjax.do?currentPage=1&rowPerPage=10&memNo={member.get('memNo', '')}"
            }
            members.append(member_info)
        
        return pd.DataFrame(members), current_time
    except Exception as e:
        st.error(f"국회의원 정보 조회 중 오류 발생: {str(e)}")
        return None, None

# 의안 정보 조회 함수
@st.cache_data(ttl=3600)  # 1시간마다 캐시 갱신
def fetch_bill_data():
    try:
        # 의안 정보 조회
        url = "https://likms.assembly.go.kr/bill/billSearchResultAjax.do"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "currentPage": 1,
            "rowPerPage": 100,
            "billKind": "BILL"  # 법률안
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # JSON 데이터 파싱
        data = response.json()
        bills = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for bill in data.get('billList', []):
            bill_info = {
                '의안번호': bill.get('billNo', ''),
                '의안명': bill.get('billName', ''),
                '제안자': bill.get('proposer', ''),
                '제안일자': bill.get('proposeDt', ''),
                '소관위원회': bill.get('commName', ''),
                'URL': f"https://likms.assembly.go.kr/bill/billDetail.do?billId={bill.get('billId', '')}"
            }
            bills.append(bill_info)
        
        return pd.DataFrame(bills), current_time
    except Exception as e:
        st.error(f"의안 정보 조회 중 오류 발생: {str(e)}")
        return None, None

# 소위원회 정보 조회 함수
@st.cache_data(ttl=3600)  # 1시간마다 캐시 갱신
def fetch_subcommittee_data():
    try:
        # 소위원회 정보 조회
        url = "https://www.assembly.go.kr/assm/comm/commListAjax.do"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest"
        }
        params = {
            "currentPage": 1,
            "rowPerPage": 100,
            "commCd": "C0101"  # 소위원회 코드
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # JSON 데이터 파싱
        data = response.json()
        subcommittees = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for committee in data.get('commList', []):
            committee_info = {
                '소위원회명': committee.get('commNm', ''),
                '위원장': committee.get('chairNm', ''),
                '위원수': committee.get('memCnt', ''),
                'URL': f"https://www.assembly.go.kr/assm/comm/commListAjax.do?currentPage=1&rowPerPage=10&commCd={committee.get('commCd', '')}"
            }
            subcommittees.append(committee_info)
        
        return pd.DataFrame(subcommittees), current_time
    except Exception as e:
        st.error(f"소위원회 정보 조회 중 오류 발생: {str(e)}")
        return None, None

# 스냅샷 데이터 로드 함수
@st.cache_data
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

# 메인 함수
def main():
    # 실시간 데이터 조회
    df, member_collect_time = fetch_assembly_member_data()
    bill_df, bill_collect_time = fetch_bill_data()
    subcommittee_df, subcommittee_collect_time = fetch_subcommittee_data()
    
    # 스냅샷 데이터 로드
    snapshot_data, snapshot_date = load_snapshot()
    
    if df is not None:
        # 필터링 옵션
        st.sidebar.header("필터")
        
        # 국회의원 정보 필터
        st.sidebar.subheader("국회의원 정보 필터")
        parties = ['전체'] + sorted(df['정당'].unique().tolist())
        selected_party = st.sidebar.selectbox('정당', parties)
        
        committees = ['전체'] + sorted(df['소속위원회'].unique().tolist())
        selected_committee = st.sidebar.selectbox('소속위원회', committees)
        
        districts = ['전체'] + sorted(df['선거구'].unique().tolist())
        selected_district = st.sidebar.selectbox('선거구', districts)
        
        # 필터링 적용
        filtered_df = df.copy()
        if selected_party != '전체':
            filtered_df = filtered_df[filtered_df['정당'] == selected_party]
        if selected_committee != '전체':
            filtered_df = filtered_df[filtered_df['소속위원회'] == selected_committee]
        if selected_district != '전체':
            filtered_df = filtered_df[filtered_df['선거구'] == selected_district]
        
        # 데이터 표시
        st.markdown(f"### 🏛️ 국회의원 정보 (수집일시: {member_collect_time})")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # 국회 바로가기 링크
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <a href="https://www.assembly.go.kr/" target="_blank">국회 바로가기</a>
        </div>
        """, unsafe_allow_html=True)
    
    if bill_df is not None:
        # 법률안 필터
        st.sidebar.subheader("법률안 필터")
        bill_names = ['전체'] + sorted(bill_df['의안명'].unique().tolist())
        selected_bill = st.sidebar.selectbox('법률안', bill_names)
        
        proposer_types = ['전체'] + sorted(bill_df['제안자'].unique().tolist())
        selected_proposer = st.sidebar.selectbox('제안자', proposer_types)
        
        status_types = ['전체'] + sorted(bill_df['소관위원회'].unique().tolist())
        selected_status = st.sidebar.selectbox('소관위원회', status_types)
        
        # 필터링 적용
        filtered_bill_df = bill_df.copy()
        if selected_bill != '전체':
            filtered_bill_df = filtered_bill_df[filtered_bill_df['의안명'] == selected_bill]
        if selected_proposer != '전체':
            filtered_bill_df = filtered_bill_df[filtered_bill_df['제안자'] == selected_proposer]
        if selected_status != '전체':
            filtered_bill_df = filtered_bill_df[filtered_bill_df['소관위원회'] == selected_status]
        
        # 데이터 표시
        st.markdown(f"### 📜 법률안 발의내역 (수집일시: {bill_collect_time})")
        st.dataframe(
            filtered_bill_df,
            use_container_width=True,
            hide_index=True,
            height=200
        )
        
        # 의안정보시스템 링크
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <a href="https://likms.assembly.go.kr/bill/main.do" target="_blank">의안정보시스템 바로가기</a>
        </div>
        """, unsafe_allow_html=True)
    
    if subcommittee_df is not None:
        # 소위원회 필터
        st.sidebar.subheader("소위원회 필터")
        selected_subcommittee = st.sidebar.selectbox('소위원회', ['전체'] + sorted(subcommittee_df['소위원회명'].unique().tolist()))
        
        # 필터링 적용
        filtered_subcommittee_df = subcommittee_df.copy()
        if selected_subcommittee != '전체':
            filtered_subcommittee_df = filtered_subcommittee_df[filtered_subcommittee_df['소위원회명'] == selected_subcommittee]
        
        # 데이터 표시
        st.markdown(f"### 🪑 소위원회 정보 (수집일시: {subcommittee_collect_time})")
        st.dataframe(
            filtered_subcommittee_df,
            use_container_width=True,
            hide_index=True,
            height=200
        )
        
        # 기획재정위원회 링크
        st.markdown("""
        <div style="text-align: right; margin-top: 10px;">
            <a href="https://finance.na.go.kr/" target="_blank">기획재정위원회 바로가기</a>
        </div>
        """, unsafe_allow_html=True)
    
    # 안내 메시지
    st.markdown(f"""
    <div class="info-box">
        <h3>📌 안내사항</h3>
        <ul>
            <li>수은 업무 관련 국회의원 및 법률안 발의내역 등 정보가 나타나 있습니다.</li>
            <li>국회의원 정보 변경사항은 스냅샷 기준일({snapshot_date}) 대비 현시점 달라진 내역을 나타냅니다.(예: 소속위원회 변경, 보좌진 변경 등)</li>
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

    # 스냅샷 데이터 보기
    with st.expander("📸 스냅샷 원본 보기", expanded=False):
        if snapshot_data:
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
                    'URL': member['메타데이터']['url']
                }
                for member in snapshot_data
            ])
            st.dataframe(
                snapshot_df,
                use_container_width=True,
                hide_index=True,
                height=400
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