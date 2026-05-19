from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_SAMPLE = ROOT / "data" / "sample"
MODELS = ROOT / "models"

CRS_KOREA = "EPSG:5179"
CRS_WGS84 = "EPSG:4326"

GRID_FEATURES_PATH = DATA_PROCESSED / "grid_features.parquet"
MODEL_PATH = MODELS / "xgb_risk_model.pkl"

# 위험 지수 계산 가중치 (EDA 후 조정 가능)
RISK_WEIGHT_ACCIDENT_FREQ = 0.4
RISK_WEIGHT_FATALITY_RATE = 0.3
RISK_WEIGHT_EMS_DELAY = 0.3
