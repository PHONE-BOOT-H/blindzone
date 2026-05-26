"""레버1-b·4: 수요(고령)변수 교차분석 + 수혜인구 정량화.

grid_features_demo.parquet(고령비율 병합)와 robust 요약(weight_sensitivity_summary.csv)을
교차해, robust 사각지대(인제·옹진)가 수요측(고령)에서도 취약한지 정량화하고,
가상 응급거점 추가 시 잠재 수혜 인구를 환산한다.

실행: py -3.12 backend/scripts/demand_analysis.py
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SUB = ROOT.parent / "docs" / "submission"


def main():
    demo = pd.read_parquet(PROC / "grid_features_demo.parquet")
    demo["sgg_code"] = demo["sgg_code"].astype(str)
    n = len(demo)

    # 고령비율 분포
    er = demo["elderly_ratio"]
    print(f"[고령비율 분포] n={n}  중앙값 {er.median():.1f}%  평균 {er.mean():.1f}%  "
          f"min {er.min():.1f}%  max {er.max():.1f}%")

    # 인제·옹진 백분위(전국 순위, 높을수록 고령)
    demo["elderly_rank"] = demo["elderly_ratio"].rank(ascending=False, method="min")
    for kw in ["인제", "옹진"]:
        r = demo[demo["sgg_name"].str.contains(kw, na=False)].iloc[0]
        pct = (1 - r["elderly_rank"] / n) * 100
        print(f"  {r['sgg_name']}: 고령 {r['elderly_ratio']:.1f}% "
              f"(전국 {int(r['elderly_rank'])}/{n}위, 상위 {100-pct:.0f}%) "
              f"총인구 {int(r['total_pop']):,} 고령 {int(r['elderly_pop']):,}")

    # robust 사각지대(weight_sensitivity_summary) 교차
    summ = pd.read_csv(SUB / "weight_sensitivity_summary.csv", dtype={"sgg_code": str})
    rob = summ[summ["top10_share"] >= 0.6].copy()
    m = rob.merge(demo[["sgg_code", "elderly_ratio", "total_pop", "elderly_pop"]],
                  on="sgg_code", how="left")
    print(f"\n[robust 8곳(top10_share>=0.6) 고령비율 — 대도시 vs 사각지대]")
    print(f"  {'시군구':<8}{'사고':>6}{'top10':>7}{'고령%':>7}{'유형'}")
    for _, r in m.iterrows():
        typ = "사각지대" if r["accident_count"] <= 1 else "대도시"
        print(f"  {r['sgg_name']:<8}{int(r['accident_count']):>6}{r['top10_share']:>7.2f}"
              f"{r['elderly_ratio']:>7.1f}  {typ}")
    daegu_avg = m[m["accident_count"] > 1]["elderly_ratio"].mean()
    blind_avg = m[m["accident_count"] <= 1]["elderly_ratio"].mean()
    print(f"  → 대도시 robust 평균 고령 {daegu_avg:.1f}% vs 사각지대(인제·옹진) 평균 {blind_avg:.1f}%")

    # 레버4: 수혜인구 (시뮬레이션 거점 추가 시 도착시간 단축 대상 = 해당 시군구 인구)
    print(f"\n[레버4: 가상 응급거점 1곳 추가 시 잠재 수혜 인구]")
    sims = {  # case-study/시뮬 결과: (직선 before, 직선 after km)
        "인제": (24.2, 8.23),
        "옹진": (75.3, 15.3),
    }
    for kw, (before, after) in sims.items():
        r = demo[demo["sgg_name"].str.contains(kw, na=False)].iloc[0]
        print(f"  {r['sgg_name']}: 응급거리 {before}→{after}km. 잠재 수혜 "
              f"총인구 {int(r['total_pop']):,}명 (고령 {int(r['elderly_pop']):,}명, "
              f"{r['elderly_ratio']:.1f}%)")


if __name__ == "__main__":
    main()
