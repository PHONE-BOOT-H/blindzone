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
FEATURE_DETAILS_PATH = DATA_PROCESSED / "feature_details.parquet"

# 위험 지수 계산 가중치 (EDA 후 조정 가능)
RISK_WEIGHT_ACCIDENT_FREQ = 0.4
RISK_WEIGHT_FATALITY_RATE = 0.3
RISK_WEIGHT_EMS_DELAY = 0.3

# 시도명 → GeoJSON code prefix 매핑
# (GeoJSON은 표준 행정코드가 아닌 자체 번호 체계 사용)
SIDO_NAME_TO_PREFIX = {
    "서울특별시": "11",
    "부산광역시": "21",
    "대구광역시": "22",
    "인천광역시": "23",
    "광주광역시": "24",
    "대전광역시": "25",
    "울산광역시": "26",
    "세종특별자치시": "29",
    "경기도": "31",
    "강원도": "32",
    "강원특별자치도": "32",
    "충청북도": "33",
    "충북": "33",
    "충청남도": "34",
    "충남": "34",
    "전라북도": "35",
    "전북특별자치도": "35",
    "전북": "35",
    "전라남도": "36",
    "전남": "36",
    "경상북도": "37",
    "경북": "37",
    "경상남도": "38",
    "경남": "38",
    "제주특별자치도": "39",
    "제주도": "39",
}
