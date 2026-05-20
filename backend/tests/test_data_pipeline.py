import math

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from src.data_pipeline import normalize_sgg_code, to_korean_crs, parse_sido_sgg


def test_normalize_sgg_code_pads_to_5_digits():
    assert normalize_sgg_code(11010) == "11010"
    assert normalize_sgg_code("11010") == "11010"
    assert normalize_sgg_code("11010.0") == "11010"
    assert normalize_sgg_code(1101) == "01101"  # 4자리 입력은 left-pad


def test_to_korean_crs_converts_wgs84_to_5179():
    gdf = gpd.GeoDataFrame({"geometry": [Point(126.978, 37.566)]}, crs="EPSG:4326")
    result = to_korean_crs(gdf)
    assert result.crs.to_string() == "EPSG:5179"
    assert result.geometry.iloc[0].x > 900000


def test_parse_sido_sgg_splits_correctly():
    assert parse_sido_sgg("서울특별시 동작구") == ("서울특별시", "동작구")
    assert parse_sido_sgg("경기도 수원시 영통구") == ("경기도", "수원시 영통구")
    assert parse_sido_sgg("부산광역시 해운대구") == ("부산광역시", "해운대구")


def test_normalize_sgg_code_handles_nan_and_none():
    assert normalize_sgg_code(math.nan) == ""
    assert normalize_sgg_code(None) == ""


def test_to_korean_crs_handles_missing_crs():
    gdf = gpd.GeoDataFrame({"geometry": [Point(126.978, 37.566)]}, crs=None)
    result = to_korean_crs(gdf)
    assert result.crs.to_string() == "EPSG:5179"


def test_parse_sido_sgg_handles_empty_and_single_word():
    assert parse_sido_sgg("") == ("", "")
    assert parse_sido_sgg("서울특별시") == ("서울특별시", "")


def test_parse_sido_sgg_handles_double_space():
    # Real data sometimes has double spaces from encoding artifacts
    assert parse_sido_sgg("서울특별시  동작구") == ("서울특별시", "동작구")


def test_aggregate_accidents_groups_by_sgg():
    from src.data_pipeline import aggregate_accidents_by_sgg
    df = pd.DataFrame({
        "시군구코드": ["11010", "11010", "11020"],
        "사고건수": [10, 5, 3],
        "사망자수": [1, 0, 0],
        "부상자수": [12, 6, 4],
    })
    out = aggregate_accidents_by_sgg(df)
    assert len(out) == 2
    row_11010 = out[out["sgg_code"] == "11010"].iloc[0]
    assert row_11010["accident_count"] == 15
    assert row_11010["fatality_count"] == 1
    assert row_11010["fatality_rate"] == 1 / 15


def test_nearest_ems_distance_returns_km():
    from shapely.geometry import Point
    from src.data_pipeline import nearest_ems_distance_km

    sgg_centers = gpd.GeoDataFrame(
        {"sgg_code": ["11010"], "geometry": [Point(953000, 1953000)]},
        crs="EPSG:5179",
    )
    ems = gpd.GeoDataFrame(
        {"name": ["A응급실"], "geometry": [Point(963000, 1953000)]},
        crs="EPSG:5179",
    )
    out = nearest_ems_distance_km(sgg_centers, ems)
    assert "ems_distance_km" in out.columns
    assert abs(out["ems_distance_km"].iloc[0] - 10.0) < 0.01


def test_estimate_ems_response_time_min_scalar():
    from src.data_pipeline import estimate_ems_response_time_min
    # 60km/h 가정 시 10km는 10분
    assert abs(estimate_ems_response_time_min(10.0) - 10.0) < 0.01
    # 평균 속도를 30km/h로 바꾸면 10km는 20분
    assert abs(estimate_ems_response_time_min(10.0, avg_speed_kmh=30.0) - 20.0) < 0.01
    # 0km는 0분
    assert estimate_ems_response_time_min(0.0) == 0.0


def test_estimate_ems_response_time_min_series():
    import numpy as np
    from src.data_pipeline import estimate_ems_response_time_min
    s = pd.Series([6.0, 12.0, 30.0])
    out = estimate_ems_response_time_min(s)
    expected = pd.Series([6.0, 12.0, 30.0])  # @60km/h: 6→6min, 12→12min, 30→30min
    assert np.allclose(out.values, expected.values, atol=0.01)
