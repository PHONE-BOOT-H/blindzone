"""XGBoost 회귀로 risk_index를 예측하는 모델 학습."""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from src.config import GRID_FEATURES_PATH, MODEL_PATH

FEATURE_COLS = [
    "accident_count",
    "fatality_count",
    "fatality_rate",
    "injury_count",
    "ems_distance_km",
    "ems_response_min",
    "area_km2",
]
TARGET_COL = "risk_index"


def load_dataset(path: Path = GRID_FEATURES_PATH):
    df = pd.read_parquet(path)
    X = df[FEATURE_COLS].fillna(0)
    y = df[TARGET_COL]
    return X, y, df


def train_and_save(model_path: Path = MODEL_PATH):
    X, y, _ = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = {
        "r2": r2_score(y_test, preds),
        "mae": mean_absolute_error(y_test, preds),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "feature_cols": FEATURE_COLS, "metrics": metrics}, f)
    print(f"saved: {model_path}")
    print(f"metrics: {metrics}")
    return metrics


if __name__ == "__main__":
    train_and_save()
