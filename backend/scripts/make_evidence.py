"""AI 분석도구(XGBoost+SHAP) 활용 증빙 그림 생성 → docs/submission/evidence/.

가점 증빙용: 실제 학습 결과·SHAP 산출물을 이미지로 만든다(캡처보다 직접 증거).
실행: py -3.12 backend/scripts/make_evidence.py
"""
import sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import shap
from xgboost import plot_importance

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.config import MODEL_PATH, GRID_FEATURES_PATH  # noqa: E402

OUT = ROOT.parent / "docs" / "submission" / "evidence"
OUT.mkdir(parents=True, exist_ok=True)

with open(MODEL_PATH, "rb") as f:
    bundle = pickle.load(f)
model, cols, metrics = bundle["model"], bundle["feature_cols"], bundle.get("metrics", {})
print("model metrics:", metrics)

df = pd.read_parquet(GRID_FEATURES_PATH)
X = df[cols].fillna(0)

# 1) XGBoost feature importance
fig, ax = plt.subplots(figsize=(7, 4.2))
plot_importance(model, ax=ax, importance_type="gain", show_values=False,
                title="XGBoost Feature Importance (gain)")
plt.tight_layout()
fig.savefig(OUT / "01_xgboost_feature_importance.png", dpi=150)
plt.close(fig)
print("saved 01_xgboost_feature_importance.png")

# 2) SHAP summary (beeswarm)
explainer = shap.TreeExplainer(model)
sv = explainer.shap_values(X)
plt.figure()
shap.summary_plot(sv, X, show=False, plot_size=(8, 4.5))
plt.title("SHAP Summary (Risk Index Contributors)", fontsize=10)
plt.tight_layout()
plt.savefig(OUT / "02_shap_summary.png", dpi=150, bbox_inches="tight")
plt.close()
print("saved 02_shap_summary.png")

# 3) SHAP bar (mean |SHAP|)
plt.figure()
shap.summary_plot(sv, X, plot_type="bar", show=False, plot_size=(8, 4))
plt.title("Mean |SHAP value| by Feature", fontsize=10)
plt.tight_layout()
plt.savefig(OUT / "03_shap_bar.png", dpi=150, bbox_inches="tight")
plt.close()
print("saved 03_shap_bar.png")

# 4) 인제군 force plot (단일 지역 설명) → matplotlib 버전
for kw in ["인제"]:
    idx = df.index[df["sgg_name"].str.contains(kw, na=False)][0]
    plt.figure()
    shap.plots._waterfall.waterfall_legacy(
        explainer.expected_value, sv[idx], feature_names=cols, show=False)
    plt.title("Inje-gun SHAP Breakdown (Risk Index)", fontsize=10)
    plt.tight_layout()
    plt.savefig(OUT / "04_shap_inje_waterfall.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("saved 04_shap_inje_waterfall.png")

print(f"\n완료. {OUT}")
