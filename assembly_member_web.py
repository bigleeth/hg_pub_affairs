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
    .stDataFrame {
        width: 100%;
    }
    .highlight {
        background-color: yellow;
    }
    .info-box {
        background-color: #f0f0f0;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .copyright {
        text-align: center;
        color: #666;
        font-size: 0.8em;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.title("국회의원실 정보 대시보드 (수은 대외팀)")

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
    for col in ['이름', '당선횟수', '선거구', '소속위원회', '보좌관', '선임비서관', '비서관']:
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
    
    # 소속위원회 필터
    committees = ['전체'] + sorted(df['소속위원회'].unique().tolist())
    selected_committee = st.sidebar.selectbox('소속위원회', committees)
    
    # 선거구 필터
    districts = ['전체'] + sorted(df['선거구'].unique().tolist())
    selected_district = st.sidebar.selectbox('선거구', districts)
    
    # 필터링 적용
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
    
    # 새로고침 버튼
    if st.button("데이터 새로고침"):
        # 스냅샷 저장
        if df is not None:
            with open('assembly_member_snapshot.json', 'w', encoding='utf-8') as f:
                json.dump(df.to_dict('records'), f, ensure_ascii=False, indent=4)
        
        # 데이터 수집 스크립트 실행
        os.system('python 국회의원실정보수집.py')
        
        # 페이지 새로고침
        st.experimental_rerun()

    # 저작권 정보
    st.markdown("""
    <div class="copyright">
        © 2025 Taehyun Lee. This dashboard is for non-commercial use only. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 