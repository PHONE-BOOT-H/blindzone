"""raw 데이터 → 시군구 단위 피처 테이블."""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.config import CRS_KOREA


def normalize_sgg_code(code: object) -> str:
    """시군구코드를 5자리 zero-padded 문자열로 통일.

    입력 형태에 무관하게 5자리 문자열을 반환한다.
    - 11010  (int)   → "11010"
    - "11010"        → "11010"
    - "11010.0"      → "11010"  (float 형태 문자열 처리)
    - 1101   (int)   → "01101"  (4자리는 left-pad)
    - NaN            → ""
    """
    try:
        if pd.isna(code):
            return ""
    except (TypeError, ValueError):
        pass
    s = str(code).split(".")[0].strip()
    return s.zfill(5)


def to_korean_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """좌표계를 EPSG:5179 (한국 측지계)로 변환.

    CRS가 설정되어 있지 않으면 WGS84(EPSG:4326)로 가정한 뒤 변환한다.
    """
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf.to_crs(CRS_KOREA)


def parse_sido_sgg(text: str) -> tuple[str, str]:
    """'시도 시군구' 형태 문자열을 (시도, 시군구) 튜플로 분리.

    첫 번째 공백을 기준으로 split한다. 시도는 항상 한 단어이고,
    시군구는 일반구를 포함한 경우 두 단어가 될 수 있다.

    예시:
        "서울특별시 동작구"      → ("서울특별시", "동작구")
        "경기도 수원시 영통구"   → ("경기도", "수원시 영통구")
    """
    try:
        if pd.isna(text) or not text:
            return ("", "")
    except (TypeError, ValueError):
        pass
    parts = str(text).strip().split(" ", 1)
    if len(parts) == 1:
        return (parts[0], "")
    return (parts[0], parts[1].strip())


def nearest_ems_distance_km(
    sgg_centers: gpd.GeoDataFrame, ems: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """각 시군구 중심점에서 가장 가까운 응급의료기관까지 거리(km)."""
    if sgg_centers.crs.to_string() != CRS_KOREA:
        sgg_centers = sgg_centers.to_crs(CRS_KOREA)
    if ems.crs is None or ems.crs.to_string() != CRS_KOREA:
        ems = ems.to_crs(CRS_KOREA) if ems.crs else ems.set_crs("EPSG:4326").to_crs(CRS_KOREA)

    joined = sgg_centers.sjoin_nearest(ems, distance_col="_dist_m")
    joined["ems_distance_km"] = joined["_dist_m"] / 1000.0
    return joined[["sgg_code", "geometry", "ems_distance_km"]].drop_duplicates(subset=["sgg_code"])


def aggregate_accidents_by_sgg(df: pd.DataFrame) -> pd.DataFrame:
    """사고 raw 데이터를 시군구별로 집계.

    입력 컬럼 가정: 시군구코드, 사고건수, 사망자수, 부상자수.
    실제 TAAS 컬럼명이 다르면 호출 전 rename으로 맞춤.
    """
    df = df.copy()
    df["시군구코드"] = df["시군구코드"].apply(normalize_sgg_code)
    grouped = (
        df.groupby("시군구코드")
        .agg(
            accident_count=("사고건수", "sum"),
            fatality_count=("사망자수", "sum"),
            injury_count=("부상자수", "sum"),
        )
        .reset_index()
        .rename(columns={"시군구코드": "sgg_code"})
    )
    grouped["fatality_rate"] = grouped["fatality_count"] / grouped["accident_count"]
    grouped["fatality_rate"] = grouped["fatality_rate"].fillna(0)
    return grouped
