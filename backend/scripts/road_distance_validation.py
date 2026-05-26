"""직선거리 vs OSRM 도로망 실거리 비교 검증.

배경: BlindZone의 ems_distance_km는 시군구 중심점→최근접 응급기관 직선거리다.
"직선거리라 부정확하다"는 비판에 대해, OpenStreetMap 도로망 라우팅(OSRM 공개
데모 서버, 무료·무키)으로 실제 자동차 도로거리·소요시간을 구해 우회율을 검증한다.

결과(2026-05-26, 핵심 시군구): 외진 사각지대일수록 우회율이 높다
(대도시 ~1.17x ↔ 옹진 2.01x). 즉 직선거리는 사각지대를 과소추정했고, 실거리로
보면 격차가 더 벌어진다 — robust 결론은 보수적이다. 자세히는
docs/submission/weight-sensitivity.md §6.1.

주의: OSRM 공개 데모 서버는 heavy use 금지. 전체 252개 호출은 throttle 필수이며,
본 스크립트는 기본적으로 핵심 시군구(targets)만 호출한다. 도서(옹진)는 육로
라우팅이라 실제 해상 이송시간은 더 길 수 있다.

실행: py -3.12 backend/scripts/road_distance_validation.py
"""
import sys, io, json, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"

# 1. 응급기관 좌표 + 시군구 중심별 최근접 응급기관
ems = pd.read_csv(RAW / "응급의료기관.csv", encoding="utf-8-sig", low_memory=False)
ems = ems.dropna(subset=["wgs84Lat", "wgs84Lon"])
ems_g = gpd.GeoDataFrame(
    ems, geometry=gpd.points_from_xy(ems["wgs84Lon"], ems["wgs84Lat"]), crs="EPSG:4326"
).to_crs("EPSG:5179")

gf = pd.read_parquet(PROC / "grid_features.parquet")
centers = gpd.GeoDataFrame(
    gf, geometry=gpd.points_from_xy(gf["lon"], gf["lat"]), crs="EPSG:4326"
).to_crs("EPSG:5179")

joined = centers.sjoin_nearest(ems_g, distance_col="_d")
# 중복 제거 (sgg당 1개)
joined = joined.drop_duplicates(subset=["sgg_code"])

namecol = next((c for c in ems.columns if "Name" in c or "name" in c or "기관" in c), None)
print("응급기관 이름 컬럼:", namecol)

def osrm(lon1, lat1, lon2, lat2):
    url = (f"http://router.project-osrm.org/route/v1/driving/"
           f"{lon1},{lat1};{lon2},{lat2}?overview=false")
    try:
        with urllib.request.urlopen(url, timeout=25) as r:
            d = json.load(r)
        if d.get("code") == "Ok":
            rt = d["routes"][0]
            return rt["distance"] / 1000, rt["duration"] / 60
        return None, d.get("code")
    except Exception as e:
        return None, f"{type(e).__name__}:{str(e)[:40]}"

targets = ["인제", "옹진", "송파", "달서", "양구", "정선"]
print(f"\n{'시군구':<8}{'직선km':>8}{'실거리km':>10}{'우회율':>8}{'실시간분':>9}  최근접응급기관")
for kw in targets:
    row = joined[joined["sgg_name"].str.contains(kw, na=False)]
    if not len(row):
        print(f"{kw}: 없음"); continue
    row = row.iloc[0]
    c_lon, c_lat = row["lon"], row["lat"]
    e_lon, e_lat = row["wgs84Lon"], row["wgs84Lat"]
    straight = row["ems_distance_km"]
    dist, dur = osrm(c_lon, c_lat, e_lon, e_lat)
    ename = str(row[namecol])[:20] if namecol else "?"
    if isinstance(dist, float):
        ratio = dist / straight if straight > 0 else 0
        print(f"{row['sgg_name']:<8}{straight:>8.1f}{dist:>10.1f}{ratio:>7.2f}x{dur:>8.1f}  {ename}")
    else:
        print(f"{row['sgg_name']:<8}{straight:>8.1f}{'FAIL':>10} ({dur})  {ename}")
    time.sleep(1.2)
