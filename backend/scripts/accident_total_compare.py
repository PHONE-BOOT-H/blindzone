"""다발지점 사고 vs 전체 교통사고 대조 (다발지점 한계 입증).

TAAS 다발지점 데이터(grid_features.accident_count)는 전체 사고가 아니라
'사고다발지점'만 집계한다. 한국도로교통공단 시군구별 전체 교통사고 통계
(경찰 집계 인적피해 사고)와 대조해, 인제·옹진이 "사고가 없는 곳"이 아니라
"사고가 분산돼 다발지점에 잡히지 않는 곳"임을 정량 입증한다.

실행: py -3.12 backend/scripts/accident_total_compare.py
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
SUB = ROOT.parent / "docs" / "submission"

# 시도 약칭 → grid sgg_code prefix (GeoJSON 자체 체계)
ABBR_PREFIX = {
    "서울": "11", "부산": "21", "대구": "22", "인천": "23", "광주": "24",
    "대전": "25", "울산": "26", "세종": "29", "경기": "31", "강원": "32",
    "충북": "33", "충남": "34", "전북": "35", "전남": "36", "경북": "37",
    "경남": "38", "제주": "39",
}


def norm(s):
    return re.sub(r"\s+", "", str(s).strip())


def main():
    tot = pd.read_csv(RAW / "taas_시군구별_전체사고통계_2024.csv", encoding="cp949")
    gf = pd.read_parquet(PROC / "grid_features.parquet")
    gf["sgg_code"] = gf["sgg_code"].astype(str)

    # grid lookup: (prefix, 정규화 시군구명) -> sgg_code
    lookup = {(str(r["sgg_code"])[:2], norm(r["sgg_name"])): r["sgg_code"]
              for _, r in gf.iterrows()}

    # 전체통계 매칭
    recs, miss = [], []
    for _, r in tot.iterrows():
        prefix = ABBR_PREFIX.get(str(r["시도"]).strip())
        if prefix is None:
            continue
        code = lookup.get((prefix, norm(r["시군구"])))
        if code is None:
            miss.append(f"{r['시도']} {r['시군구']}")
            continue
        recs.append({"sgg_code": code, "total_acc": int(r["사고건수"]),
                     "total_death": int(r["사망자수"])})
    td = pd.DataFrame(recs).groupby("sgg_code").sum().reset_index()
    m = gf.merge(td, on="sgg_code", how="left")
    matched = m["total_acc"].notna().sum()
    print(f"매칭: grid 252개 중 {matched}개에 전체사고 결합. 전체통계 미매칭 {len(set(miss))}개.")
    if miss:
        print("  미매칭 샘플:", sorted(set(miss))[:12])

    m["다발지점건수"] = m["accident_count"].astype(int)
    m["capture"] = m["다발지점건수"] / m["total_acc"]  # 다발지점 포착률

    print("\n[다발지점 사고 vs 전체 교통사고 — 인제·옹진]")
    for kw in ["인제", "옹진"]:
        r = m[m["sgg_name"].str.contains(kw, na=False)].iloc[0]
        print(f"  {r['sgg_name']}: 다발지점 {int(r['다발지점건수'])}건 / 전체 {int(r['total_acc'])}건 "
              f"(전체 사망 {int(r['total_death'])}명). 다발지점 포착률 {r['capture']*100:.1f}%")

    # robust 대도시와 대조
    summ = pd.read_csv(SUB / "weight_sensitivity_summary.csv", dtype={"sgg_code": str})
    rob = summ[summ["top10_share"] >= 0.6]
    mm = rob.merge(m[["sgg_code", "다발지점건수", "total_acc"]], on="sgg_code", how="left")
    print("\n[robust 8곳 — 다발지점 vs 전체]")
    print(f"  {'시군구':<8}{'다발':>6}{'전체':>7}{'포착률':>8}")
    for _, r in mm.iterrows():
        cap = r["다발지점건수"] / r["total_acc"] * 100 if r["total_acc"] else 0
        print(f"  {r['sgg_name']:<8}{int(r['다발지점건수']):>6}{int(r['total_acc']):>7}{cap:>7.1f}%")

    # 전국 분포 참고
    print(f"\n[참고] 전국 다발지점 포착률 중앙값 {m['capture'].median()*100:.1f}% "
          f"(다발지점은 전체 사고의 일부만 집계)")


if __name__ == "__main__":
    main()
