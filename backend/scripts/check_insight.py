"""V1 시군구 단위 인사이트가 충분히 강한지 확인.

핵심 질문: '사고는 평균인데 응급은 늦은' 시군구가 통계적으로 의미 있게 존재하나?
존재하면 시군구 V1 OK. 약하면 1km 격자로 전환 (V1.1 앞당김).
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import GRID_FEATURES_PATH  # noqa: E402


def main():
    df = pd.read_parquet(GRID_FEATURES_PATH)
    print(f"총 시군구: {len(df)}")
    print(f"\nrisk_index 분포:\n{df['risk_index'].describe()}")

    # '평균 사고 수준이지만 응급 사각'인 그룹
    median_acc = df["accident_count"].median()
    p75_ems = df["ems_response_min"].quantile(0.75)
    blind_zone = df[
        (df["accident_count"].between(median_acc * 0.5, median_acc * 1.5))
        & (df["ems_response_min"] >= p75_ems)
    ]
    print(f"\n'사고는 평균인데 응급 늦은' 시군구: {len(blind_zone)}개")
    print(blind_zone[["sgg_name", "sgg_code", "accident_count", "ems_response_min", "risk_index"]].head(15))

    # 판정
    if len(blind_zone) >= 10:
        print("\n→ V1 시군구 단위 OK (발견 임팩트 충분)")
    else:
        print("\n→ 시군구 단위 인사이트 약함. V1.1 격자 전환 권장.")


if __name__ == "__main__":
    main()
