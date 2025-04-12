import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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
    <h1 style="margin-bottom: 1rem;">🚀국회 모니터링(수은 대외팀)🚀</h1>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 데이터프레임으로 변환
        df = pd.DataFrame([
            {
                '이름': member['국회의원']['이름'],
                '정당': member['국회의원'].get('정당', '정보 없음'),
                '당선횟수': member['국회의원']['당선횟수'][:2],  # 처음 두 글자만 표시
                '선거구': member['국회의원']['선거구'],
                '소속위원회': member['국회의원']['소속위원회'],
                '보좌관': ','.join(member['보좌관']),  # 쉼표 뒤에 공백 없이 조인
                '선임비서관': ','.join(member['선임비서관']),
                '비서관': ','.join(member['비서관']),
                'URL': member['메타데이터']['url'],
                '수집일시': member['메타데이터']['수집일시']
            }
            for member in data
        ])
        
        # 스냅샷 파일이 없으면 현재 데이터를 스냅샷으로 저장
        if not os.path.exists('assembly_member_snapshot.json'):
            with open('assembly_member_snapshot.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            st.info("현재 데이터가 스냅샷으로 저장되었습니다. 이후 변경사항은 이 시점을 기준으로 비교됩니다.")
        
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
                # 스냅샷 파일의 생성 시간 가져오기
                snapshot_time = datetime.fromtimestamp(os.path.getmtime('assembly_member_snapshot.json')).strftime("%Y년 %m월 %d일")
                return snapshot_data, snapshot_time
        else:
            st.warning("스냅샷 파일이 존재하지 않습니다.")
            return None, None
    except Exception as e:
        st.error(f"스냅샷 로드 중 오류 발생: {str(e)}")
        return None, None

# 스냅샷 리셋 함수
def reset_snapshot():
    try:
        with open('assembly_member_data.json', 'r', encoding='utf-8') as f:
            current_data = json.load(f)
        with open('assembly_member_snapshot.json', 'w', encoding='utf-8') as f:
            json.dump(current_data, f, ensure_ascii=False, indent=4)
        st.success("스냅샷이 성공적으로 업데이트되었습니다.")
    except Exception as e:
        st.error(f"스냅샷 업데이트 중 오류 발생: {str(e)}")

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
            '보좌관': member['보좌관'],
            '선임비서관': member['선임비서관'],
            '비서관': member['비서관'],
            'URL': member['메타데이터']['url']
        }
        for member in snapshot_data
    ])
    
    # 변경사항을 저장할 새로운 열 추가
    df['변경사항'] = ''
    
    # 변경된 셀 체크
    for idx, row in df.iterrows():
        if row['URL'] in snapshot_df['URL'].values:
            snapshot_row = snapshot_df[snapshot_df['URL'] == row['URL']].iloc[0]
            
            # 각 열 비교
            for col in ['이름', '당선횟수', '선거구', '소속위원회', '보좌관', '선임비서관', '비서관']:
                current_value = str(row[col])
                snapshot_value = snapshot_row[col]

                if col == '당선횟수':
                    # 당선횟수는 처음 두 글자만 비교
                    if current_value[:2] != snapshot_value[:2]:
                        df.at[idx, '변경사항'] += f'{col} 변경, '
                elif col in ['보좌관', '선임비서관', '비서관']:
                    # 현재 값과 스냅샷 값을 쉼표로 구분된 문자열로 변환하고 공백 제거
                    current_str = str(current_value).replace(" ", "")
                    snapshot_str = ','.join(snapshot_value).replace(" ", "")
                    
                    if current_str != snapshot_str:
                        df.at[idx, '변경사항'] += f'{col} 변경, '
                else:
                    # 다른 열들은 문자열로 비교
                    if current_value != snapshot_value:
                        df.at[idx, '변경사항'] += f'{col} 변경, '
    
    # 변경사항 열의 마지막 쉼표 제거
    df['변경사항'] = df['변경사항'].str.rstrip(', ')
    
    return df

# 메인 함수
def main():
    # 데이터 로드
    df = load_data()
    if df is None:
        return
        
    # 스냅샷 로드
    snapshot_data, snapshot_time = load_snapshot()
    
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
    filtered_df = df.copy()  # 원본 데이터프레임 복사
    if selected_party != '전체':
        filtered_df = filtered_df[filtered_df['정당'] == selected_party]
    if selected_committee != '전체':
        filtered_df = filtered_df[filtered_df['소속위원회'] == selected_committee]
    if selected_district != '전체':
        filtered_df = filtered_df[filtered_df['선거구'] == selected_district]
    
    # 데이터 표시
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
    
    # 안내 메시지
    st.markdown(f"""
    <div class="info-box">
        <h3>📌 안내사항</h3>
        <ul>
            <li>기재위 소속 및 기타 수은 업무 관련 의원실 정보가 나타나 있습니다.</li>
            <li>변경사항은 스냅샷 기준일({snapshot_time}) 대비 달라진 내역을 나타냅니다.(예: 소속위원회 변경, 보좌진 변경 등)</li>
            <li>데이터는 매일 자동으로 업데이트됩니다.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # 스냅샷 관리 버튼 (작고 눈에 잘 띄지 않게)
    st.markdown("""
    <style>
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
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
    with col2:
        password = st.text_input("", type="password", key="snapshot_password", label_visibility="collapsed")
        if st.button("스냅샷 리셋", key="snapshot_reset"):
            if password == "0204":
                reset_snapshot()
                st.rerun()
            else:
                st.error("잘못된 비밀번호입니다.")

    # 저작권 정보
    st.markdown("""
    <div class="copyright">
        © 2025 Taehyun Lee. This dashboard is for non-commercial use only. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()