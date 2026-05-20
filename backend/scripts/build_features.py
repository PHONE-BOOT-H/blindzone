"""raw → data/processed/grid_features.parquet 생성."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_pipeline import build_grid_features  # noqa: E402
from src.config import DATA_RAW, GRID_FEATURES_PATH  # noqa: E402


def main():
    print("grid_features.parquet 빌드 시작...")
    features = build_grid_features(
        accidents_csv=DATA_RAW / "taas_다발지역.csv",
        ems_csv=DATA_RAW / "응급의료기관.csv",
        sgg_geojson=DATA_RAW / "시군구_경계.geojson",
    )
    GRID_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(GRID_FEATURES_PATH, index=False)
    print(f"\nsaved: {GRID_FEATURES_PATH} ({len(features)} rows, {len(features.columns)} cols)")
    print(f"\ncolumns: {list(features.columns)}")
    print(f"\nrisk_index 분포:\n{features['risk_index'].describe()}")
    print(f"\nNaN 확인:\n{features.isnull().sum()}")
    print("\n상위 10개 위험지대:")
    print(
        features.nlargest(10, "risk_index")[
            ["sgg_name", "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min", "risk_index"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
