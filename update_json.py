# update_json.py
# -*- coding: utf-8 -*-

import json
import re
import unicodedata
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup


# =========================================================
# 공통 유틸
# =========================================================
KST = ZoneInfo("Asia/Seoul")


def now_kst_str() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")


def normalize_bill_title(title: str) -> str:
    """
    - NFKC 정규화
    - '계류의안', '처리의안' 같은 접두어 제거
    - 괄호 블록 전부 제거: (대안)(OO의원 등) 등 여러 개도 제거
    - 공백 정리
    """
    if not title:
        return ""

    t = unicodedata.normalize("NFKC", title).strip()

    # ✅ 접두어 제거 (td[1]에 붙어오는 케이스 대응)
    # 필요하면 접두어를 더 추가해도 됨.
    t = re.sub(r"^(계류의안|처리의안)\s+", "", t)

    # ✅ 괄호 전부 제거 (여러 괄호도 싹 제거)
    t = re.sub(r"\s*\([^)]*\)", "", t)

    # 공백 정리
    t = re.sub(r"\s+", " ", t).strip()
    return t

# =========================================================
# 1) 국회의원 정보 수집
# =========================================================
def collect_members():
    print("🔎 국회의원 정보 수집 시작")

    headers_members = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
    }

    # (이전 코드 그대로) - 필요하면 멤버 추가/수정
    members = [
        ("김영진", "KIMYOUNGJIN"),
        ("정태호", "JUNGTAEHO"),
        ("김영환", "KIMYOUNGWHAN"),
        ("김태년", "KIMTAENYEON"),
        ("박홍근", "PARKHONGKEUN"),
        ("박민규", "PARKMINKYU"),
        ("안규백", "AHNGYUBACK"),
        ("안도걸", "AHNDOGEOL"),
        ("오기형", "OHGIHYOUNG"),
        ("이소영", "LEESOYOUNG"),
        ("정성호", "JUNGSUNGHO"),
        ("정일영", "CHUNGILYOUNG"),
        ("조승래", "JOSEOUNGLAE"),
        ("진성준", "JINSUNGJOON"),
        ("송언석", "SONGEONSEOG"),
        ("박수영", "PARKSOOYOUNG"),
        ("박대출", "PARKDAECHUL"),
        ("박성훈", "PARKSUNGHOON"),
        ("유상범", "YOOSANGBUM"),
        ("윤영석", "YOONYOUNGSEOK"),
        ("이인선", "LEEINSEON"),
        ("임이자", "LIMLEEJA"),
        ("최은석", "CHOIEUNSEOK"),
        ("차규근", "CHAGYUGEUN"),
        ("천하람", "CHUNHARAM"),
        ("최기상", "CHOIKISANG"),
        ("권영세", "KWONYOUNGSE"),
    ]

    party_mapping = {
        "정태호": "더불어민주당",
        "김영진": "더불어민주당",
        "김영환": "더불어민주당",
        "김태년": "더불어민주당",
        "박홍근": "더불어민주당",
        "박민규": "더불어민주당",
        "안규백": "더불어민주당",
        "안도걸": "더불어민주당",
        "오기형": "더불어민주당",
        "이소영": "더불어민주당",
        "정성호": "더불어민주당",
        "정일영": "더불어민주당",
        "조승래": "더불어민주당",
        "진성준": "더불어민주당",
        "최기상": "더불어민주당",
        "송언석": "국민의힘",
        "박수영": "국민의힘",
        "박대출": "국민의힘",
        "박성훈": "국민의힘",
        "유상범": "국민의힘",
        "윤영석": "국민의힘",
        "이인선": "국민의힘",
        "임이자": "국민의힘",
        "최은석": "국민의힘",
        "권영세": "국민의힘",
        "차규근": "조국혁신당",
        "천하람": "개혁신당",
    }

    def extract_member_data(soup, fallback_name, member_id, status_code):
        name_el = soup.find("span", class_="sr-only")
        name = name_el.get_text(strip=True) if name_el else fallback_name

        party = party_mapping.get(name, "정보 없음")
        election_count, district, committee = "정보 없음", "정보 없음", "정보 없음"

        for dt in soup.find_all("dt"):
            label = dt.get_text(strip=True)
            dd = dt.find_next("dd")
            if not dd:
                continue
            val = dd.get_text(" ", strip=True)

            if label == "당선횟수":
                election_count = val[:2]
            elif label == "선거구":
                district = val
            elif label == "소속위원회":
                committee = val

        chief, senior, secretary = [], [], []
        for li in soup.find_all("li"):
            title = li.find("dt")
            value = li.find("dd")
            if not title or not value:
                continue
            role = title.get_text(strip=True)
            names = [n.strip() for n in value.get_text(strip=True).split(",") if n.strip()]
            if "보좌관" in role:
                chief = names
            elif "선임비서관" in role:
                senior = names
            elif "비서관" in role:
                secretary = names

        return {
            "국회의원": {
                "이름": name,
                "정당": party,
                "당선횟수": election_count,
                "선거구": district,
                "소속위원회": committee,
            },
            "보좌관": chief,
            "선임비서관": senior,
            "비서관": secretary,
            "메타데이터": {
                "url": f"https://www.assembly.go.kr/members/22nd/{member_id}",
                "status_code": status_code,
                "수집일시": now_kst_str(),
            },
        }

    session = requests.Session()
    session.headers.update(headers_members)

    all_member_data = []
    for name, member_id in members:
        url = f"https://www.assembly.go.kr/members/22nd/{member_id}"
        try:
            resp = session.get(url, timeout=30)
            soup = BeautifulSoup(resp.text, "html.parser")
            all_member_data.append(extract_member_data(soup, name, member_id, resp.status_code))
        except Exception as e:
            print(f"⚠️ [국회의원] {name} 실패: {e}")
            all_member_data.append({
                "국회의원": {"이름": name, "정당": party_mapping.get(name, "정보 없음"),
                          "당선횟수": "정보 없음", "선거구": "정보 없음", "소속위원회": "정보 없음"},
                "보좌관": [], "선임비서관": [], "비서관": [],
                "메타데이터": {"url": url, "status_code": 0, "수집일시": now_kst_str()},
            })

    with open("assembly_member_data.json", "w", encoding="utf-8") as f:
        json.dump(all_member_data, f, ensure_ascii=False, indent=2)

    print("✅ 국회의원 정보 저장 완료")


# =========================================================
# 2) 의안정보(LIKMS) 수집 - CSRF 자동 + 정확 제목 매칭
# =========================================================
LIKMS_REFERER = "https://likms.assembly.go.kr/bill/bi/bill/sch/detailedSchPage.do"
LIKMS_FIND_URL = "https://likms.assembly.go.kr/bill/bi/bill/sch/findSchPaging.do"


def likms_prepare_session() -> requests.Session:
    """
    1) detailedSchPage.do GET 해서 쿠키/JSESSIONID/CSRF meta 확보
    2) 이후 findSchPaging.do POST에서 같은 세션 사용
    """
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": LIKMS_REFERER,
        "Origin": "https://likms.assembly.go.kr",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })

    # CSRF 메타가 있을 수 있어서 먼저 referer 페이지를 GET
    r = s.get(LIKMS_REFERER, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # 일반적으로 _csrf / _csrf_header 메타가 존재
    csrf = soup.find("meta", {"name": "_csrf"})
    csrf_header = soup.find("meta", {"name": "_csrf_header"})

    if csrf and csrf.get("content"):
        token = csrf["content"].strip()
        header_name = csrf_header["content"].strip() if (csrf_header and csrf_header.get("content")) else "X-CSRF-TOKEN"
        s.headers[header_name] = token

    # findSchPaging.do는 form-urlencoded
    s.headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    s.headers["Accept"] = "text/html, */*; q=0.8"

    return s


def likms_fetch_by_billname(session: requests.Session, bill_name: str) -> str:
    """
    bill_name로 검색 POST → HTML(테이블 포함) 반환
    """
    data = {
        "reqPageId": "billSrch",
        "srchCmtId": "",
        "detailedTab": "billDtl",
        "gnStatsDiv": "",
        "srchBillDtlKindCd": "",
        "srchBillKindCd": "",
        "isGnStats": "",
        "dtlResultCd": "",
        "useNotIn": "",
        "mainQuery": "",
        "mainTabType": "",
        "fromMainBillStat": "",
        "billNm": bill_name,      # ★ 전체 제목 그대로 넣고 아래에서 정확 매칭
        "nmReSchText": "",
        "billNo": "",
        "representKindCd": "전체",
        "represent": "",
        "representId": "",
        "isPopSelect": "N",
        "ageCmtId": "전체",
        "ageFrom": "22",
        "ageTo": "22",
        "billKind": "전체",
        "proposerKind": "전체",
        "procGbnCd": "전체",
        "jntPrpslYn": "전체",
        "cmtResultCd": "전체",
        "mainResultCd": "전체",
        "mainUpdateYn": "전체",
        "lawStatus": "전체",
        "page": "1",
        "rows": "50",
        "schSorting": "score",
        "ordCd": "DESC",
    }

    r = session.post(LIKMS_FIND_URL, data=data, timeout=30)
    r.raise_for_status()
    return r.text


def likms_parse_and_filter(html: str, target_bill_name: str):
    """
    - 테이블의 tbody tr을 파싱
    - 의안명(td[1])에서만 title을 뽑아서 normalize 후 target과 동일한 것만 저장
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table")
    if not table:
        return [], []

    target_norm = normalize_bill_title(target_bill_name)

    all_titles_preview = []
    matched = []

    rows = table.select("tbody tr")
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        title_td = tds[1]
        raw_title = title_td.get_text(" ", strip=True)
        all_titles_preview.append(raw_title)

        norm_title = normalize_bill_title(raw_title)
        if norm_title != target_norm:
            continue

        bill_no = tds[0].get_text(strip=True)

        # billId 추출 (onclick: fGoDetail('2212345', ...)
        bill_id = ""
        a = title_td.find("a")
        if a and a.has_attr("onclick"):
            m = re.search(r"fGoDetail\('([^']+)'", a["onclick"])
            if m:
                bill_id = m.group(1)

        proposer_kind = tds[2].get_text(strip=True) if len(tds) > 2 else ""
        propose_date = tds[3].get_text(strip=True) if len(tds) > 3 else ""
        vote_date = tds[4].get_text(strip=True) if len(tds) > 4 else ""
        vote_result = tds[5].get_text(strip=True) if len(tds) > 5 else ""
        status = tds[7].get_text(strip=True) if len(tds) > 7 else ""

        matched.append({
            "의안번호": bill_no,
            "의안ID": bill_id,
            "의안명": raw_title,  # 원문 유지 (괄호 포함)
            "제안자구분": proposer_kind,
            "제안일자": propose_date,
            "의결일자": vote_date,
            "의결결과": vote_result,
            "심사진행상태": status,
            "상세URL": f"https://likms.assembly.go.kr/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else "",
            "수집일시": now_kst_str(),
        })

    return matched, all_titles_preview


def collect_bills():
    print("🔎 의안 정보 수집 시작")

    bill_names = [
        "한국수출입은행법 일부개정법률안",
        "경제안보를 위한 공급망 안정화 지원 기본법 일부개정법률안",
        "첨단조선업의 경쟁력 강화 및 지원에 관한 특별법안",
        "공공기관의 운영에 관한 법률 일부개정법률안",
        "한국산업은행법 일부개정법률안",
        "2025년도에 발행하는 첨단전략산업기금채권에 대한 국가보증동의안",
        "중소기업은행법 일부개정법률안",
        "정부조직법 일부개정법률안",
        "신용보증기금법 일부개정법률안",
        "동남권산업투자공사 설립 및 운영에 관한 법률안",
        "충청권산업투자공사 설립 및 운영에 관한 법률안",
        "기후위기 대응을 위한 탄소중립ㆍ녹색성장 기본법 일부개정법률안",
    ]

    session = likms_prepare_session()

    all_bills = []
    for name in bill_names:
        try:
            html = likms_fetch_by_billname(session, name)
            matched, preview = likms_parse_and_filter(html, name)

            if not preview:
                print(f"ℹ️ [{name}] 검색 결과(행)가 없습니다. (HTTP 200, 테이블은 있으나 tbody 비었거나 구조변경)")
            elif not matched:
                # 검색은 되는데 정확매칭 0건이면 예시 출력
                ex = preview[:5]
                print(f"ℹ️ [{name}] 검색은 됐지만 정확제목 매칭 0건. 예시: {ex}")
            else:
                print(f"✅ [{name}] {len(matched)}건 저장")

            all_bills.extend(matched)

        except Exception as e:
            print(f"⚠️ [의안] {name} 수집 실패: {type(e).__name__} - {e}")

    with open("의안정보검색결과.json", "w", encoding="utf-8") as f:
        json.dump(all_bills, f, ensure_ascii=False, indent=2)

    print(f"✅ 의안 정보 저장 완료: {len(all_bills)}건")


# =========================================================
# 3) 소위원회 정보 수집
# =========================================================
def collect_subcommittees():
    print("🔎 소위원회 정보 수집 시작")

    session = requests.Session()
    main_url = "https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/subCmt.do?menuNo=2000014"

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    main_resp = session.get(main_url, headers=headers, timeout=30)
    main_resp.raise_for_status()

    soup = BeautifulSoup(main_resp.text, "html.parser")
    csrf_parameter = soup.find("meta", {"name": "_csrf_parameter"})
    csrf_header = soup.find("meta", {"name": "_csrf_header"})
    csrf_token = soup.find("meta", {"name": "_csrf"})

    if not all([csrf_parameter, csrf_header, csrf_token]):
        raise RuntimeError("CSRF 메타 태그를 찾을 수 없습니다. (finance.na.go.kr 구조 변경 가능)")

    csrf_parameter_value = csrf_parameter["content"]
    csrf_header_value = csrf_header["content"]
    csrf_token_value = csrf_token["content"]

    api_headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://finance.na.go.kr:444",
        "Referer": main_url,
        "User-Agent": headers["User-Agent"],
        "X-Requested-With": "XMLHttpRequest",
        csrf_header_value: csrf_token_value,
    }

    data = {
        "hgNm": "",
        "subCmtNm": "",
        "pageUnit": "9",
        "pageIndex": "",
        csrf_parameter_value: csrf_token_value,
    }

    resp = session.post(
        "https://finance.na.go.kr:444/cmmit/mem/cmmitMemList/getSubCmitLst.json",
        headers=api_headers,
        data=data,
        timeout=30,
    )
    resp.raise_for_status()
    response_data = resp.json()

    def parse_members(member_str):
        members = []
        for m in member_str.split(","):
            m = m.strip()
            if m.startswith("◈"):
                m = m.lstrip("◈")
                if "(長)" not in m:
                    name_part, sep, han_part = m.partition("(")
                    m = f"(長){name_part}{sep}{han_part}"
            members.append(m)
        return members

    result = {}
    for item in response_data.get("resultList", []):
        committee_name = item.get("sbcmtNm", "")
        count = item.get("naasCnt", "")
        key = f"{committee_name}({count}인)"

        parties = {}
        if item.get("poly1NaasNm") and item.get("poly1NaasCn"):
            parties[item["poly1NaasNm"]] = parse_members(item["poly1NaasCn"])
        if item.get("poly2NaasNm") and item.get("poly2NaasCn"):
            parties[item["poly2NaasNm"]] = parse_members(item["poly2NaasCn"])
        if item.get("poly99NaasNm") and item.get("poly99NaasCn"):
            parties[item["poly99NaasNm"]] = parse_members(item["poly99NaasCn"])

        result[key] = parties

    final_result = {
        "소위원회_정보": result,
        "메타데이터": {
            "수집일시": now_kst_str(),
            "url": main_url,
            "status_code": resp.status_code,
        },
    }

    with open("소위원회정보.json", "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print("✅ 소위원회 정보 저장 완료")


# =========================================================
# main
# =========================================================
def main():
    collect_members()
    collect_bills()
    collect_subcommittees()


if __name__ == "__main__":
    main()

