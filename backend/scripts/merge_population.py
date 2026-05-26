"""인구·고령 데이터 → grid_features 병합 (레버1·4 준비).

jumin.mois.go.kr "고령 인구현황"(또는 시군구 연령별 인구) CSV를 backend/data/raw/에
넣고 실행하면, 시군구명 매칭으로 grid_features에 total_pop·elderly_pop·elderly_ratio를
붙여 grid_features_demo.parquet를 만든다.

매칭은 data_pipeline의 시도→prefix + 시군구명 정규화 로직을 재사용한다(일반구·세종 포함).
실데이터 컬럼은 자동 탐지하며, 매칭/탐지 실패분을 콘솔에 리포트하니 확인 후 조정할 것.

실행:
  py -3.12 backend/scripts/merge_population.py [인구CSV경로]
  (경로 생략 시 raw 폴더에서 '고령/인구/연령' 키워드 파일 자동 탐색)
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import GRID_FEATURES_PATH, DATA_RAW, DATA_PROCESSED, SIDO_NAME_TO_PREFIX  # noqa: E402
from src.data_pipeline import _normalize_name, _map_taas_to_sgg_code  # noqa: E402

KNOWN = {"taas_다발지역.csv", "응급의료기관.csv", "119_구급통계.csv"}


def build_lookup(gf: pd.DataFrame) -> dict:
    """(시도 prefix, 정규화 시군구명) -> sgg_code. data_pipeline 매칭과 동형."""
    lookup = {}
    for _, r in gf.iterrows():
        prefix = str(r["sgg_code"])[:2]
        lookup[(prefix, _normalize_name(r["sgg_name"]))] = r["sgg_code"]
    return lookup


def find_pop_file(arg: str | None) -> Path | None:
    if arg:
        p = Path(arg)
        return p if p.exists() else None
    cands = [p for p in DATA_RAW.glob("*.csv") if p.name not in KNOWN]
    cands += list(DATA_RAW.glob("*.xlsx"))
    # 인구/고령/연령 키워드 우선
    for p in cands:
        if any(k in p.name for k in ["고령", "인구", "연령", "주민등록"]):
            return p
    return cands[0] if cands else None


def load_any(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    for enc in ["cp949", "utf-8-sig", "euc-kr", "utf-8"]:
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False, thousands=",")
        except (UnicodeDecodeError, ValueError):
            continue
    raise ValueError(f"read fail: {path}")


def detect_cols(df: pd.DataFrame):
    cols = [str(c) for c in df.columns]
    region = next((c for c in cols if "행정구역" in c or "시군구" in c or c.strip() == "지역"), None)
    # 총인구: '총인구' 포함 또는 '_전체'로 끝남(행안부 고령현황 포맷). 65/고령/남/여 미포함
    total = next((c for c in cols if ("총인구" in c or c.endswith("_전체"))
                  and "65" not in c and "고령" not in c and "남자" not in c and "여자" not in c), None)
    # 고령(65+) 수: '65세이상' or '고령인구', 비율·남/여 컬럼 제외
    elderly = next((c for c in cols if ("65세이상" in c or "고령인구" in c)
                    and "비율" not in c and "구성비" not in c and "남자" not in c and "여자" not in c), None)
    ratio = next((c for c in cols if ("고령" in c or "65" in c) and ("비율" in c or "구성비" in c)), None)
    return region, total, elderly, ratio


def parse_region(text: str) -> tuple[str, str]:
    """'서울특별시 종로구 (1111000000)' -> ('서울특별시', '종로구'). 코드 괄호 제거."""
    s = re.sub(r"\(.*?\)", "", str(text)).strip()
    parts = s.split()
    if len(parts) == 0:
        return ("", "")
    if len(parts) == 1:
        return (parts[0], "세종시" if "세종" in parts[0] else "")
    return (parts[0], " ".join(parts[1:]))


def main():
    gf = pd.read_parquet(GRID_FEATURES_PATH)
    gf["sgg_code"] = gf["sgg_code"].astype(str)
    lookup = build_lookup(gf)

    path = find_pop_file(sys.argv[1] if len(sys.argv) > 1 else None)
    if path is None:
        print("[대기] 인구 CSV를 backend/data/raw/에 넣고 다시 실행하세요.")
        print("       jumin.mois.go.kr > 고령 인구현황 > 전국/시군구/최근월 > CSV 다운로드")
        return
    print("인구 파일:", path.name)

    df = load_any(path)
    print("컬럼:", [str(c) for c in df.columns][:20])
    region, total, elderly, ratio = detect_cols(df)
    print(f"탐지 -> 지역={region} | 총인구={total} | 고령수={elderly} | 고령비율={ratio}")
    if region is None or (total is None and ratio is None):
        print("[조정 필요] 핵심 컬럼 미탐지. 위 컬럼 목록 보고 detect_cols() 수정.")
        return

    # 매칭
    recs = []
    miss = []
    for _, r in df.iterrows():
        sido, sgg = parse_region(r[region])
        code = _map_taas_to_sgg_code(sido, sgg, lookup, SIDO_NAME_TO_PREFIX)
        if code is None:
            if sgg:
                miss.append(f"{sido} {sgg}")
            continue
        rec = {"sgg_code": code}
        if total:
            rec["total_pop"] = pd.to_numeric(str(r[total]).replace(",", ""), errors="coerce")
        if elderly:
            rec["elderly_pop"] = pd.to_numeric(str(r[elderly]).replace(",", ""), errors="coerce")
        if ratio:
            rec["elderly_ratio_src"] = pd.to_numeric(re.sub(r"[^0-9.]", "", str(r[ratio])), errors="coerce")
        recs.append(rec)

    pop = pd.DataFrame(recs).dropna(subset=["sgg_code"]).groupby("sgg_code").first().reset_index()
    if "total_pop" in pop and "elderly_pop" in pop:
        pop["elderly_ratio"] = (pop["elderly_pop"] / pop["total_pop"] * 100).round(2)
    elif "elderly_ratio_src" in pop:
        pop["elderly_ratio"] = pop["elderly_ratio_src"].round(2)

    merged = gf.merge(pop, on="sgg_code", how="left")
    matched = merged["elderly_ratio"].notna().sum() if "elderly_ratio" in merged else 0
    print(f"\n매칭: grid 252개 중 {matched}개에 고령비율 부여. 인구측 미매칭 {len(set(miss))}개.")
    if miss:
        print("  미매칭 샘플:", sorted(set(miss))[:15])

    out_path = DATA_PROCESSED / "grid_features_demo.parquet"
    merged.to_parquet(out_path, index=False)
    print(f"저장: {out_path}")

    if "elderly_ratio" in merged:
        nat = merged["elderly_ratio"].median()
        print(f"\n전국 고령비율 중앙값: {nat:.1f}%")
        for kw in ["인제", "옹진"]:
            r = merged[merged["sgg_name"].str.contains(kw, na=False)]
            if len(r) and pd.notna(r.iloc[0].get("elderly_ratio")):
                print(f"  {r.iloc[0]['sgg_name']}: 고령비율 {r.iloc[0]['elderly_ratio']:.1f}%")


if __name__ == "__main__":
    main()
