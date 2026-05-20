"""공공데이터 API -> data/raw/ CSV 저장.

API 1: 국립중앙의료원 응급의료기관 정보 조회
  endpoint: /B552657/ErmctInfoInqireService/getEgytListInfoInqire
  전국 534개 응급의료기관 (위치 좌표 포함)

API 2: 소방청 구급통계서비스
  endpoint: /1661000/EmergencyStatisticsService/getTrafficAccidentEmgActStats
  시도본부별·접수년월별 구급 출동 통계 (시도 루프)
"""
from __future__ import annotations

import os
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator

import pandas as pd
import requests
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_RAW  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
API_KEY = os.environ["DATA_GO_KR_API_KEY"]

# ── 공통 설정 ─────────────────────────────────────────────────
TIMEOUT = 60
PAGE_SLEEP = 0.3  # 페이지 사이 대기 (rate limit)

# 소방청 시도본부 전체 목록 (API에서 사용하는 공식 명칭)
SIDO_HQ_LIST = [
    "서울소방재난본부",
    "부산소방본부",
    "대구소방안전본부",
    "인천소방본부",
    "광주소방본부",
    "대전소방본부",
    "울산소방본부",
    "세종소방본부",
    "경기도소방재난본부",
    "강원소방본부",
    "충북소방본부",
    "충남소방본부",
    "전북소방본부",
    "전남소방본부",
    "경북소방본부",
    "경남소방본부",
    "제주소방본부",
]


# ── 유틸 ──────────────────────────────────────────────────────

def _xml_to_records(xml_bytes: bytes) -> tuple[list[dict], int]:
    """XML 바이트를 파싱해 (records_list, totalCount) 반환."""
    root = ET.fromstring(xml_bytes)
    total_text = root.findtext(".//totalCount") or "0"
    total = int(total_text)
    records = []
    for item in root.findall(".//item"):
        row = {child.tag: child.text for child in item}
        records.append(row)
    return records, total


def _paginate_xml(url: str, base_params: dict, num_per_page: int = 1000) -> Iterator[dict]:
    """XML API 전체 페이지 순회 제너레이터."""
    page = 1
    fetched = 0
    total = None

    while True:
        params = {**base_params, "pageNo": str(page), "numOfRows": str(num_per_page)}
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()

        records, page_total = _xml_to_records(resp.content)
        if total is None:
            total = page_total
            if total == 0:
                return  # 데이터 없음

        for rec in records:
            yield rec
            fetched += 1

        if fetched >= total or not records:
            break

        page += 1
        time.sleep(PAGE_SLEEP)


# ── API 1: 응급의료기관 ────────────────────────────────────────

def fetch_emergency_facilities() -> pd.DataFrame:
    """응급의료기관 전체 목록 (전국, 좌표 포함)."""
    url = (
        "https://apis.data.go.kr/B552657/ErmctInfoInqireService"
        "/getEgytListInfoInqire"
    )
    base_params = {
        "serviceKey": API_KEY,
    }

    records = list(_paginate_xml(url, base_params, num_per_page=1000))
    if not records:
        raise RuntimeError("응급의료기관 API: 데이터 0건. API 키 또는 엔드포인트 확인 필요.")

    df = pd.DataFrame(records)
    return df


# ── API 2: 소방청 구급통계 ────────────────────────────────────

def _fetch_ems_stats_for_sido(sido_hq: str, year: str) -> list[dict]:
    """단일 시도본부의 구급통계를 전체 페이지 수집."""
    url = (
        "https://apis.data.go.kr/1661000/EmergencyStatisticsService"
        "/getTrafficAccidentEmgActStats"
    )
    base_params = {
        "serviceKey": API_KEY,
        "resultType": "xml",
        "sidoHqOgidNm": sido_hq,
    }
    # 특정 연도만 받으려면 rcptYm을 202301~202312 식으로 반복해야 함.
    # 파라미터 생략 시 전체 기간 데이터 제공.

    records = []
    try:
        for rec in _paginate_xml(url, base_params, num_per_page=1000):
            records.append(rec)
    except requests.exceptions.ReadTimeout:
        print(f"    [WARN] {sido_hq}: 타임아웃 — 부분 데이터({len(records)}건) 사용")
    except Exception as exc:
        print(f"    [WARN] {sido_hq}: {exc}")
    return records


def fetch_ems_statistics(year: str = "2023") -> pd.DataFrame:
    """119 구급통계 시도별 전체 수집.

    API 특성상 시도본부별로 쿼리해야 하므로 루프 실행.
    year 파라미터는 없는 API이므로 전체 기간 수집 후 연도 필터링.
    """
    all_records: list[dict] = []

    for sido in SIDO_HQ_LIST:
        print(f"    {sido} 수집 중...", end=" ", flush=True)
        recs = _fetch_ems_stats_for_sido(sido, year)
        print(f"{len(recs)}건")
        all_records.extend(recs)
        time.sleep(PAGE_SLEEP)

    if not all_records:
        raise RuntimeError(
            "소방청 구급통계 API: 전 시도 0건. 시도본부 명칭 또는 키 확인 필요."
        )

    df = pd.DataFrame(all_records)

    # rcptYm 컬럼이 있으면 연도 필터 적용
    if "rcptYm" in df.columns:
        df["rcptYm"] = df["rcptYm"].astype(str)
        df_year = df[df["rcptYm"].str.startswith(year)]
        if len(df_year) > 0:
            df = df_year
        else:
            print(f"  [WARN] {year}년 데이터 없음 — 전체 기간 유지 ({len(df)}건)")

    return df


# ── main ──────────────────────────────────────────────────────

def main() -> None:
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    # ── 응급의료기관 ─────────────────────────
    print("Fetching 응급의료기관...")
    df_em = fetch_emergency_facilities()
    em_path = DATA_RAW / "응급의료기관.csv"
    df_em.to_csv(em_path, index=False, encoding="utf-8-sig")
    print(f"  saved: {em_path} ({len(df_em)} rows, {len(df_em.columns)} cols)")
    print(f"  columns: {list(df_em.columns)}")
    print()

    # ── 소방청 구급통계 ──────────────────────
    print("Fetching 119 구급통계...")
    df_119 = fetch_ems_statistics(year="2023")
    p119 = DATA_RAW / "119_구급통계.csv"
    df_119.to_csv(p119, index=False, encoding="utf-8-sig")
    print(f"  saved: {p119} ({len(df_119)} rows, {len(df_119.columns)} cols)")
    print(f"  columns: {list(df_119.columns)}")


if __name__ == "__main__":
    main()
