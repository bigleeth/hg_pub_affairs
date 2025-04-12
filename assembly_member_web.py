import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import requests

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
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {str(e)}")
        return None

# 스냅샷 데이터 로드 함수
@st.cache_data
def load_snapshot():
    try:
        # GitHub에서 스냅샷 데이터 가져오기
        response = requests.get('https://raw.githubusercontent.com/your-username/your-repo/main/assembly_member_snapshot.json')
        if response.status_code == 200:
            snapshot_data = response.json()
            # GitHub API를 통해 파일의 마지막 수정 시간 가져오기
            github_api_url = 'https://api.github.com/repos/your-username/your-repo/contents/assembly_member_snapshot.json'
            github_response = requests.get(github_api_url)
            if github_response.status_code == 200:
                github_data = github_response.json()
                snapshot_time = datetime.strptime(github_data['last_modified'], '%a, %d %b %Y %H:%M:%S %Z').strftime("%Y년 %m월 %d일")
            else:
                snapshot_time = "알 수 없음"
            return snapshot_data, snapshot_time
        else:
            st.warning("GitHub에서 스냅샷 파일을 가져오지 못했습니다.")
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

# 메인 함수
def main():
    # 데이터 로드
    df = load_data()
    if df is None:
        return

    # 스냅샷 데이터 로드
    snapshot_data, snapshot_time = load_snapshot()
    
    # 사이드바에 스냅샷 정보 표시
    with st.sidebar:
        st.markdown("### 📸 스냅샷 정보")
        if snapshot_time:
            st.markdown(f"**스냅샷 생성일:** {snapshot_time}")
        else:
            st.warning("스냅샷이 존재하지 않습니다.")

    # 데이터프레임 표시
    if snapshot_data:
        df = highlight_changes(df, snapshot_data)
        st.markdown("### 📊 국회의원 정보 (변경된 항목이 노란색으로 표시됩니다)")
    else:
        st.markdown("### 📊 국회의원 정보")
    
    # 데이터프레임 높이 설정
    st.dataframe(df, height=500)
    
    # 스냅샷 데이터 보기
    with st.expander("📸 스냅샷 원본 보기 (assembly_member_snapshot.json)", expanded=False):
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
                height=400,
                column_config={
                    "URL": st.column_config.LinkColumn("URL")
                }
            )
        else:
            st.warning("스냅샷 데이터가 없습니다.")
    
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

    # 저작권 정보
    st.markdown("""
    <div class="copyright">
        © 2025 Taehyun Lee. This dashboard is for non-commercial use only. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()