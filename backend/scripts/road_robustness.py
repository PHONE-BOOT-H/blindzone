"""실거리 기반 robust 재산출.

build_road_distances.py가 만든 road_distance_252.csv(OSRM 도로 실거리)를 사용해,
위험지수의 응급접근성 항목을 직선거리 대신 도로 실거리·실소요시간으로 바꿔
126개 가중치 시나리오 robust를 재산출한다. 직선거리 기반 결론(인제·옹진)이
실거리에서도 유지되는지 검증한다.

가중치 시나리오·정규화는 weight_sensitivity.py와 동일(일관성).
실행: py -3.12 backend/scripts/road_robustness.py
"""
import sys, io, warnings
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import numpy as np
import pandas as pd

warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
SUB = ROOT.parent / "docs" / "submission"
ROAD_CSV = SUB / "road_distance_252.csv"

BASE_W = (0.40, 0.30, 0.30)


def minmax(s):
    s = pd.Series(s).astype(float)
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-9)


def build_weight_scenarios():
    named = {
        "baseline": (0.40, 0.30, 0.30), "equal": (1/3, 1/3, 1/3),
        "acc_heavy": (0.60, 0.20, 0.20), "ems_heavy": (0.25, 0.25, 0.50),
        "fatal_heavy": (0.25, 0.50, 0.25), "conservative": (0.45, 0.20, 0.35),
    }
    grid = {}
    vals = np.round(np.arange(0.10, 0.81, 0.05), 2)
    i = 0
    for wa in vals:
        for wf in vals:
            we = round(1.0 - wa - wf, 2)
            if 0.10 <= we <= 0.80:
                grid[f"grid_{i:03d}"] = (float(wa), float(wf), we)
                i += 1
    return {**named, **grid}


def robust_table(df, ems_metric):
    """ems_metric: 위험지수 응급접근성 항목으로 쓸 컬럼(직선 또는 도로). 126 시나리오 robust 반환."""
    acc_n = minmax(df["accident_count"])
    fat_n = minmax(df["fatality_rate"])
    ems_n = minmax(df[ems_metric])
    weights = build_weight_scenarios()
    ranks = pd.DataFrame(index=df.index)
    for name, (wa, wf, we) in weights.items():
        sc = wa * acc_n + wf * fat_n + we * ems_n
        ranks[name] = sc.rank(ascending=False, method="min")
    top10_share = (ranks <= 10).mean(axis=1)
    return pd.DataFrame({
        "sgg_name": df["sgg_name"],
        "accident_count": df["accident_count"].astype(int),
        "baseline_rank": ranks["baseline"].astype(int),
        "rank_median": ranks.median(axis=1),
        "top10_share": top10_share.round(3),
    })


def main():
    if not ROAD_CSV.exists():
        print(f"[대기] {ROAD_CSV} 없음. 먼저 build_road_distances.py 실행 필요.")
        return
    gf = pd.read_parquet(PROC / "grid_features.parquet")
    road = pd.read_csv(ROAD_CSV, dtype={"sgg_code": str})
    gf["sgg_code"] = gf["sgg_code"].astype(str)
    df = gf.merge(road[["sgg_code", "road_km", "road_min", "detour_ratio", "osrm_ok"]],
                  on="sgg_code", how="left")
    n_ok = int(df["osrm_ok"].fillna(False).sum())
    print(f"merge: {len(df)}개, OSRM 성공 {n_ok}")

    # 직선: ems_response_min + ems_distance_km (data_pipeline 정의와 동일)
    df["ems_straight"] = df["ems_response_min"] + df["ems_distance_km"]
    # 도로: road_min + road_km (동형)
    df["ems_road"] = df["road_min"].fillna(df["ems_response_min"]) + df["road_km"].fillna(df["ems_distance_km"])

    rs = robust_table(df, "ems_straight").rename(columns={
        "baseline_rank": "rank_s", "rank_median": "med_s", "top10_share": "t10_s"})
    rr = robust_table(df, "ems_road").rename(columns={
        "baseline_rank": "rank_r", "rank_median": "med_r", "top10_share": "t10_r"})
    comp = rs[["sgg_name", "accident_count", "rank_s", "med_s", "t10_s"]].join(
        rr[["rank_r", "med_r", "t10_r"]])

    print("\n[직선 vs 실거리 robust 비교 - 인제/옹진]")
    print("  (rank_s/med_s/t10_s = 직선,  rank_r/med_r/t10_r = 도로실거리)")
    for kw in ["인제", "옹진"]:
        r = comp[comp["sgg_name"].str.contains(kw, na=False)].iloc[0]
        print(f"  {r['sgg_name']}: 직선 base{int(r['rank_s'])} t10={r['t10_s']:.2f}  ->  "
              f"실거리 base{int(r['rank_r'])} t10={r['t10_r']:.2f}")

    print("\n[실거리 기준 robust top10_share>=0.6]")
    rob = comp[comp["t10_r"] >= 0.6].sort_values("t10_r", ascending=False)
    for _, r in rob.iterrows():
        print(f"  {r['sgg_name']:<10} acc{int(r['accident_count']):>5} "
              f"base{int(r['rank_r']):>3} t10={r['t10_r']:.2f}")

    out = comp.sort_values("t10_r", ascending=False)
    out.to_csv(SUB / "road_robustness_summary.csv", index=False, encoding="utf-8-sig")
    print(f"\n저장: {SUB / 'road_robustness_summary.csv'}")


if __name__ == "__main__":
    main()
