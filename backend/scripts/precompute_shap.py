"""모든 시군구에 대해 SHAP 상위 3개 피처를 사전 계산하여 parquet에 저장."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import GRID_FEATURES_PATH, DATA_PROCESSED  # noqa: E402
from src.shap_explain import explain_one  # noqa: E402


def main():
    df = pd.read_parquet(GRID_FEATURES_PATH)
    print(f"computing SHAP for {len(df)} rows ...")
    shap_rows = []
    for _, row in df.iterrows():
        try:
            items = explain_one(row)
        except Exception as exc:
            print(f"  [WARN] sgg {row['sgg_code']}: {exc}")
            items = []
        shap_rows.append(json.dumps(items, ensure_ascii=False))
    df_out = df.copy()
    df_out["shap_top_json"] = shap_rows
    out_path = DATA_PROCESSED / "feature_details.parquet"
    df_out.to_parquet(out_path, index=False)
    print(f"saved: {out_path} ({len(df_out)} rows)")


if __name__ == "__main__":
    main()
