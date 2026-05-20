"""raw 데이터 → 시군구 단위 피처 테이블."""
from __future__ import annotations

import re

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


def estimate_ems_response_time_min(
    distance_km: float | pd.Series,
    avg_speed_kmh: float = 60.0,
) -> float | pd.Series:
    """응급기관까지 거리 + 평균 속도로 예상 도착 시간(분) 추정.

    실제 119 raw 데이터에 출동시간 컬럼이 없어서 거리 기반 추정으로 대체.
    도시 평균 속도 60 km/h 가정 (도로 효율 보정 포함).

    scalar 또는 pandas Series 둘 다 처리.
    """
    return (distance_km / avg_speed_kmh) * 60.0


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


def load_sgg_centers(geojson_path) -> gpd.GeoDataFrame:
    """시군구 폴리곤 → 중심점 + 면적(km^2).

    GeoJSON 컬럼 alias 자동 매핑:
    - 시군구코드: 'SIG_CD' | '시군구코드' | 'code'
    - 시군구명: 'KOR_NM' | '시군구명' | 'name'
    """
    gdf = gpd.read_file(geojson_path)

    code_col = next(
        (c for c in gdf.columns
         if "SIG_CD" in c.upper() or "시군구코드" in c or c.lower() == "code"),
        None,
    )
    name_col = next(
        (c for c in gdf.columns
         if "KOR_NM" in c.upper() or "시군구명" in c or c.lower() == "name"),
        None,
    )
    if code_col is None:
        raise ValueError(f"시군구코드 컬럼 못 찾음. columns: {list(gdf.columns)}")
    if name_col is None:
        raise ValueError(f"시군구명 컬럼 못 찾음. columns: {list(gdf.columns)}")

    gdf = gdf.rename(columns={code_col: "sgg_code", name_col: "sgg_name"})
    gdf["sgg_code"] = gdf["sgg_code"].apply(normalize_sgg_code)
    gdf = to_korean_crs(gdf)
    gdf["area_km2"] = gdf.geometry.area / 1_000_000
    gdf["centroid"] = gdf.geometry.centroid

    centers = gdf[["sgg_code", "sgg_name", "area_km2", "centroid"]].rename(
        columns={"centroid": "geometry"}
    )
    return gpd.GeoDataFrame(centers, geometry="geometry", crs=CRS_KOREA)


def _strip_trailing_digits(text: str) -> str:
    """'정읍시1', '세종특별자치시3' 같이 끝에 붙은 숫자를 제거."""
    return re.sub(r"\d+$", "", str(text).strip()).strip()


def _normalize_name(name: str) -> str:
    """공백 제거 + 소문자 통일로 이름 정규화 (매핑 비교용)."""
    return re.sub(r"\s+", "", str(name).strip())


def _build_taas_sgg_lookup(centers: gpd.GeoDataFrame) -> dict[tuple[str, str], str]:
    """(sido_prefix, normalized_sgg_name) → sgg_code 룩업 테이블 생성.

    GeoJSON name은 공백 없이 이어 붙인 형태("수원시장안구")이므로,
    TAAS에서 파싱한 sgg_name("수원시 장안구")도 공백 제거 후 비교한다.

    세종특별자치시는 sgg_name이 없으므로 ("29", "세종시") → 코드 매핑.
    """
    lookup: dict[tuple[str, str], str] = {}
    for _, row in centers.iterrows():
        prefix = str(row["sgg_code"])[:2]
        norm = _normalize_name(row["sgg_name"])
        lookup[(prefix, norm)] = row["sgg_code"]
    return lookup


# TAAS에 남아있는 구 명칭 → 현재 GeoJSON 명칭 (공백 없는 정규화 상태로 비교)
# 부천시 일반구 폐지(2016), 인천 남구→미추홀구 개칭(2018), 여주군→여주시 승격(2013),
# 충북 청원군→청주시 편입(2014)
_TAAS_NAME_ALIAS: dict[tuple[str, str], str] = {
    ("31", "부천시원미구"): "부천시",
    ("31", "부천시소사구"): "부천시",
    ("31", "부천시오정구"): "부천시",
    ("23", "미추홀구"): "남구",
    ("31", "여주군"): "여주시",
    ("33", "청원군"): "청주시흥덕구",
}


def _map_taas_to_sgg_code(
    sido: str,
    sgg_raw: str,
    lookup: dict[tuple[str, str], str],
    sido_prefix_map: dict[str, str],
) -> str | None:
    """TAAS 한 행의 (시도명, 시군구 텍스트) → sgg_code.

    1. sido_prefix_map으로 시도 prefix 결정
    2. sgg_raw 공백 제거 후 lookup 조회
    3. 실패 시 _TAAS_NAME_ALIAS 테이블로 재시도 (행정구역 변경 대응)
    4. 실패 시 None 반환
    """
    prefix = sido_prefix_map.get(sido)
    if prefix is None:
        return None
    norm = _normalize_name(sgg_raw)
    if not norm:
        return None

    code = lookup.get((prefix, norm))
    if code is not None:
        return code

    alias_norm = _TAAS_NAME_ALIAS.get((prefix, norm))
    if alias_norm is not None:
        return lookup.get((prefix, alias_norm))

    return None


def build_grid_features(
    accidents_csv,
    ems_csv,
    sgg_geojson,
) -> pd.DataFrame:
    """모든 raw 데이터를 합쳐 시군구 단위 피처 테이블 생성.

    반환: plain DataFrame (geometry 없음).
    컬럼: sgg_code, sgg_name, area_km2, lon, lat,
          accident_count, fatality_count, injury_count, fatality_rate,
          ems_distance_km, ems_response_min, risk_index
    """
    from src.config import (
        SIDO_NAME_TO_PREFIX,
        RISK_WEIGHT_ACCIDENT_FREQ,
        RISK_WEIGHT_FATALITY_RATE,
        RISK_WEIGHT_EMS_DELAY,
    )

    # --- 1. 시군구 중심·면적 ---
    centers = load_sgg_centers(sgg_geojson)

    # --- 2. TAAS 사고 raw 로드 ---
    accidents_raw = pd.read_csv(accidents_csv, encoding="cp949", low_memory=False)

    # TAAS sgg 컬럼의 끝 숫자 제거 후 (시도, 시군구) 분리
    def _parse_taas_row(text):
        cleaned = _strip_trailing_digits(str(text))
        parts = cleaned.split(" ", 1)
        if len(parts) == 1:
            # "세종특별자치시" 같이 시도명만 있는 경우
            # 세종시는 sgg_name이 "세종시" 로 매핑
            sido = parts[0]
            sgg = "세종시" if "세종" in sido else ""
            return sido, sgg
        return parts[0], parts[1].strip()

    parsed = accidents_raw["사고다발지역시도시군구"].apply(_parse_taas_row)
    accidents_raw = accidents_raw.copy()
    accidents_raw["_sido"] = parsed.apply(lambda x: x[0])
    accidents_raw["_sgg_raw"] = parsed.apply(lambda x: x[1])

    # sgg_code 룩업 테이블
    lookup = _build_taas_sgg_lookup(centers)

    accidents_raw["sgg_code"] = accidents_raw.apply(
        lambda r: _map_taas_to_sgg_code(r["_sido"], r["_sgg_raw"], lookup, SIDO_NAME_TO_PREFIX),
        axis=1,
    )

    unmatched = accidents_raw["sgg_code"].isnull().sum()
    total = len(accidents_raw)
    print(f"  사고 행 매핑 실패: {unmatched} / {total}건 ({unmatched/total*100:.1f}%)")
    if unmatched / total > 0.5:
        # 매핑 실패율 50% 초과 시 샘플 출력
        failed_sample = accidents_raw[accidents_raw["sgg_code"].isnull()]["사고다발지역시도시군구"].unique()[:10]
        print("  매핑 실패 샘플:", failed_sample)

    accidents_mapped = accidents_raw.dropna(subset=["sgg_code"])

    # 부상자수: 부상신고자수 사용 (TAAS 실제 컬럼)
    accidents_for_agg = accidents_mapped[["sgg_code", "사고건수", "사망자수", "부상신고자수"]].copy()
    accidents_for_agg = accidents_for_agg.rename(
        columns={
            "sgg_code": "시군구코드",
            "사고건수": "사고건수",
            "사망자수": "사망자수",
            "부상신고자수": "부상자수",
        }
    )
    accidents = aggregate_accidents_by_sgg(accidents_for_agg)

    # --- 3. 응급의료기관 → 시군구별 최근접 거리 ---
    ems_df = pd.read_csv(ems_csv, encoding="utf-8-sig", low_memory=False)
    ems_df = ems_df.dropna(subset=["wgs84Lat", "wgs84Lon"])
    ems = gpd.GeoDataFrame(
        ems_df,
        geometry=gpd.points_from_xy(ems_df["wgs84Lon"], ems_df["wgs84Lat"]),
        crs="EPSG:4326",
    )
    ems_dist = nearest_ems_distance_km(centers, ems)

    # --- 4. 응급 도착시간 추정 ---
    ems_dist = ems_dist.copy()
    ems_dist["ems_response_min"] = estimate_ems_response_time_min(ems_dist["ems_distance_km"])

    # --- 5. 병합: centers + accidents + ems ---
    features = centers.merge(accidents, on="sgg_code", how="left").merge(
        ems_dist[["sgg_code", "ems_distance_km", "ems_response_min"]],
        on="sgg_code",
        how="left",
    )

    # 결측 보정
    features["accident_count"] = features["accident_count"].fillna(0)
    features["fatality_count"] = features["fatality_count"].fillna(0)
    features["injury_count"] = features["injury_count"].fillna(0)
    features["fatality_rate"] = features["fatality_rate"].fillna(0)
    features["ems_distance_km"] = features["ems_distance_km"].fillna(features["ems_distance_km"].median())
    features["ems_response_min"] = features["ems_response_min"].fillna(features["ems_response_min"].median())

    # 위경도 컬럼 추가 (지도 시각화용)
    features_wgs = features.to_crs("EPSG:4326")
    features = features.copy()
    features["lon"] = features_wgs.geometry.x
    features["lat"] = features_wgs.geometry.y

    # --- 6. 위험 지수 계산 (min-max 정규화 후 가중합) ---
    def _minmax(s: pd.Series) -> pd.Series:
        mn, mx = s.min(), s.max()
        return (s - mn) / (mx - mn + 1e-9)

    features["risk_index"] = (
        RISK_WEIGHT_ACCIDENT_FREQ * _minmax(features["accident_count"])
        + RISK_WEIGHT_FATALITY_RATE * _minmax(features["fatality_rate"])
        + RISK_WEIGHT_EMS_DELAY * _minmax(features["ems_response_min"] + features["ems_distance_km"])
    )

    # geometry 컬럼 제거 후 plain DataFrame 반환
    return pd.DataFrame(features.drop(columns=["geometry"]))
