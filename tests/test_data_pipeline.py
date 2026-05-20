import pandas as pd
from src.data_pipeline import normalize_sgg_code, to_korean_crs, parse_sido_sgg


def test_normalize_sgg_code_pads_to_5_digits():
    assert normalize_sgg_code(11010) == "11010"
    assert normalize_sgg_code("11010") == "11010"
    assert normalize_sgg_code("11010.0") == "11010"
    assert normalize_sgg_code(1101) == "01101"  # 4자리 입력은 left-pad


def test_to_korean_crs_converts_wgs84_to_5179():
    import geopandas as gpd
    from shapely.geometry import Point
    gdf = gpd.GeoDataFrame({"geometry": [Point(126.978, 37.566)]}, crs="EPSG:4326")
    result = to_korean_crs(gdf)
    assert result.crs.to_string() == "EPSG:5179"
    assert result.geometry.iloc[0].x > 900000


def test_parse_sido_sgg_splits_correctly():
    assert parse_sido_sgg("서울특별시 동작구") == ("서울특별시", "동작구")
    assert parse_sido_sgg("경기도 수원시 영통구") == ("경기도", "수원시 영통구")
    assert parse_sido_sgg("부산광역시 해운대구") == ("부산광역시", "해운대구")
