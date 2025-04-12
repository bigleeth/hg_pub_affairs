# 국회의원 정보 대시보드

국회의원의 정보를 실시간으로 수집하고 표시하는 웹 대시보드입니다.

## 기능

- 국회의원 기본 정보 표시 (이름, 당선횟수, 선거구, 소속위원회)
- 보좌진 정보 표시 (보좌관, 선임비서관, 비서관)
- 데이터 변경 감지 및 하이라이트
- 소속위원회 및 선거구별 필터링
- 실시간 데이터 새로고침

## 설치 및 실행

1. 저장소 클론
```bash
git clone https://github.com/your-username/assembly-member-dashboard.git
cd assembly-member-dashboard
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 데이터 수집 스크립트 실행
```bash
python 국회의원실정보수집.py
```

5. 웹 대시보드 실행
```bash
streamlit run assembly_member_web.py
```

## GitHub Pages 배포

1. Streamlit Cloud에 배포:
   - [Streamlit Cloud](https://streamlit.io/cloud)에 가입
   - GitHub 저장소 연결
   - `assembly_member_web.py`를 메인 파일로 선택
   - 배포 설정에서 환경 변수 설정

2. GitHub Actions를 사용한 자동 배포:
   - `.github/workflows/deploy.yml` 파일 생성
   - GitHub Actions 설정에서 워크플로우 활성화

## 사용 방법

1. 웹 브라우저에서 대시보드 접속
2. 사이드바에서 소속위원회 또는 선거구 필터 선택
3. "데이터 새로고침" 버튼으로 최신 정보 업데이트
4. 변경된 정보는 노란색으로 하이라이트 표시

## 라이선스

MIT License 