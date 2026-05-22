# backend/api/routes.py
from fastapi import APIRouter, HTTPException

from api import schemas
from api.deps import get_features, get_model_bundle, parse_shap

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
