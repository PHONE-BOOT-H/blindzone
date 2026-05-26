"""전체 252 시군구 OSRM 도로 실거리 계산 → CSV 캐시.

각 시군구 중심점에서 최근접 응급기관(직선거리 기준)까지의 실제 자동차 도로거리·
소요시간을 OSRM 공개 데모 서버로 계산한다. reasonable use를 위해 요청 간 1.5초
throttle, 실패 시 직선거리 fallback. 결과는 한 번만 계산해 CSV로 캐시한다.

출력: docs/submission/road_distance_252.csv
실행: py -3.12 backend/scripts/build_road_distances.py
"""
import sys, io, json, time, urllib.request
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
OUT = ROOT.parent / "docs" / "submission" / "road_distance_252.csv"


def nearest_ems_coords() -> pd.DataFrame:
    ems = pd.read_csv(RAW / "응급의료기관.csv", encoding="utf-8-sig", low_memory=False)
    ems = ems.dropna(subset=["wgs84Lat", "wgs84Lon"])
    ems_g = gpd.GeoDataFrame(
        ems, geometry=gpd.points_from_xy(ems["wgs84Lon"], ems["wgs84Lat"]), crs="EPSG:4326"
    ).to_crs("EPSG:5179")
    gf = pd.read_parquet(PROC / "grid_features.parquet")
    centers = gpd.GeoDataFrame(
        gf, geometry=gpd.points_from_xy(gf["lon"], gf["lat"]), crs="EPSG:4326"
    ).to_crs("EPSG:5179")
    j = centers.sjoin_nearest(ems_g, distance_col="_d").drop_duplicates(subset=["sgg_code"])
    return j[["sgg_code", "sgg_name", "lon", "lat", "wgs84Lon", "wgs84Lat", "ems_distance_km"]]


def osrm(lon1, lat1, lon2, lat2):
    url = (f"http://router.project-osrm.org/route/v1/driving/"
           f"{lon1},{lat1};{lon2},{lat2}?overview=false")
    with urllib.request.urlopen(url, timeout=25) as r:
        d = json.load(r)
    if d.get("code") == "Ok":
        rt = d["routes"][0]
        return rt["distance"] / 1000, rt["duration"] / 60
    raise ValueError(d.get("code", "ERR"))


def main():
    df = nearest_ems_coords().reset_index(drop=True)
    rows = []
    fails = 0
    for i, r in df.iterrows():
        straight = float(r["ems_distance_km"])
        ok = True
        try:
            road_km, road_min = osrm(r["lon"], r["lat"], r["wgs84Lon"], r["wgs84Lat"])
        except Exception:
            road_km, road_min, ok = straight, straight, False  # fallback: 직선=실거리 가정
            fails += 1
        rows.append({
            "sgg_code": r["sgg_code"], "sgg_name": r["sgg_name"],
            "straight_km": round(straight, 2), "road_km": round(road_km, 2),
            "road_min": round(road_min, 1),
            "detour_ratio": round(road_km / straight, 3) if straight > 0 else 1.0,
            "osrm_ok": ok,
        })
        if (i + 1) % 30 == 0:
            print(f"  {i+1}/{len(df)} done (fails={fails})", flush=True)
        time.sleep(1.5)
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8-sig")
    print(f"\n저장: {OUT}  (총 {len(out)}, OSRM 실패 {fails})")
    ok = out[out["osrm_ok"]]
    print(f"우회율 중앙값(성공분): {ok['detour_ratio'].median():.2f}x  평균: {ok['detour_ratio'].mean():.2f}x")
    for kw in ["인제", "옹진"]:
        r = out[out["sgg_name"].str.contains(kw, na=False)]
        if len(r):
            r = r.iloc[0]
            print(f"  {r['sgg_name']}: 직선 {r['straight_km']} -> 도로 {r['road_km']}km "
                  f"({r['detour_ratio']}x, {r['road_min']}분, ok={r['osrm_ok']})")


if __name__ == "__main__":
    main()
