import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="국회의원 정보",
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
    </style>
""", unsafe_allow_html=True)

# 제목
st.markdown("""
    <h1 style="margin-bottom: 1rem;">국회의원실 정보 대시보드 (수은 대외팀)</h1>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
            
        # 데이터프레임으로 변환
        df = pd.DataFrame([
            {
                '이름': member['국회의원']['이름'],
                '정당': member['국회의원'].get('정당', '정보 없음'),  # 정당 정보가 없는 경우 '정보 없음'으로 설정
                '당선횟수': member['국회의원']['당선횟수'],
                '선거구': member['국회의원']['선거구'],
                '소속위원회': member['국회의원']['소속위원회'],
                '보좌관': ', '.join(member['보좌관']),
                '선임비서관': ', '.join(member['선임비서관']),
                '비서관': ', '.join(member['비서관']),
                'URL': member['메타데이터']['url'],
                '수집일시': member['메타데이터']['수집일시']
            }
            for member in current_data
        ])
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")
        return None

# 스냅샷 데이터 로드 함수
@st.cache_data
def load_snapshot():
    try:
        if os.path.exists('assembly_member_snapshot.json'):
            with open('assembly_member_snapshot.json', 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            return snapshot_data
        return None
    except Exception as e:
        st.error(f"스냅샷 로드 중 오류 발생: {str(e)}")
        return None

# 데이터 비교 및 하이라이트 함수
def highlight_changes(df, snapshot_data):
    if snapshot_data is None:
        return df
        
    # 스냅샷 데이터프레임 생성
    snapshot_df = pd.DataFrame([
        {
            '이름': member['국회의원']['이름'],
            '정당': member['국회의원'].get('정당', '정보 없음'),
            '당선횟수': member['국회의원']['당선횟수'],
            '선거구': member['국회의원']['선거구'],
            '소속위원회': member['국회의원']['소속위원회'],
            '보좌관': ', '.join(member['보좌관']),
            '선임비서관': ', '.join(member['선임비서관']),
            '비서관': ', '.join(member['비서관']),
            'URL': member['메타데이터']['url']
        }
        for member in snapshot_data
    ])
    
    # 변경된 셀 하이라이트
    def highlight_cell(val, snapshot_val):
        if val != snapshot_val:
            return 'background-color: yellow'
        return ''
    
    # 각 열에 대해 변경사항 확인
    for col in ['이름', '정당', '당선횟수', '선거구', '소속위원회', '보좌관', '선임비서관', '비서관']:
        df[col] = df.apply(
            lambda row: f'<span class="highlight">{row[col]}</span>' 
            if row['URL'] in snapshot_df['URL'].values 
            and snapshot_df[snapshot_df['URL'] == row['URL']][col].iloc[0] != row[col]
            else row[col],
            axis=1
        )
    
    return df

# 메인 함수
def main():
    # 데이터 로드
    df = load_data()
    if df is None:
        return
        
    # 스냅샷 로드
    snapshot_data = load_snapshot()
    
    # 데이터 비교 및 하이라이트
    df = highlight_changes(df, snapshot_data)
    
    # 필터링 옵션
    st.sidebar.header("필터")
    
    # 정당 필터
    parties = ['전체'] + sorted(df['정당'].unique().tolist())
    selected_party = st.sidebar.selectbox('정당', parties)
    
    # 소속위원회 필터
    committees = ['전체'] + sorted(df['소속위원회'].unique().tolist())
    selected_committee = st.sidebar.selectbox('소속위원회', committees)
    
    # 선거구 필터
    districts = ['전체'] + sorted(df['선거구'].unique().tolist())
    selected_district = st.sidebar.selectbox('선거구', districts)
    
    # 필터링 적용
    if selected_party != '전체':
        df = df[df['정당'] == selected_party]
    if selected_committee != '전체':
        df = df[df['소속위원회'] == selected_committee]
    if selected_district != '전체':
        df = df[df['선거구'] == selected_district]
    
    # 데이터 표시
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn("URL"),
            "수집일시": st.column_config.DatetimeColumn("수집일시")
        }
    )
    
    # 안내 메시지
    st.markdown("""
    <div class="info-box">
        <h3>📌 안내사항</h3>
        <ul>
            <li>노란색으로 표시된 셀은 2025년 4월 기준 대비 변동된 정보입니다.</li>
            <li>변동사항: 소속위원회 변경, 보좌진 변경 등</li>
            <li>데이터는 매일 자동으로 업데이트됩니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 저작권 정보
    st.markdown("""
    <div class="copyright">
        © 2025 Taehyun Lee. This dashboard is for non-commercial use only. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 