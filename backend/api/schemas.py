# backend/api/schemas.py
from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureSummary(BaseModel):
    sgg_code: str
    sgg_name: str
    lon: float
    lat: float
    risk_index: float
    accident_count: int
    fatality_rate: float
    ems_distance_km: float
    ems_response_min: float


class ShapItem(BaseModel):
    feature: str
    shap_value: float
    direction: str  # "위험 증가" | "위험 감소"


class FeatureDetail(FeatureSummary):
    area_km2: float
    fatality_count: int
    injury_count: int
    shap_top: list[ShapItem]


class SimulateRequest(BaseModel):
    virtual_ems: list[tuple[float, float]] = Field(
        default_factory=list,
        description="가상 응급의료 거점 좌표 [(lon, lat), ...]"
    )


class SimulationItem(BaseModel):
    sgg_code: str
    sgg_name: str
    lon: float
    lat: float
    risk_index: float
    risk_index_new: float
    risk_delta: float
    ems_distance_km_new: float


class SimulateResponse(BaseModel):
    avg_delta: float
    max_drop: float
    improved_count: int
    items: list[SimulationItem]


class ContrastItem(BaseModel):
    sgg_code: str
    sgg_name: str
    accident_count: int
    accident_rank: int  # 사고건수 순위
    risk_rank: int       # BlindZone 순위
    rank_diff: int       # 사고 순위 - BlindZone 순위 (양수면 BlindZone에서 더 위험)


class ContrastResponse(BaseModel):
    blindzone_top10_not_in_accident_top10: int
    accident_top10_not_in_blindzone_top10: int
    items: list[ContrastItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    features_loaded: bool
    feature_count: int
