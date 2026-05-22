# backend/api/routes.py
import numpy as np
from fastapi import APIRouter, HTTPException

from api import schemas
from api.deps import get_features, get_model_bundle, parse_shap


def _haversine_km(lon1, lat1, lon2, lat2):
    """단순 haversine 거리 (km). lon/lat은 array 또는 scalar 가능."""
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return R * 2 * np.arcsin(np.sqrt(a))


router = APIRouter()


@router.get("/health", response_model=schemas.HealthResponse)
def health():
    try:
        features = get_features()
        bundle = get_model_bundle()
        return schemas.HealthResponse(
            status="ok",
            model_loaded=bundle is not None,
            features_loaded=features is not None,
            feature_count=len(features),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/features", response_model=list[schemas.FeatureSummary])
def list_features():
    df = get_features()
    cols = ["sgg_code", "sgg_name", "lon", "lat", "risk_index",
            "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min"]
    out = df[cols].copy()
    out["accident_count"] = out["accident_count"].astype(int)
    return out.to_dict(orient="records")


@router.get("/features/{sgg_code}", response_model=schemas.FeatureDetail)
def get_feature_detail(sgg_code: str):
    df = get_features()
    row = df[df["sgg_code"] == sgg_code]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"sgg_code {sgg_code} not found")
    row = row.iloc[0]
    shap_list = parse_shap(row.get("shap_top_json", ""))
    return schemas.FeatureDetail(
        sgg_code=row["sgg_code"],
        sgg_name=row["sgg_name"],
        lon=float(row["lon"]),
        lat=float(row["lat"]),
        risk_index=float(row["risk_index"]),
        accident_count=int(row["accident_count"]),
        fatality_rate=float(row["fatality_rate"]),
        ems_distance_km=float(row["ems_distance_km"]),
        ems_response_min=float(row["ems_response_min"]),
        area_km2=float(row["area_km2"]),
        fatality_count=int(row["fatality_count"]),
        injury_count=int(row["injury_count"]),
        shap_top=[schemas.ShapItem(**item) for item in shap_list],
    )


@router.get("/top10", response_model=list[schemas.FeatureSummary])
def top10():
    df = get_features()
    top = df.nlargest(10, "risk_index")
    cols = ["sgg_code", "sgg_name", "lon", "lat", "risk_index",
            "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min"]
    out = top[cols].copy()
    out["accident_count"] = out["accident_count"].astype(int)
    return out.to_dict(orient="records")


@router.post("/simulate", response_model=schemas.SimulateResponse)
def simulate(req: schemas.SimulateRequest):
    df = get_features()
    bundle = get_model_bundle()
    model = bundle["model"]
    cols = bundle["feature_cols"]

    if not req.virtual_ems:
        return schemas.SimulateResponse(
            avg_delta=0.0, max_drop=0.0, improved_count=0, items=[]
        )

    # 각 시군구 중심점에서 가상 ems까지 거리 (km, haversine)
    new_dist_arr = df["ems_distance_km"].values.copy()
    for vlon, vlat in req.virtual_ems:
        d = _haversine_km(df["lon"].values, df["lat"].values, vlon, vlat)
        new_dist_arr = np.minimum(new_dist_arr, d)

    # 모델 재추론
    X_new = df[cols].copy().fillna(0)
    X_new["ems_distance_km"] = new_dist_arr
    risk_new = model.predict(X_new)

    result = df.copy()
    result["risk_index_new"] = risk_new
    result["risk_delta"] = result["risk_index_new"] - result["risk_index"]
    result["ems_distance_km_new"] = new_dist_arr

    avg_delta = float(result["risk_delta"].mean())
    max_drop = float(result["risk_delta"].min())
    improved_count = int((result["risk_delta"] < -0.001).sum())

    top_items = result.nsmallest(50, "risk_delta")
    items = [
        schemas.SimulationItem(
            sgg_code=r["sgg_code"],
            sgg_name=r["sgg_name"],
            lon=float(r["lon"]),
            lat=float(r["lat"]),
            risk_index=float(r["risk_index"]),
            risk_index_new=float(r["risk_index_new"]),
            risk_delta=float(r["risk_delta"]),
            ems_distance_km_new=float(r["ems_distance_km_new"]),
        )
        for _, r in top_items.iterrows()
    ]
    return schemas.SimulateResponse(
        avg_delta=avg_delta,
        max_drop=max_drop,
        improved_count=improved_count,
        items=items,
    )
