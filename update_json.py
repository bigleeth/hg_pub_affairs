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
    - '계류의안', '처리의안' 접두어 제거
    - 괄호 블록 전부 제거: (대안)(OO의원 등) 등 여러 개도 제거
    - 공백 정리
    """
    if not title:
        return ""

    t = unicodedata.normalize("NFKC", title).strip()
    t = re.sub(r"^(계류의안|처리의안)\s+", "", t)
    t = re.sub(r"\s*\([^)]*\)", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def safe_text(el) -> str:
    return el.get_text(" ", strip=True) if el else ""


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
                "국회의원": {
                    "이름": name,
                    "정당": party_mapping.get(name, "정보 없음"),
                    "당선횟수": "정보 없음",
                    "선거구": "정보 없음",
                    "소속위원회": "정보 없음"
                },
                "보좌관": [], "선임비서관": [], "비서관": [],
                "메타데이터": {"url": url, "status_code": 0, "수집일시": now_kst_str()},
            })

    with open("assembly_member_data.json", "w", encoding="utf-8") as f:
        json.dump(all_member_data, f, ensure_ascii=False, indent=2)

    print("✅ 국회의원 정보 저장 완료")


# =========================================================
# 2) 의안정보(LIKMS) 수집 - CSRF 자동 + "검색결과 전부 저장"
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

    r = s.get(LIKMS_REFERER, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    csrf = soup.find("meta", {"name": "_csrf"})
    csrf_header = soup.find("meta", {"name": "_csrf_header"})

    if csrf and csrf.get("content"):
        token = csrf["content"].strip()
        header_name = csrf_header["content"].strip() if (csrf_header and csrf_header.get("content")) else "X-CSRF-TOKEN"
        s.headers[header_name] = token

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
        "billNm": bill_name,
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


def likms_parse_all(html: str, keyword: str):
    """
    ✅ 필터링 없이 테이블 tbody tr을 전부 파싱하여 저장한다.
    - 다만, exact_match 여부는 기록해둔다(나중에 UI에서 필터 가능)
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.select_one("table")
    if not table:
        return [], []

    target_norm = normalize_bill_title(keyword)

    preview_titles = []
    results = []

    rows = table.select("tbody tr")
    for tr in rows:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue

        # 의안번호
        bill_no = safe_text(tds[0])

        # 의안명 + billId
        title_td = tds[1]
        raw_title = title_td.get_text(" ", strip=True)
        preview_titles.append(raw_title)

        norm_title = normalize_bill_title(raw_title)
        exact_match = (norm_title == target_norm)

        bill_id = ""
        a = title_td.find("a")
        if a and a.has_attr("onclick"):
            m = re.search(r"fGoDetail\('([^']+)'", a["onclick"])
            if m:
                bill_id = m.group(1)

        proposer_kind = safe_text(tds[2]) if len(tds) > 2 else ""
        propose_date = safe_text(tds[3]) if len(tds) > 3 else ""
        vote_date = safe_text(tds[4]) if len(tds) > 4 else ""
        vote_result = safe_text(tds[5]) if len(tds) > 5 else ""
        reason_text = safe_text(tds[6]) if len(tds) > 6 else ""
        status = safe_text(tds[7]) if len(tds) > 7 else ""

        results.append({
            "검색어": keyword,
            "정규화검색어": target_norm,
            "정확제목매칭여부": exact_match,

            "의안번호": bill_no,
            "의안ID": bill_id,
            "의안명": raw_title,
            "정규화의안명": norm_title,

            "제안자구분": proposer_kind,
            "제안일자": propose_date,
            "의결일자": vote_date,
            "의결결과": vote_result,
            "제안이유": reason_text,
            "심사진행상태": status,

            "상세URL": f"https://likms.assembly.go.kr/bill/bi/bill/detail.do?billId={bill_id}" if bill_id else "",
            "수집일시": now_kst_str(),
        })

    return results, preview_titles


def dedupe_bills(items: list) -> list:
    """
    의안ID가 있으면 의안ID 기준으로 중복 제거.
    의안ID가 없으면 (의안번호 + 의안명)으로 보조키.
    """
    seen = set()
    out = []
    for x in items:
        bill_id = (x.get("의안ID") or "").strip()
        if bill_id:
            key = f"ID:{bill_id}"
        else:
            key = f"NO:{(x.get('의안번호') or '').strip()}|TITLE:{(x.get('의안명') or '').strip()}"

        if key in seen:
            continue
        seen.add(key)
        out.append(x)
    return out


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
        "전략수출금융지원에 관한 법률안",
        "한미 조선산업 협력 및 지원 특별법안",
        "한미 전략적 투자 관리를 위한 특별법안",
    ]

    session = likms_prepare_session()

    all_bills = []
    for name in bill_names:
        try:
            html = likms_fetch_by_billname(session, name)
            rows, preview = likms_parse_all(html, name)

            if not preview:
                print(f"ℹ️ [{name}] 검색 결과(행)가 없습니다. (HTTP 200, table/tbody 구조 확인 필요)")
            else:
                # 매칭 여부 통계만 로그로
                match_cnt = sum(1 for r in rows if r.get("정확제목매칭여부") is True)
                print(f"✅ [{name}] {len(rows)}건 저장 (정확매칭 {match_cnt}건)")

            all_bills.extend(rows)

        except Exception as e:
            print(f"⚠️ [의안] {name} 수집 실패: {type(e).__name__} - {e}")

    # ✅ 중복 제거
    all_bills = dedupe_bills(all_bills)

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

