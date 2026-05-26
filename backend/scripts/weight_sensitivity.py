"""가중치 민감도 분석 + 사망률 smoothing 영향 분석.

배경 (외부 AI 2차 평가, 2026-05-23):
  BlindZone 위험지수는 실제 사고/사망을 예측하는 모델이 아니라
  0.4/0.3/0.3 가중합으로 정의한 '잠재 위험지수'이다. 따라서 가중치가
  사실상 모델 그 자체이며, "왜 0.4/0.3/0.3이냐"는 임의성이 방법론
  최대 약점이다. 단일 순위를 '정답'으로 방어하는 대신, 합리적 가중치
  공간 전반에서 반복적으로 상위에 남는 지역(robust blind zone)을
  제시하여 임의성을 '관리된 불확실성'으로 전환한다.

산출물:
  - docs/submission/weight_sensitivity_summary.csv  (252개 시군구 순위 안정성)
  - docs/submission/smoothing_effect.csv            (소표본 사망률 보정 전후)
  콘솔에는 검증 결과 + 핵심 수치만 출력 (한글 상세는 CSV에서 확인).

정규화/가중합 방식은 src/data_pipeline.py build_grid_features 의 위험지수
계산식과 동일하게 맞춘다 (baseline 재현 검증으로 보장).
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# 시나리오별 순위 컬럼을 반복 추가하며 나오는 성능 경고는 결과에 영향 없음
warnings.simplefilter("ignore", category=pd.errors.PerformanceWarning)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import (  # noqa: E402
    GRID_FEATURES_PATH,
    RISK_WEIGHT_ACCIDENT_FREQ,
    RISK_WEIGHT_FATALITY_RATE,
    RISK_WEIGHT_EMS_DELAY,
)

OUT_DIR = Path(__file__).resolve().parents[2] / "docs" / "submission"

BASE_W = (RISK_WEIGHT_ACCIDENT_FREQ, RISK_WEIGHT_FATALITY_RATE, RISK_WEIGHT_EMS_DELAY)


def minmax(s: pd.Series) -> pd.Series:
    """data_pipeline.py 와 동일한 min-max (분모 +1e-9)."""
    s = pd.Series(s).astype(float)
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn + 1e-9)


def compute_score(
    df: pd.DataFrame,
    wa: float,
    wf: float,
    we: float,
    fatal_col: str = "fatality_rate",
    acc_transform: str = "raw",
) -> pd.Series:
    """가중합 위험지수. acc_transform='log1p' 면 사고건수 로그 변환."""
    acc = df["accident_count"]
    if acc_transform == "log1p":
        acc = np.log1p(acc)
    acc_n = minmax(acc)
    fat_n = minmax(df[fatal_col])
    # data_pipeline: minmax(ems_response_min + ems_distance_km)
    ems_n = minmax(df["ems_response_min"] + df["ems_distance_km"])
    return wa * acc_n + wf * fat_n + we * ems_n


def smoothed_fatality(df: pd.DataFrame, k: float) -> pd.Series:
    """소표본 사망률 보정 (empirical Bayes).

    fatal_smooth = (사망건수 + k*전국평균비율) / (사고건수 + k)
    사고 표본이 작은 시군구는 전국 평균 쪽으로 당겨진다.
    """
    total_death = df["fatality_count"].sum()
    total_acc = df["accident_count"].sum()
    global_rate = total_death / max(total_acc, 1)
    return (df["fatality_count"] + k * global_rate) / (df["accident_count"] + k)


def build_weight_scenarios() -> dict[str, tuple[float, float, float]]:
    """명시 시나리오 6개 + 격자 탐색(각 요소 0.10~0.80, step 0.05, 합=1)."""
    named = {
        "baseline_040_030_030": (0.40, 0.30, 0.30),
        "equal_033_033_033": (1 / 3, 1 / 3, 1 / 3),
        "accident_heavy_060_020_020": (0.60, 0.20, 0.20),
        "ems_heavy_025_025_050": (0.25, 0.25, 0.50),
        "fatal_heavy_025_050_025": (0.25, 0.50, 0.25),
        "conservative_045_020_035": (0.45, 0.20, 0.35),
    }
    grid: dict[str, tuple[float, float, float]] = {}
    vals = np.round(np.arange(0.10, 0.81, 0.05), 2)
    i = 0
    for wa in vals:
        for wf in vals:
            we = round(1.0 - wa - wf, 2)
            if 0.10 <= we <= 0.80:
                grid[f"grid_{i:03d}"] = (float(wa), float(wf), we)
                i += 1
    return {**named, **grid}


def find(df: pd.DataFrame, keyword: str) -> pd.Series:
    return df[df["sgg_name"].str.contains(keyword, na=False)].iloc[0]


def graded_distance_factor(dist_km: pd.Series) -> pd.Series:
    """거리 구간별 도로망 우회 보정 배수 (외진 곳일수록 우회율 높다는 가정).

    외부 평가가 제안한 유형별(산악/도서) 보정을, 유형 데이터 부재로 거리 구간
    proxy로 근사한다. **가정이며 정밀 추정이 아니다.**
      <5km ×1.0 / 5~15km ×1.3 / 15~30km ×1.6 / >=30km ×2.0
    """
    f = pd.Series(1.0, index=dist_km.index)
    f[dist_km >= 5] = 1.3
    f[dist_km >= 15] = 1.6
    f[dist_km >= 30] = 2.0
    return f


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(GRID_FEATURES_PATH).copy()
    n = len(df)

    # === 0. baseline 재현 검증 ===========================================
    base_score = compute_score(df, *BASE_W)
    max_diff = float((base_score - df["risk_index"]).abs().max())
    print(f"[검증] 가중합 재현 vs 저장된 risk_index 최대오차 = {max_diff:.2e}"
          f"  ({'OK' if max_diff < 1e-6 else 'MISMATCH!'})")

    # === 1. 가중치 민감도 ================================================
    weights = build_weight_scenarios()
    named_keys = [k for k in weights if not k.startswith("grid_")]
    rank_cols: list[str] = []
    for name, (wa, wf, we) in weights.items():
        sc = compute_score(df, wa, wf, we)
        col = f"rank_{name}"
        df[col] = sc.rank(ascending=False, method="min")
        rank_cols.append(col)

    summary = pd.DataFrame({
        "sgg_name": df["sgg_name"],
        "sgg_code": df["sgg_code"],
        "accident_count": df["accident_count"].astype(int),
        "fatality_count": df["fatality_count"].astype(int),
        "fatality_rate": df["fatality_rate"].round(4),
        "ems_distance_km": df["ems_distance_km"].round(2),
        "baseline_rank": df["rank_baseline_040_030_030"].astype(int),
        "rank_median": df[rank_cols].median(axis=1),
        "rank_best": df[rank_cols].min(axis=1).astype(int),
        "rank_worst": df[rank_cols].max(axis=1).astype(int),
        "rank_p90worst": df[rank_cols].quantile(0.90, axis=1),
        "top10_share": (df[rank_cols] <= 10).mean(axis=1).round(3),
        "top20_share": (df[rank_cols] <= 20).mean(axis=1).round(3),
    }).sort_values(["top10_share", "rank_median"], ascending=[False, True]).reset_index(drop=True)

    summary.to_csv(OUT_DIR / "weight_sensitivity_summary.csv", index=False, encoding="utf-8-sig")

    n_scen = len(weights)
    robust10 = summary[summary["top10_share"] >= 0.6]
    robust20 = summary[summary["top20_share"] >= 0.8]
    print(f"\n[가중치 시나리오] {n_scen}개 (명시 {len(named_keys)} + 격자 {n_scen - len(named_keys)})")
    print(f"[robust] top10_share>=0.6 : {len(robust10)}곳 / top20_share>=0.8 : {len(robust20)}곳")

    # 사고건수 하위인데 robust (= 진짜 응급 사각지대 후보)
    acc_median = df["accident_count"].median()
    low_acc_robust = robust20[robust20["accident_count"] <= acc_median]
    print(f"[핵심] 사고건수<=중앙값({acc_median:.0f}) & top20_share>=0.8 : {len(low_acc_robust)}곳")

    # === 2. 사망률 smoothing 민감도 (baseline 가중치 고정) ================
    ks = [0, 10, 20, 30]
    global_rate = df["fatality_count"].sum() / max(df["accident_count"].sum(), 1)
    print(f"\n[smoothing] 전국 평균 사망률 = {global_rate:.4f}")
    for k in ks:
        fcol = "fatality_rate" if k == 0 else f"_fsm{k}"
        if k != 0:
            df[fcol] = smoothed_fatality(df, k)
        sc = compute_score(df, *BASE_W, fatal_col=fcol)
        df[f"rank_smooth_k{k}"] = sc.rank(ascending=False, method="min").astype(int)
        df[f"score_smooth_k{k}"] = sc.round(4)

    smooth_cols = (["sgg_name", "accident_count", "fatality_count", "fatality_rate", "ems_distance_km"]
                   + [f"score_smooth_k{k}" for k in ks]
                   + [f"rank_smooth_k{k}" for k in ks])
    smooth_df = df[smooth_cols].sort_values("rank_smooth_k0").reset_index(drop=True)
    smooth_df.to_csv(OUT_DIR / "smoothing_effect.csv", index=False, encoding="utf-8-sig")

    # 인제/옹진 순위 변화 추적
    print("\n[smoothing 순위 변화]  k=0(현재) -> k=10 -> k=20 -> k=30")
    for kw in ["인제", "옹진"]:
        r = find(df, kw)
        ranks = " -> ".join(str(int(r[f"rank_smooth_k{k}"])) for k in ks)
        print(f"  {kw}: {ranks}  (사고 {int(r['accident_count'])}건, 사망 {int(r['fatality_count'])}, "
              f"사망률 {r['fatality_rate']:.3f}, ems {r['ems_distance_km']:.1f}km)")

    # 인제/옹진의 가중치 민감도 요약도 출력
    print("\n[가중치 민감도 - 인제/옹진/robust 상위]")
    print("  (열: baseline순위 / 중앙값 / 최선 / 최악 / top10비율 / top20비율)")
    show = pd.concat([
        summary[summary["sgg_name"].str.contains("인제|옹진", na=False)],
        summary.head(12),
    ]).drop_duplicates(subset="sgg_code")
    for _, r in show.iterrows():
        print(f"  code {r['sgg_code']} acc{int(r['accident_count']):>5} | "
              f"base{int(r['baseline_rank']):>3} med{r['rank_median']:>5.1f} "
              f"best{int(r['rank_best']):>3} worst{int(r['rank_worst']):>3} "
              f"t10={r['top10_share']:.2f} t20={r['top20_share']:.2f}")

    # === 3. 추가 강건성 점검 (후속 과제) ================================
    print("\n[추가 강건성 점검]")
    base_rank = compute_score(df, *BASE_W).rank(ascending=False, method="min")

    # 3a. 사고건수 log1p 정규화 (대도시 쏠림 완화)
    rank_log = compute_score(df, *BASE_W, acc_transform="log1p").rank(ascending=False, method="min")
    print("  [3a. 사고건수 log1p 정규화, baseline 가중치]")
    for kw in ["인제", "옹진"]:
        idx = df.index[df["sgg_name"].str.contains(kw, na=False)][0]
        print(f"    {kw}: raw {int(base_rank[idx])}위 -> log {int(rank_log[idx])}위")
    log_robust_nondaegu = df.loc[(rank_log <= 10), "sgg_name"].tolist()
    print(f"    log1p top10: {log_robust_nondaegu}")

    # 3b. 직선거리 균일 배수 -> min-max 순위 불변 입증
    print("  [3b. 직선거리 균일 배수 -> 최대 순위변화 (0이면 순위 불변)]")
    for fac in [1.3, 1.6, 2.0]:
        d2 = df.copy()
        d2["ems_distance_km"] = df["ems_distance_km"] * fac
        d2["ems_response_min"] = df["ems_response_min"] * fac
        r = compute_score(d2, *BASE_W).rank(ascending=False, method="min")
        print(f"    x{fac}: {int((r - base_rank).abs().max())}")

    # 3c. 거리 구간별 차등 보정 (외진 곳 우회 가중) -> robust 유지 확인
    fac = graded_distance_factor(df["ems_distance_km"])
    d3 = df.copy()
    d3["ems_distance_km"] = df["ems_distance_km"] * fac
    d3["ems_response_min"] = df["ems_response_min"] * fac
    rank_graded = compute_score(d3, *BASE_W).rank(ascending=False, method="min")
    print("  [3c. 거리 구간별 차등 보정, baseline 가중치]")
    for kw in ["인제", "옹진"]:
        idx = df.index[df["sgg_name"].str.contains(kw, na=False)][0]
        print(f"    {kw}: 직선 {int(base_rank[idx])}위 -> 보정 {int(rank_graded[idx])}위")
    print(f"    보정 후 top10: {df.loc[(rank_graded <= 10), 'sgg_name'].tolist()}")

    print(f"\n저장: {OUT_DIR / 'weight_sensitivity_summary.csv'}")
    print(f"저장: {OUT_DIR / 'smoothing_effect.csv'}")


if __name__ == "__main__":
    main()
