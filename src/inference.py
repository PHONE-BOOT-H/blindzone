"""가상 응급기관 추가 시 영향 시뮬레이션."""
from __future__ import annotations

import pickle

import numpy as np
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

from src.config import CRS_KOREA, MODEL_PATH, GRID_FEATURES_PATH


def simulate_new_ems(virtual_ems_lonlat: list[tuple[float, float]]) -> pd.DataFrame:
    """가상 응급기관 좌표들을 추가했을 때 각 시군구의 ems_distance_km 재계산 + risk_index 재예측.

    Args:
        virtual_ems_lonlat: [(lon, lat), ...] WGS84 좌표
    Returns:
        DataFrame: 시군구별 before/after risk_index
    """
    features = pd.read_parquet(GRID_FEATURES_PATH)
    centers = gpd.GeoDataFrame(
        features,
        geometry=gpd.points_from_xy(features["lon"], features["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_KOREA)

    if not virtual_ems_lonlat:
        return features.assign(risk_index_new=features["risk_index"])

    v_ems = gpd.GeoDataFrame(
        geometry=[Point(lon, lat) for lon, lat in virtual_ems_lonlat],
        crs="EPSG:4326",
    ).to_crs(CRS_KOREA)

    # 기존 ems_distance_km와 가상 ems까지 거리 중 최소값
    centers_with_v = centers.sjoin_nearest(v_ems, distance_col="_v_dist_m")
    centers_with_v["v_dist_km"] = centers_with_v["_v_dist_m"] / 1000.0
    new_dist = np.minimum(
        centers_with_v["ems_distance_km"].values,
        centers_with_v["v_dist_km"].values,
    )

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    model = bundle["model"]
    cols = bundle["feature_cols"]

    X_new = features[cols].copy().fillna(0)
    X_new["ems_distance_km"] = new_dist
    risk_new = model.predict(X_new)

    result = features.copy()
    result["risk_index_new"] = risk_new
    result["risk_delta"] = result["risk_index_new"] - result["risk_index"]
    result["ems_distance_km_new"] = new_dist
    return result
