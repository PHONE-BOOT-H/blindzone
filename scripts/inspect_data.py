"""다운로드된 raw 데이터의 스키마·결측·좌표계를 빠르게 확인."""
from pathlib import Path
import sys

import pandas as pd
import geopandas as gpd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_RAW  # noqa: E402


def inspect_csv(path: Path, n: int = 3):
    print(f"\n--- {path.name} ---")
    try:
        df = pd.read_csv(path, encoding="cp949", low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    print(f"shape: {df.shape}")
    print(f"columns: {list(df.columns)[:15]}")
    print(f"null counts (top 5):\n{df.isnull().sum().sort_values(ascending=False).head()}")
    print(f"head({n}):\n{df.head(n)}")


def inspect_geojson(path: Path):
    print(f"\n--- {path.name} ---")
    gdf = gpd.read_file(path)
    print(f"shape: {gdf.shape}")
    print(f"crs: {gdf.crs}")
    print(f"columns: {list(gdf.columns)}")
    print(f"bounds: {gdf.total_bounds}")


def inspect_excel(path: Path):
    print(f"\n--- {path.name} ---")
    xls = pd.ExcelFile(path)
    print(f"sheets: {xls.sheet_names}")
    for sheet in xls.sheet_names[:3]:
        df = xls.parse(sheet)
        print(f"  [{sheet}] shape: {df.shape}, columns: {list(df.columns)[:8]}")


def main():
    files = list(DATA_RAW.iterdir())
    for f in sorted(files):
        if f.suffix == ".csv":
            inspect_csv(f)
        elif f.suffix in (".geojson", ".shp"):
            inspect_geojson(f)
        elif f.suffix in (".xlsx", ".xls"):
            inspect_excel(f)


if __name__ == "__main__":
    main()
