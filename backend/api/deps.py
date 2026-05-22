# backend/api/deps.py
"""SHAP 사전 계산된 feature_details와 모델 싱글톤 로드."""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import FEATURE_DETAILS_PATH, MODEL_PATH  # noqa: E402

_features: pd.DataFrame | None = None
_model_bundle: dict | None = None


def get_features() -> pd.DataFrame:
    """SHAP 사전 계산된 feature_details parquet 로드."""
    global _features
    if _features is None:
        _features = pd.read_parquet(FEATURE_DETAILS_PATH)
    return _features


def get_model_bundle() -> dict:
    """XGBoost 모델 로드 — simulate endpoint에서만 사용."""
    global _model_bundle
    if _model_bundle is None:
        with open(MODEL_PATH, "rb") as f:
            _model_bundle = pickle.load(f)
    return _model_bundle


def parse_shap(json_str: str) -> list[dict]:
    """parquet에 저장된 shap_top_json 문자열 → 리스트."""
    if not json_str:
        return []
    return json.loads(json_str)
