# src/shap_explain.py
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import shap

from src.config import MODEL_PATH
from src.train import FEATURE_COLS


def load_model(path: Path = MODEL_PATH):
    with open(path, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle.get("feature_cols", FEATURE_COLS)


def explain_one(features_row: pd.Series, top_n: int = 3) -> list[dict]:
    """단일 시군구에 대한 상위 N개 기여 피처 추출."""
    model, cols = load_model()
    X = features_row[cols].to_frame().T.fillna(0).astype(float)
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X)[0]
    pairs = sorted(zip(cols, shap_vals), key=lambda kv: abs(kv[1]), reverse=True)
    feature_label = {
        "accident_count": "사고 빈도",
        "fatality_count": "사망사고 수",
        "fatality_rate": "사망사고 비율",
        "injury_count": "부상자 수",
        "ems_distance_km": "응급기관까지 거리",
        "ems_response_min": "평균 출동시간",
        "area_km2": "면적",
    }
    return [
        {
            "feature": feature_label.get(name, name),
            "shap_value": float(val),
            "direction": "위험 증가" if val > 0 else "위험 감소",
        }
        for name, val in pairs[:top_n]
    ]
