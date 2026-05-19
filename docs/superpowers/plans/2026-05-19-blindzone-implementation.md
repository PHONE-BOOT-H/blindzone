# BlindZone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 사고위험 × 응급사각지대 데이터를 융합해 잠재 위험지대를 발굴하고 응급자원 배치 시뮬레이션을 제공하는 Streamlit 웹앱(BlindZone)을 D-10 안에 시제품으로 완성한다.

**Architecture:** Python 단일 스택. 공공데이터 raw → 시군구 단위 피처 테이블(Parquet) → XGBoost 회귀 모델 + SHAP → Streamlit + Folium 인터랙티브 지도. 시민 모드(검색·설명) + 정책 시뮬레이터 모드(가상 응급기관 What-if). Streamlit Cloud 배포.

**Tech Stack:** Python 3.11+, pandas, geopandas, pyproj, scikit-learn, xgboost, shap, streamlit, streamlit-folium, folium, plotly, pyarrow, requests, pytest

---

## Spec Reference

`docs/superpowers/specs/2026-05-19-blindzone-design.md`

---

## File Structure

```
project-root/
├── app.py                              # Streamlit 진입점
├── requirements.txt                    # 의존성
├── README.md                           # 데모 안내
├── .gitignore                          # 이미 있음 (data/raw 제외)
│
├── src/
│   ├── __init__.py
│   ├── config.py                       # 경로·상수 (EPSG:5179 등)
│   ├── data_pipeline.py                # raw → processed
│   ├── train.py                        # XGBoost 학습 스크립트
│   ├── inference.py                    # 시뮬레이터 inference
│   ├── viz.py                          # Folium 지도 빌더
│   ├── shap_explain.py                 # SHAP 설명 로직
│   └── ui/
│       ├── __init__.py
│       ├── citizen.py                  # 시민 모드 view
│       ├── policy.py                   # 정책 시뮬레이터 view
│       └── about.py                    # About 페이지
│
├── tests/
│   ├── test_data_pipeline.py
│   ├── test_inference.py
│   └── test_viz.py
│
├── data/
│   ├── raw/                            # gitignore (다운로드 원본)
│   ├── processed/
│   │   └── grid_features.parquet       # 핵심 피처 테이블
│   └── sample/                         # 커밋용 소형 샘플
│
├── models/
│   └── xgb_risk_model.pkl              # 학습된 모델
│
├── scripts/
│   └── download_data.py                # 데이터 다운로드 일괄 스크립트
│
└── notebooks/
    └── 01_eda.ipynb                    # 탐색용 (옵션, 산출물 X)
```

---

## Testing Strategy

- **Unit tests (pytest):** 데이터 가공 함수, 좌표 변환, 거리 계산, 인터페이스 검증
- **Integration test:** 모델 학습 → 평가 메트릭이 임계값 통과 (예: R² > 0.3)
- **수동 검증:** Streamlit UI는 브라우저로 직접 확인
- **데이터 검증:** EDA 노트북에서 분포·결측·이상치 확인

---

## Phase 1: Environment Setup

### Task 1.1: Python 환경 + 의존성

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1.1.1: 작업 디렉토리에서 가상환경 생성**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Expected: `(.venv)` 프롬프트 prefix.

- [ ] **Step 1.1.2: `requirements.txt` 작성**

```
streamlit>=1.32.0
streamlit-folium>=0.18.0
folium>=0.16.0
pandas>=2.2.0
geopandas>=0.14.0
pyproj>=3.6.0
shapely>=2.0.0
numpy>=1.26.0
scikit-learn>=1.4.0
xgboost>=2.0.0
shap>=0.44.0
plotly>=5.19.0
pyarrow>=15.0.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=8.0.0
openpyxl>=3.1.0
```

- [ ] **Step 1.1.3: 의존성 설치**

```powershell
pip install -r requirements.txt
```

Expected: 모든 패키지 설치 완료 (geopandas는 GDAL 의존 → Windows에서 실패 시 conda 대안 안내).

- [ ] **Step 1.1.4: 커밋**

```powershell
git add requirements.txt
git commit -m "chore: requirements.txt 추가 — 핵심 의존성 명시"
```

### Task 1.2: 디렉토리 구조 + config

**Files:**
- Create: `src/__init__.py`, `src/config.py`, `src/ui/__init__.py`, `tests/__init__.py` (빈 파일)
- Create: `data/raw/.gitkeep`, `data/processed/.gitkeep`, `data/sample/.gitkeep`, `models/.gitkeep`, `scripts/.gitkeep`
- Create: `src/config.py`

- [ ] **Step 1.2.1: 디렉토리 + 빈 init 파일 일괄 생성**

```powershell
New-Item -ItemType Directory -Force -Path src, src/ui, tests, data/raw, data/processed, data/sample, models, scripts, notebooks
New-Item -ItemType File -Force -Path src/__init__.py, src/ui/__init__.py, tests/__init__.py, data/raw/.gitkeep, data/processed/.gitkeep, data/sample/.gitkeep, models/.gitkeep, scripts/.gitkeep
```

- [ ] **Step 1.2.2: `src/config.py` 작성**

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_SAMPLE = ROOT / "data" / "sample"
MODELS = ROOT / "models"

CRS_KOREA = "EPSG:5179"
CRS_WGS84 = "EPSG:4326"

GRID_FEATURES_PATH = DATA_PROCESSED / "grid_features.parquet"
MODEL_PATH = MODELS / "xgb_risk_model.pkl"

# 위험 지수 계산 가중치 (EDA 후 조정 가능)
RISK_WEIGHT_ACCIDENT_FREQ = 0.4
RISK_WEIGHT_FATALITY_RATE = 0.3
RISK_WEIGHT_EMS_DELAY = 0.3
```

- [ ] **Step 1.2.3: 커밋**

```powershell
git add src tests data models scripts notebooks
git commit -m "chore: 디렉토리 구조 + src/config.py 셋업"
```

### Task 1.3: Hello Streamlit (연결 검증)

**Files:**
- Create: `app.py`

- [ ] **Step 1.3.1: 최소 `app.py` 작성 (셋업 검증용)**

```python
import streamlit as st

st.set_page_config(page_title="BlindZone", page_icon=None, layout="wide")
st.title("BlindZone — 보이지 않던 위험지대")
st.write("환경 셋업 완료. 다음 단계: 데이터 수집.")
```

- [ ] **Step 1.3.2: 로컬 실행 + 브라우저 확인**

```powershell
streamlit run app.py
```

Expected: `http://localhost:8501`에서 타이틀과 메시지 표시. 정상 확인 후 Ctrl+C로 종료.

- [ ] **Step 1.3.3: 커밋**

```powershell
git add app.py
git commit -m "feat: 최소 Streamlit 진입점 추가 — 환경 검증용"
```

---

## Phase 2: Data Acquisition

### Task 2.1: 다운로드 스크립트 골격

**Files:**
- Create: `scripts/download_data.py`

- [ ] **Step 2.1.1: 다운로드 스크립트 작성 (URL 카탈로그 + 수동 안내 형식)**

```python
"""
공공데이터 다운로드 가이드 + 가능한 자동화.
대부분 공공데이터포털은 로그인/신청 필요 → 수동 다운로드 후 data/raw/에 배치.
파일명은 아래 SOURCES 딕셔너리에 명시된 대로 저장.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import DATA_RAW  # noqa: E402

SOURCES = {
    "taas_다발지역.csv": {
        "url": "https://www.data.go.kr/data/15029185/standard.do",
        "desc": "전국교통사고다발지역표준데이터 (좌표 포함)",
        "method": "manual",
    },
    "taas_다발지역_api.json": {
        "url": "https://www.data.go.kr/data/15057467/openapi.do",
        "desc": "한국도로교통공단_지자체별 교통사고 다발지역 (오픈 API)",
        "method": "api_optional",
    },
    "응급의료기관.csv": {
        "url": "https://www.data.go.kr/data/15096291/standard.do",
        "desc": "전국응급의료기관표준데이터",
        "method": "manual",
    },
    "119_구급통계연보.xlsx": {
        "url": "https://www.data.go.kr/data/15139158/fileData.do",
        "desc": "소방청_119구급서비스 통계연보 (시도·시군구 단위)",
        "method": "manual",
    },
    "시군구_경계.geojson": {
        "url": "https://sgis.kostat.go.kr/view/board/boardList?cur_menu_no=0001",
        "desc": "통계청 SGIS 시군구 행정경계 (대안: VWORLD)",
        "method": "manual",
    },
}


def main():
    print("=" * 70)
    print("BlindZone 데이터 다운로드 가이드")
    print("=" * 70)
    DATA_RAW.mkdir(parents=True, exist_ok=True)

    for filename, info in SOURCES.items():
        target = DATA_RAW / filename
        status = "OK" if target.exists() else "MISSING"
        print(f"\n[{status}] {filename}")
        print(f"  설명: {info['desc']}")
        print(f"  URL: {info['url']}")
        print(f"  방식: {info['method']}")
        print(f"  저장 경로: {target}")

    print("\n" + "=" * 70)
    print("수동 다운로드 후 다시 실행하면 [OK] 표시로 검증 가능.")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2.1.2: 실행 + 가이드 확인**

```powershell
python scripts/download_data.py
```

Expected: 5개 데이터셋이 모두 `[MISSING]`으로 표시되고 URL·저장 경로 안내.

- [ ] **Step 2.1.3: 커밋**

```powershell
git add scripts/download_data.py
git commit -m "feat: 데이터 다운로드 가이드 스크립트 — 5개 공공데이터 카탈로그"
```

### Task 2.2: 데이터 다운로드 (수동)

**Files:**
- Modify: `data/raw/` (5개 파일 추가)

- [ ] **Step 2.2.1: 한태영이 5개 URL 방문 → 다운로드 → `data/raw/`에 정확한 이름으로 저장**

각 URL에서:
1. 회원가입/로그인 (공공데이터포털 무료)
2. 파일 다운로드 (또는 미리보기 후 CSV/JSON 직접 받기)
3. `data/raw/` 폴더에 위 SOURCES dict 키 이름 그대로 저장

데이터 파일이 큰 경우 .gitignore가 이미 `data/raw/`를 제외하므로 git에 안 들어감 (정상).

- [ ] **Step 2.2.2: 다운로드 검증**

```powershell
python scripts/download_data.py
```

Expected: 5개 모두 `[OK]`.

만약 일부 데이터셋이 신청·승인 필요해서 즉시 못 받으면 다음 fallback 적용:
- TAAS 다발지역: 공공데이터포털 표준데이터는 즉시 다운 가능
- 응급의료기관: 즉시 다운 가능
- 119 통계연보: 즉시 다운 가능 (Excel)
- SGIS 시군구 경계: SGIS 또는 VWORLD에서 다운, 대안으로 `https://github.com/southkorea/southkorea-maps` 같은 GitHub repo의 GeoJSON 사용 가능

- [ ] **Step 2.2.3: 커밋 (raw는 gitignore이지만 다운로드 완료 시점 기록용 빈 commit)**

```powershell
git commit --allow-empty -m "data: raw 데이터 5종 다운로드 완료 (TAAS, 응급의료, 119, SGIS, 도로)"
```

### Task 2.3: 데이터 inspection 노트북

**Files:**
- Create: `notebooks/01_eda.ipynb` (수동, 또는 .py로 대체)
- 대안: Create `scripts/inspect_data.py`

- [ ] **Step 2.3.1: `scripts/inspect_data.py` 작성**

```python
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
```

- [ ] **Step 2.3.2: 실행 + 결과 확인**

```powershell
python scripts/inspect_data.py
```

Expected: 각 데이터셋의 shape·컬럼·결측이 콘솔에 출력. 인코딩 문제(cp949 vs utf-8) 자동 처리. 출력 결과를 보고 컬럼명·좌표 컬럼·시군구 컬럼 매핑 결정.

- [ ] **Step 2.3.3: 커밋**

```powershell
git add scripts/inspect_data.py
git commit -m "feat: raw 데이터 inspection 스크립트 — 스키마·결측·CRS 확인"
```

---

## Phase 3: Data Processing

### Task 3.1: 좌표·시군구 키 정규화 (가장 큰 함정 지점)

**Files:**
- Create: `src/data_pipeline.py`
- Create: `tests/test_data_pipeline.py`

- [ ] **Step 3.1.1: 실패하는 테스트 작성**

```python
# tests/test_data_pipeline.py
import pandas as pd
from src.data_pipeline import normalize_sgg_code, to_korean_crs


def test_normalize_sgg_code_pads_to_5_digits():
    assert normalize_sgg_code(1101) == "11010"
    assert normalize_sgg_code("11010") == "11010"
    assert normalize_sgg_code("11010.0") == "11010"


def test_to_korean_crs_converts_wgs84_to_5179():
    import geopandas as gpd
    from shapely.geometry import Point
    gdf = gpd.GeoDataFrame({"geometry": [Point(126.978, 37.566)]}, crs="EPSG:4326")
    result = to_korean_crs(gdf)
    assert result.crs.to_string() == "EPSG:5179"
    assert result.geometry.iloc[0].x > 900000  # 한국 좌표계 X 범위
```

- [ ] **Step 3.1.2: 테스트 실행 (실패 확인)**

```powershell
pytest tests/test_data_pipeline.py -v
```

Expected: FAIL — `normalize_sgg_code`, `to_korean_crs` 미정의.

- [ ] **Step 3.1.3: `src/data_pipeline.py` 초기 구현**

```python
"""raw 데이터 → 시군구 단위 피처 테이블."""
from __future__ import annotations

import geopandas as gpd
import pandas as pd

from src.config import CRS_KOREA


def normalize_sgg_code(code) -> str:
    """시군구코드를 5자리 zero-padded 문자열로 통일."""
    if pd.isna(code):
        return ""
    s = str(code).split(".")[0].strip()
    return s.zfill(5)


def to_korean_crs(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """좌표계를 EPSG:5179 (한국 측지계)로 변환."""
    if gdf.crs is None:
        gdf = gdf.set_crs("EPSG:4326")
    return gdf.to_crs(CRS_KOREA)
```

- [ ] **Step 3.1.4: 테스트 재실행 (통과 확인)**

```powershell
pytest tests/test_data_pipeline.py -v
```

Expected: PASS.

- [ ] **Step 3.1.5: 커밋**

```powershell
git add src/data_pipeline.py tests/test_data_pipeline.py
git commit -m "feat(data): 시군구코드 정규화 + EPSG:5179 변환 + 테스트"
```

### Task 3.2: 사고 데이터 집계 (시군구별)

**Files:**
- Modify: `src/data_pipeline.py`
- Modify: `tests/test_data_pipeline.py`

- [ ] **Step 3.2.1: 테스트 추가 — `aggregate_accidents_by_sgg`**

```python
# tests/test_data_pipeline.py 에 추가
def test_aggregate_accidents_groups_by_sgg():
    from src.data_pipeline import aggregate_accidents_by_sgg
    df = pd.DataFrame({
        "시군구코드": ["11010", "11010", "11020"],
        "사고건수": [10, 5, 3],
        "사망자수": [1, 0, 0],
        "부상자수": [12, 6, 4],
    })
    out = aggregate_accidents_by_sgg(df)
    assert len(out) == 2
    row_11010 = out[out["sgg_code"] == "11010"].iloc[0]
    assert row_11010["accident_count"] == 15
    assert row_11010["fatality_count"] == 1
    assert row_11010["fatality_rate"] == 1 / 15
```

- [ ] **Step 3.2.2: 테스트 실행 (실패)**

```powershell
pytest tests/test_data_pipeline.py::test_aggregate_accidents_groups_by_sgg -v
```

Expected: FAIL.

- [ ] **Step 3.2.3: 구현 추가**

```python
# src/data_pipeline.py 에 추가
def aggregate_accidents_by_sgg(df: pd.DataFrame) -> pd.DataFrame:
    """사고 raw 데이터를 시군구별로 집계.

    입력 컬럼 가정: 시군구코드, 사고건수, 사망자수, 부상자수.
    실제 TAAS 컬럼명이 다르면 호출 전 rename으로 맞춤.
    """
    df = df.copy()
    df["시군구코드"] = df["시군구코드"].apply(normalize_sgg_code)
    grouped = (
        df.groupby("시군구코드")
        .agg(
            accident_count=("사고건수", "sum"),
            fatality_count=("사망자수", "sum"),
            injury_count=("부상자수", "sum"),
        )
        .reset_index()
        .rename(columns={"시군구코드": "sgg_code"})
    )
    grouped["fatality_rate"] = grouped["fatality_count"] / grouped["accident_count"]
    grouped["fatality_rate"] = grouped["fatality_rate"].fillna(0)
    return grouped
```

- [ ] **Step 3.2.4: 테스트 PASS 확인**

```powershell
pytest tests/test_data_pipeline.py -v
```

- [ ] **Step 3.2.5: 커밋**

```powershell
git add src/data_pipeline.py tests/test_data_pipeline.py
git commit -m "feat(data): 사고 데이터 시군구별 집계 함수 + 테스트"
```

### Task 3.3: 응급의료기관 거리 계산 (시군구 중심 → 가장 가까운 응급기관)

**Files:**
- Modify: `src/data_pipeline.py`
- Modify: `tests/test_data_pipeline.py`

- [ ] **Step 3.3.1: 테스트 추가**

```python
def test_nearest_ems_distance_returns_km():
    import geopandas as gpd
    from shapely.geometry import Point
    from src.data_pipeline import nearest_ems_distance_km

    sgg_centers = gpd.GeoDataFrame(
        {"sgg_code": ["11010"], "geometry": [Point(953000, 1953000)]},
        crs="EPSG:5179",
    )
    ems = gpd.GeoDataFrame(
        {"name": ["A응급실"], "geometry": [Point(963000, 1953000)]},
        crs="EPSG:5179",
    )
    out = nearest_ems_distance_km(sgg_centers, ems)
    assert "ems_distance_km" in out.columns
    assert abs(out["ems_distance_km"].iloc[0] - 10.0) < 0.01
```

- [ ] **Step 3.3.2: 테스트 실행 (실패)**

```powershell
pytest tests/test_data_pipeline.py::test_nearest_ems_distance_returns_km -v
```

- [ ] **Step 3.3.3: 구현 추가**

```python
def nearest_ems_distance_km(
    sgg_centers: gpd.GeoDataFrame, ems: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """각 시군구 중심점에서 가장 가까운 응급의료기관까지 거리(km)."""
    if sgg_centers.crs.to_string() != CRS_KOREA:
        sgg_centers = sgg_centers.to_crs(CRS_KOREA)
    if ems.crs is None or ems.crs.to_string() != CRS_KOREA:
        ems = ems.to_crs(CRS_KOREA) if ems.crs else ems.set_crs("EPSG:4326").to_crs(CRS_KOREA)

    joined = sgg_centers.sjoin_nearest(ems, distance_col="_dist_m")
    joined["ems_distance_km"] = joined["_dist_m"] / 1000.0
    return joined[["sgg_code", "geometry", "ems_distance_km"]].drop_duplicates(subset=["sgg_code"])
```

- [ ] **Step 3.3.4: 테스트 PASS 확인 + 커밋**

```powershell
pytest tests/test_data_pipeline.py -v
git add src/data_pipeline.py tests/test_data_pipeline.py
git commit -m "feat(data): 시군구별 최근접 응급의료기관 거리 계산 + 테스트"
```

### Task 3.4: 119 평균 출동시간 매핑

**Files:**
- Modify: `src/data_pipeline.py`

- [ ] **Step 3.4.1: 119 통계연보 Excel을 파싱해서 시군구별 평균 출동시간 추출하는 함수**

```python
def load_ems_response_time(xlsx_path) -> pd.DataFrame:
    """119 통계연보에서 시군구별 평균 출동시간(분) 추출.

    실제 시트 구조는 inspect_data.py 결과로 확인 후 컬럼명 맞춤.
    여기서는 가장 표준적인 구조 가정: '시도' '시군구' '평균출동시간'.
    """
    df = pd.read_excel(xlsx_path, sheet_name=0)
    df.columns = [c.strip() for c in df.columns]
    rename_map = {}
    for c in df.columns:
        if "시군구" in c and "코드" in c:
            rename_map[c] = "sgg_code"
        elif "평균" in c and ("출동" in c or "도착" in c):
            rename_map[c] = "ems_response_min"
    df = df.rename(columns=rename_map)
    if "sgg_code" not in df.columns or "ems_response_min" not in df.columns:
        raise ValueError(
            f"119 데이터 컬럼 매핑 실패. 실제 컬럼: {list(df.columns)}. "
            "inspect_data.py 출력을 보고 rename_map 조정 필요."
        )
    df["sgg_code"] = df["sgg_code"].apply(normalize_sgg_code)
    df["ems_response_min"] = pd.to_numeric(df["ems_response_min"], errors="coerce")
    return df[["sgg_code", "ems_response_min"]].dropna()
```

- [ ] **Step 3.4.2: 통합 검증을 위한 작은 테스트 (Mock 데이터)**

```python
def test_load_ems_response_time_via_mock(tmp_path):
    import pandas as pd
    from src.data_pipeline import load_ems_response_time
    p = tmp_path / "mock.xlsx"
    pd.DataFrame(
        {"시군구코드": [11010, 11020], "평균출동시간(분)": [7.5, 9.2]}
    ).to_excel(p, index=False)
    out = load_ems_response_time(p)
    assert set(out.columns) == {"sgg_code", "ems_response_min"}
    assert out.loc[out["sgg_code"] == "11010", "ems_response_min"].iloc[0] == 7.5
```

- [ ] **Step 3.4.3: 실행 + 통과 + 커밋**

```powershell
pytest tests/test_data_pipeline.py -v
git add src/data_pipeline.py tests/test_data_pipeline.py
git commit -m "feat(data): 119 통계연보에서 시군구별 평균 출동시간 추출 + 테스트"
```

### Task 3.5: 시군구 중심점 + 면적 + 도로 길이 (선택, 시간 되면)

**Files:**
- Modify: `src/data_pipeline.py`

- [ ] **Step 3.5.1: SGIS 시군구 GeoJSON에서 시군구 중심점·면적 추출**

```python
def load_sgg_centers(geojson_path) -> gpd.GeoDataFrame:
    """시군구 폴리곤 → 중심점 + 면적(km^2)."""
    gdf = gpd.read_file(geojson_path)
    # SGIS 표준 컬럼: SIG_CD (시군구코드), SIG_KOR_NM
    code_col = next((c for c in gdf.columns if "SIG_CD" in c.upper() or "시군구코드" in c), None)
    name_col = next((c for c in gdf.columns if "KOR_NM" in c.upper() or "시군구명" in c), None)
    if code_col is None:
        raise ValueError(f"시군구코드 컬럼 못 찾음. columns: {list(gdf.columns)}")
    gdf = gdf.rename(columns={code_col: "sgg_code", name_col: "sgg_name"})
    gdf["sgg_code"] = gdf["sgg_code"].apply(normalize_sgg_code)
    gdf = to_korean_crs(gdf)
    gdf["area_km2"] = gdf.geometry.area / 1_000_000
    gdf["centroid"] = gdf.geometry.centroid
    centers = gdf[["sgg_code", "sgg_name", "area_km2", "centroid"]].rename(
        columns={"centroid": "geometry"}
    )
    return gpd.GeoDataFrame(centers, geometry="geometry", crs=CRS_KOREA)
```

- [ ] **Step 3.5.2: 커밋 (테스트는 실제 GeoJSON 의존이라 통합 테스트로 다음 단계 합치기)**

```powershell
git add src/data_pipeline.py
git commit -m "feat(data): 시군구 GeoJSON → 중심점·면적 추출 함수"
```

### Task 3.6: 통합 파이프라인 (raw → grid_features.parquet)

**Files:**
- Modify: `src/data_pipeline.py`
- Create: `scripts/build_features.py`

- [ ] **Step 3.6.1: 통합 함수 작성**

```python
# src/data_pipeline.py 에 추가
def build_grid_features(
    accidents_csv,
    ems_csv,
    ems_response_xlsx,
    sgg_geojson,
) -> pd.DataFrame:
    """모든 raw를 합쳐서 시군구 단위 피처 테이블 생성."""
    # 1. 사고 집계
    accidents_raw = pd.read_csv(accidents_csv, encoding="cp949", low_memory=False)
    accidents = aggregate_accidents_by_sgg(accidents_raw)

    # 2. 시군구 중심·면적
    centers = load_sgg_centers(sgg_geojson)

    # 3. 응급의료기관 거리
    ems = gpd.read_file(ems_csv) if str(ems_csv).endswith((".geojson", ".shp")) else None
    if ems is None:
        # CSV에 위도·경도 컬럼이 있는 경우
        df_ems = pd.read_csv(ems_csv, encoding="cp949", low_memory=False)
        lat_col = next(c for c in df_ems.columns if "위도" in c or "lat" in c.lower())
        lon_col = next(c for c in df_ems.columns if "경도" in c or "lon" in c.lower())
        ems = gpd.GeoDataFrame(
            df_ems,
            geometry=gpd.points_from_xy(df_ems[lon_col], df_ems[lat_col]),
            crs="EPSG:4326",
        )
    ems_dist = nearest_ems_distance_km(centers, ems)

    # 4. 119 평균 출동시간
    ems_resp = load_ems_response_time(ems_response_xlsx)

    # 5. 병합
    features = (
        centers.merge(accidents, on="sgg_code", how="left")
        .merge(ems_dist[["sgg_code", "ems_distance_km"]], on="sgg_code", how="left")
        .merge(ems_resp, on="sgg_code", how="left")
    )
    # 결측 보정
    features["accident_count"] = features["accident_count"].fillna(0)
    features["fatality_count"] = features["fatality_count"].fillna(0)
    features["fatality_rate"] = features["fatality_rate"].fillna(0)
    features["ems_response_min"] = features["ems_response_min"].fillna(
        features["ems_response_min"].median()
    )
    features["ems_distance_km"] = features["ems_distance_km"].fillna(
        features["ems_distance_km"].median()
    )
    # 위경도 컬럼 추가 (지도용)
    features_wgs = features.to_crs("EPSG:4326")
    features["lon"] = features_wgs.geometry.x
    features["lat"] = features_wgs.geometry.y

    # 잠재 위험 지수 (가중합)
    from src.config import (
        RISK_WEIGHT_ACCIDENT_FREQ,
        RISK_WEIGHT_FATALITY_RATE,
        RISK_WEIGHT_EMS_DELAY,
    )
    # 정규화(min-max)
    def mm(s):
        return (s - s.min()) / (s.max() - s.min() + 1e-9)

    features["risk_index"] = (
        RISK_WEIGHT_ACCIDENT_FREQ * mm(features["accident_count"])
        + RISK_WEIGHT_FATALITY_RATE * mm(features["fatality_rate"])
        + RISK_WEIGHT_EMS_DELAY * mm(features["ems_response_min"] + features["ems_distance_km"])
    )
    return pd.DataFrame(features.drop(columns=["geometry"]))
```

- [ ] **Step 3.6.2: 빌드 스크립트 작성**

```python
# scripts/build_features.py
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data_pipeline import build_grid_features  # noqa: E402
from src.config import DATA_RAW, GRID_FEATURES_PATH  # noqa: E402


def main():
    features = build_grid_features(
        accidents_csv=DATA_RAW / "taas_다발지역.csv",
        ems_csv=DATA_RAW / "응급의료기관.csv",
        ems_response_xlsx=DATA_RAW / "119_구급통계연보.xlsx",
        sgg_geojson=DATA_RAW / "시군구_경계.geojson",
    )
    GRID_FEATURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(GRID_FEATURES_PATH, index=False)
    print(f"saved: {GRID_FEATURES_PATH} ({len(features)} rows)")
    print(features.describe())


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.6.3: 실행 + 결과 확인**

```powershell
python scripts/build_features.py
```

Expected: `data/processed/grid_features.parquet` 생성. ~250 rows (전국 시군구). 통계 출력에서 risk_index 분포 확인.

만약 컬럼명 매핑 실패하면 `scripts/inspect_data.py` 출력으로 돌아가 `aggregate_accidents_by_sgg`나 `load_ems_response_time`의 컬럼 매핑 조정 후 재시도.

- [ ] **Step 3.6.4: 커밋**

```powershell
git add src/data_pipeline.py scripts/build_features.py
git commit -m "feat(data): 통합 파이프라인 — raw → grid_features.parquet 빌드"
```

### Task 3.7: 인사이트 강도 검증 (시군구 vs 격자 결정)

**Files:**
- Create: `scripts/check_insight.py`

- [ ] **Step 3.7.1: 검증 스크립트 작성**

```python
"""V1 시군구 단위 인사이트가 충분히 강한지 확인.

핵심 질문: '사고는 평균인데 응급은 늦은' 시군구가 통계적으로 의미 있게 존재하나?
존재하면 시군구 V1 OK. 약하면 1km 격자로 전환 (V1.1 앞당김).
"""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import GRID_FEATURES_PATH  # noqa: E402


def main():
    df = pd.read_parquet(GRID_FEATURES_PATH)
    print(f"총 시군구: {len(df)}")
    print(f"\nrisk_index 분포:\n{df['risk_index'].describe()}")

    # '평균 사고 수준이지만 응급 사각'인 그룹
    median_acc = df["accident_count"].median()
    p75_ems = df["ems_response_min"].quantile(0.75)
    blind_zone = df[
        (df["accident_count"].between(median_acc * 0.5, median_acc * 1.5))
        & (df["ems_response_min"] >= p75_ems)
    ]
    print(f"\n'사고는 평균인데 응급 늦은' 시군구: {len(blind_zone)}개")
    print(blind_zone[["sgg_name", "sgg_code", "accident_count", "ems_response_min", "risk_index"]].head(15))

    # 판정
    if len(blind_zone) >= 10:
        print("\n→ V1 시군구 단위 OK (발견 임팩트 충분)")
    else:
        print("\n→ 시군구 단위 인사이트 약함. V1.1 격자 전환 권장.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3.7.2: 실행 + 판정**

```powershell
python scripts/check_insight.py
```

Expected: blind_zone 후보 시군구 리스트와 V1 OK / 전환 권장 판정.

판정이 "전환 권장"이면 한태영과 상의 — 1km 격자 작업 추가 결정 (시간 부담 vs 임팩트 trade-off).

- [ ] **Step 3.7.3: 커밋**

```powershell
git add scripts/check_insight.py
git commit -m "feat(data): 시군구 단위 인사이트 강도 검증 스크립트"
```

---

## Phase 4: Model Training

### Task 4.1: XGBoost 학습 + 평가

**Files:**
- Create: `src/train.py`
- Create: `tests/test_train.py`

- [ ] **Step 4.1.1: 학습 모듈 작성**

```python
# src/train.py
"""XGBoost 회귀로 risk_index를 예측하는 모델 학습."""
from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

from src.config import GRID_FEATURES_PATH, MODEL_PATH

FEATURE_COLS = [
    "accident_count",
    "fatality_count",
    "fatality_rate",
    "injury_count",
    "ems_distance_km",
    "ems_response_min",
    "area_km2",
]
TARGET_COL = "risk_index"


def load_dataset(path: Path = GRID_FEATURES_PATH):
    df = pd.read_parquet(path)
    X = df[FEATURE_COLS].fillna(0)
    y = df[TARGET_COL]
    return X, y, df


def train_and_save(model_path: Path = MODEL_PATH):
    X, y, _ = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    metrics = {
        "r2": r2_score(y_test, preds),
        "mae": mean_absolute_error(y_test, preds),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump({"model": model, "feature_cols": FEATURE_COLS, "metrics": metrics}, f)
    print(f"saved: {model_path}")
    print(f"metrics: {metrics}")
    return metrics


if __name__ == "__main__":
    train_and_save()
```

- [ ] **Step 4.1.2: 통합 테스트 (학습 → 메트릭 임계값)**

```python
# tests/test_train.py
from src.train import train_and_save


def test_training_produces_reasonable_metrics():
    metrics = train_and_save()
    assert metrics["r2"] > 0.5  # risk_index는 동일 피처 가중합 정의라 높은 R2 기대
    assert metrics["mae"] < 0.1
```

- [ ] **Step 4.1.3: 학습 실행 + 테스트**

```powershell
python -m src.train
pytest tests/test_train.py -v
```

Expected: 모델이 `models/xgb_risk_model.pkl`로 저장, R²/MAE 출력, 테스트 PASS.

**주의:** risk_index가 피처들의 가중합으로 정의되어 있어서 학습 모델이 거의 그 가중합을 재현 → R² 매우 높음. 이는 의도된 것 (모델은 SHAP 해석·시뮬레이션용 wrapper). 발표 시 "위험 지수는 가중합 공식, 모델은 해석·What-if 도구"로 명시.

- [ ] **Step 4.1.4: 커밋**

```powershell
git add src/train.py tests/test_train.py
git commit -m "feat(model): XGBoost 회귀 학습 + 평가 + 테스트"
```

### Task 4.2: SHAP 설명 모듈

**Files:**
- Create: `src/shap_explain.py`

- [ ] **Step 4.2.1: SHAP 모듈 작성**

```python
# src/shap_explain.py
from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import shap

from src.config import MODEL_PATH
from src.train import FEATURE_COLS


def load_model(path: Path = MODEL_PATH):
    with open(path, "rb") as f:
        bundle = pickle.load(f)
    return bundle["model"], bundle.get("feature_cols", FEATURE_COLS)


def explain_one(features_row: pd.Series, top_n: int = 3) -> list[dict]:
    """단일 시군구에 대한 상위 N개 기여 피처 추출."""
    model, cols = load_model()
    X = features_row[cols].to_frame().T.fillna(0)
    explainer = shap.TreeExplainer(model)
    shap_vals = explainer.shap_values(X)[0]
    pairs = sorted(zip(cols, shap_vals), key=lambda kv: abs(kv[1]), reverse=True)
    feature_label = {
        "accident_count": "사고 빈도",
        "fatality_count": "사망사고 수",
        "fatality_rate": "사망사고 비율",
        "injury_count": "부상자 수",
        "ems_distance_km": "응급기관까지 거리",
        "ems_response_min": "평균 출동시간",
        "area_km2": "면적",
    }
    return [
        {
            "feature": feature_label.get(name, name),
            "shap_value": float(val),
            "direction": "위험 증가" if val > 0 else "위험 감소",
        }
        for name, val in pairs[:top_n]
    ]
```

- [ ] **Step 4.2.2: 빠른 검증 — 인터프리터에서 한 시군구 explain 호출**

```powershell
python -c "import pandas as pd; from src.shap_explain import explain_one; from src.config import GRID_FEATURES_PATH; df = pd.read_parquet(GRID_FEATURES_PATH); print(explain_one(df.iloc[0]))"
```

Expected: 3개 피처(이름·shap_value·방향) 리스트 출력.

- [ ] **Step 4.2.3: 커밋**

```powershell
git add src/shap_explain.py
git commit -m "feat(model): SHAP 단일 시군구 설명 모듈"
```

### Task 4.3: 시뮬레이션 inference

**Files:**
- Create: `src/inference.py`

- [ ] **Step 4.3.1: inference 모듈 작성**

```python
# src/inference.py
"""가상 응급기관 추가 시 영향 시뮬레이션."""
from __future__ import annotations

import pickle

import numpy as np
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

from src.config import CRS_KOREA, MODEL_PATH, GRID_FEATURES_PATH


def simulate_new_ems(virtual_ems_lonlat: list[tuple[float, float]]) -> pd.DataFrame:
    """가상 응급기관 좌표들을 추가했을 때 각 시군구의 ems_distance_km 재계산 + risk_index 재예측.

    Args:
        virtual_ems_lonlat: [(lon, lat), ...] WGS84 좌표
    Returns:
        DataFrame: 시군구별 before/after risk_index
    """
    features = pd.read_parquet(GRID_FEATURES_PATH)
    centers = gpd.GeoDataFrame(
        features,
        geometry=gpd.points_from_xy(features["lon"], features["lat"]),
        crs="EPSG:4326",
    ).to_crs(CRS_KOREA)

    if not virtual_ems_lonlat:
        return features.assign(risk_index_new=features["risk_index"])

    v_ems = gpd.GeoDataFrame(
        geometry=[Point(lon, lat) for lon, lat in virtual_ems_lonlat],
        crs="EPSG:4326",
    ).to_crs(CRS_KOREA)

    # 기존 ems_distance_km와 가상 ems까지 거리 중 최소값
    centers_with_v = centers.sjoin_nearest(v_ems, distance_col="_v_dist_m")
    centers_with_v["v_dist_km"] = centers_with_v["_v_dist_m"] / 1000.0
    new_dist = np.minimum(
        centers_with_v["ems_distance_km"].values,
        centers_with_v["v_dist_km"].values,
    )

    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
    model = bundle["model"]
    cols = bundle["feature_cols"]

    X_new = features[cols].copy().fillna(0)
    X_new["ems_distance_km"] = new_dist
    risk_new = model.predict(X_new)

    result = features.copy()
    result["risk_index_new"] = risk_new
    result["risk_delta"] = result["risk_index_new"] - result["risk_index"]
    result["ems_distance_km_new"] = new_dist
    return result
```

- [ ] **Step 4.3.2: 간단 동작 검증**

```powershell
python -c "from src.inference import simulate_new_ems; r = simulate_new_ems([(127.0, 37.5)]); print(r[['sgg_name', 'risk_index', 'risk_index_new', 'risk_delta']].sort_values('risk_delta').head(10))"
```

Expected: 위치 (127.0, 37.5) 근처 시군구들의 risk_delta가 음수 (위험 감소).

- [ ] **Step 4.3.3: 커밋**

```powershell
git add src/inference.py
git commit -m "feat(model): 가상 응급기관 추가 시뮬레이션 inference 모듈"
```

---

## Phase 5: Streamlit UI — Citizen Mode

### Task 5.1: 메인 진입점 + 모드 토글

**Files:**
- Modify: `app.py`
- Create: `src/ui/citizen.py` (빈 stub)
- Create: `src/ui/policy.py` (빈 stub)
- Create: `src/ui/about.py` (빈 stub)

- [ ] **Step 5.1.1: 메인 `app.py` 본격 작성**

```python
import streamlit as st
import pandas as pd

from src.config import GRID_FEATURES_PATH
from src.ui import citizen, policy, about

st.set_page_config(page_title="BlindZone — 보이지 않던 위험지대", layout="wide")


@st.cache_data
def load_features():
    return pd.read_parquet(GRID_FEATURES_PATH)


features = load_features()

st.sidebar.title("BlindZone")
mode = st.sidebar.radio(
    "모드",
    ["시민 모드", "정책 시뮬레이터", "About"],
    label_visibility="collapsed",
)

if mode == "시민 모드":
    citizen.render(features)
elif mode == "정책 시뮬레이터":
    policy.render(features)
else:
    about.render()
```

- [ ] **Step 5.1.2: stub 파일들 빈 render 함수로 생성**

```python
# src/ui/citizen.py
import streamlit as st
def render(features):
    st.title("시민 모드")
    st.write("(작성 예정)")

# src/ui/policy.py
import streamlit as st
def render(features):
    st.title("정책 시뮬레이터")
    st.write("(작성 예정)")

# src/ui/about.py
import streamlit as st
def render():
    st.title("About")
    st.write("(작성 예정)")
```

- [ ] **Step 5.1.3: 동작 확인**

```powershell
streamlit run app.py
```

Expected: 사이드바에서 모드 전환되고 각 모드의 stub 표시.

- [ ] **Step 5.1.4: 커밋**

```powershell
git add app.py src/ui/
git commit -m "feat(ui): Streamlit 진입점 + 모드 라우팅 (시민/정책/About)"
```

### Task 5.2: 시민 모드 — 검색 + 통계 카드

**Files:**
- Modify: `src/ui/citizen.py`

- [ ] **Step 5.2.1: 검색 + 메트릭 카드 추가**

```python
# src/ui/citizen.py
import streamlit as st
import pandas as pd

from src.shap_explain import explain_one


def render(features: pd.DataFrame):
    st.title("우리 동네 응급 사각지대 확인")
    st.caption("사고는 적은데 죽음은 많은 곳 — 데이터로 발굴한 잠재 위험지대")

    left, right = st.columns([1, 2])

    with left:
        st.subheader("지역 검색")
        sgg_name = st.selectbox(
            "시군구 선택",
            sorted(features["sgg_name"].dropna().unique()),
            index=None,
            placeholder="시군구를 검색·선택하세요",
        )

        if sgg_name:
            row = features[features["sgg_name"] == sgg_name].iloc[0]
            st.metric("잠재 위험 지수", f"{row['risk_index']:.3f}")
            st.metric("연간 사고 건수", f"{int(row['accident_count'])}건")
            st.metric("평균 응급 도착시간", f"{row['ems_response_min']:.1f}분")
            st.metric("가장 가까운 응급기관 거리", f"{row['ems_distance_km']:.1f} km")

            st.subheader("왜 위험한가")
            try:
                explanations = explain_one(row)
                for e in explanations:
                    arrow = "↑" if e["shap_value"] > 0 else "↓"
                    st.write(f"- **{e['feature']}** {arrow} (영향도 {e['shap_value']:+.3f})")
            except Exception as ex:
                st.warning(f"SHAP 설명 로드 실패: {ex}")

    with right:
        st.subheader("전국 위험지도")
        st.write("(지도는 다음 단계에서 추가)")
```

- [ ] **Step 5.2.2: 브라우저 확인**

```powershell
streamlit run app.py
```

Expected: 시군구 선택 시 메트릭 4개 + SHAP 상위 3개 피처 표시.

- [ ] **Step 5.2.3: 커밋**

```powershell
git add src/ui/citizen.py
git commit -m "feat(ui): 시민 모드 검색 + 메트릭 카드 + SHAP 설명"
```

### Task 5.3: 시민 모드 — Folium 지도

**Files:**
- Modify: `src/ui/citizen.py`
- Create: `src/viz.py`

- [ ] **Step 5.3.1: 지도 빌더 모듈 작성**

```python
# src/viz.py
import folium
import pandas as pd

KOREA_CENTER = [36.5, 127.8]


def build_risk_map(features: pd.DataFrame, selected_sgg: str | None = None) -> folium.Map:
    m = folium.Map(location=KOREA_CENTER, zoom_start=7, tiles="cartodbpositron")

    qmin, qmax = features["risk_index"].quantile([0.05, 0.95])

    def color(val):
        if pd.isna(val):
            return "#cccccc"
        norm = (val - qmin) / (qmax - qmin + 1e-9)
        norm = max(0.0, min(1.0, norm))
        # 위험 높을수록 진한 빨강
        r = int(255 * norm)
        g = int(200 * (1 - norm))
        return f"#{r:02x}{g:02x}40"

    for _, row in features.iterrows():
        is_selected = selected_sgg and row["sgg_name"] == selected_sgg
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=12 if is_selected else 5,
            color="#000000" if is_selected else color(row["risk_index"]),
            weight=2 if is_selected else 1,
            fill=True,
            fill_color=color(row["risk_index"]),
            fill_opacity=0.7,
            tooltip=(
                f"<b>{row['sgg_name']}</b><br>"
                f"위험지수: {row['risk_index']:.3f}<br>"
                f"사고: {int(row['accident_count'])}건<br>"
                f"평균 응급도착: {row['ems_response_min']:.1f}분"
            ),
        ).add_to(m)

    return m
```

- [ ] **Step 5.3.2: 시민 모드에 지도 통합**

```python
# src/ui/citizen.py의 right 컬럼 교체
from streamlit_folium import st_folium
from src.viz import build_risk_map

# ... (left 컬럼은 그대로)
    with right:
        st.subheader("전국 위험지도")
        m = build_risk_map(features, selected_sgg=sgg_name)
        st_folium(m, width=None, height=600, returned_objects=[])
```

- [ ] **Step 5.3.3: 브라우저 확인**

```powershell
streamlit run app.py
```

Expected: 전국 시군구가 점으로 표시되고 색이 위험도에 따라 다름. 호버하면 툴팁. 시군구 선택 시 해당 점이 강조.

- [ ] **Step 5.3.4: 커밋**

```powershell
git add src/viz.py src/ui/citizen.py
git commit -m "feat(ui): Folium 지도 통합 — 시군구별 위험지수 색 표현"
```

### Task 5.4: 시민 모드 — 상위 위험지대 리스트

**Files:**
- Modify: `src/ui/citizen.py`

- [ ] **Step 5.4.1: 하단 리스트 섹션 추가**

```python
# src/ui/citizen.py 하단에 추가
    st.divider()
    st.subheader("전국 상위 잠재 위험지대 TOP 10")
    top = features.nlargest(10, "risk_index")[
        ["sgg_name", "risk_index", "accident_count", "fatality_rate", "ems_response_min", "ems_distance_km"]
    ].rename(
        columns={
            "sgg_name": "시군구",
            "risk_index": "위험지수",
            "accident_count": "사고건수",
            "fatality_rate": "사망사고비율",
            "ems_response_min": "평균출동(분)",
            "ems_distance_km": "응급기관거리(km)",
        }
    )
    st.dataframe(top, use_container_width=True, hide_index=True)
```

- [ ] **Step 5.4.2: 확인 + 커밋**

```powershell
streamlit run app.py
git add src/ui/citizen.py
git commit -m "feat(ui): 시민 모드 — 전국 상위 10개 잠재 위험지대 리스트"
```

---

## Phase 6: Streamlit UI — Policy Simulator

### Task 6.1: 정책 시뮬레이터 — 가상 응급기관 추가

**Files:**
- Modify: `src/ui/policy.py`

- [ ] **Step 6.1.1: 시뮬레이터 view 작성**

```python
# src/ui/policy.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from src.viz import KOREA_CENTER
from src.inference import simulate_new_ems


def render(features: pd.DataFrame):
    st.title("정책 시뮬레이터")
    st.caption("가상 응급기관·분서를 추가하면 어떤 변화가 생기나?")

    if "virtual_ems" not in st.session_state:
        st.session_state.virtual_ems = []

    left, right = st.columns([1, 2])

    with left:
        st.subheader("가상 응급기관 추가")
        lon = st.number_input("경도", value=127.0, format="%.4f")
        lat = st.number_input("위도", value=37.5, format="%.4f")
        if st.button("추가"):
            st.session_state.virtual_ems.append((lon, lat))
        if st.button("초기화"):
            st.session_state.virtual_ems = []

        st.write(f"현재 추가된 가상 응급기관: {len(st.session_state.virtual_ems)}개")
        for i, (lo, la) in enumerate(st.session_state.virtual_ems, 1):
            st.write(f"{i}. ({lo:.4f}, {la:.4f})")

    with right:
        st.subheader("시뮬레이션 결과")
        result = simulate_new_ems(st.session_state.virtual_ems)

        col1, col2, col3 = st.columns(3)
        avg_delta = result["risk_delta"].mean()
        max_drop = result["risk_delta"].min()
        improved = (result["risk_delta"] < -0.001).sum()
        col1.metric("평균 위험지수 변화", f"{avg_delta:+.4f}")
        col2.metric("가장 큰 위험 감소", f"{max_drop:+.4f}")
        col3.metric("개선된 시군구 수", f"{improved}개")

        # 지도: 감소가 큰 시군구 강조
        m = folium.Map(location=KOREA_CENTER, zoom_start=7, tiles="cartodbpositron")
        for _, row in result.iterrows():
            delta = row["risk_delta"]
            radius = max(3, min(15, abs(delta) * 500))
            color = "#2ca02c" if delta < 0 else "#cccccc"
            folium.CircleMarker(
                [row["lat"], row["lon"]],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"{row['sgg_name']}<br>변화: {delta:+.4f}",
            ).add_to(m)
        for lo, la in st.session_state.virtual_ems:
            folium.Marker([la, lo], icon=folium.Icon(color="red", icon="plus")).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])

    st.divider()
    st.subheader("개선 효과 TOP 10 시군구")
    top_improved = result.nsmallest(10, "risk_delta")[
        ["sgg_name", "risk_index", "risk_index_new", "risk_delta", "ems_distance_km_new"]
    ].rename(
        columns={
            "sgg_name": "시군구",
            "risk_index": "기존 위험",
            "risk_index_new": "신규 위험",
            "risk_delta": "변화",
            "ems_distance_km_new": "신규 응급기관거리(km)",
        }
    )
    st.dataframe(top_improved, use_container_width=True, hide_index=True)
```

- [ ] **Step 6.1.2: 브라우저 동작 확인**

```powershell
streamlit run app.py
```

Expected: 정책 모드에서 경위도 입력 → 가상 응급기관 추가 → 시뮬레이션 결과(지도·메트릭·TOP 10) 즉시 갱신.

- [ ] **Step 6.1.3: 커밋**

```powershell
git add src/ui/policy.py
git commit -m "feat(ui): 정책 시뮬레이터 — 가상 응급기관 추가 What-if 분석"
```

---

## Phase 7: About Page + 발표·제출 준비

### Task 7.1: About 페이지

**Files:**
- Modify: `src/ui/about.py`

- [ ] **Step 7.1.1: About 페이지 작성**

```python
# src/ui/about.py
import streamlit as st


def render():
    st.title("About — BlindZone")

    st.markdown(
        """
### 무엇을 푸는가

한국 교통사고 골든타임 놓침으로 인한 사망률이 선진국의 2배입니다. 사고 후 1시간 내 수술실 도착률은 50% 수준에 그칩니다. 그러나 기존 사고 통계 지도는 "사고가 자주 나는 곳"만 보여줄 뿐, **사고 위험 × 응급 도달 시간**을 결합해 잠재 위험지대를 발굴하는 일반인용 서비스는 부재했습니다.

BlindZone은 사고 통계와 응급 의료 접근성을 결합해 **"사고는 평균인데 죽음은 많은 곳"**을 발굴하는 서비스입니다.

### 사용한 데이터

- 전국교통사고다발지역표준데이터 (공공데이터포털, TAAS 기반)
- 전국응급의료기관표준데이터 (공공데이터포털, 보건복지부)
- 소방청 119구급서비스 통계연보 (공공데이터포털, 소방청)
- 시군구 행정경계 (통계청 SGIS)

### 방법론

1. 시군구 단위로 사고 빈도·사망사고 비율·응급 도달 시간·응급기관 거리 등 변수를 산출
2. 변수들을 가중합한 "잠재 위험 지수"를 정의
3. XGBoost 회귀 모델로 위험 지수를 재학습 → SHAP 값으로 격자별 "왜 위험한가" 설명
4. 가상 응급기관 추가 시뮬레이션은 동일 모델을 inference loop으로 활용

### 한계

- 시군구 단위 평균 데이터를 사용해 격자 내 변동성은 평준화됨 (V1.1에서 1km 격자 세분화 예정)
- 119 출동 raw 데이터(사건별)는 비공개, 통계 평균과 응급기관 거리로 추정
- 사망률 정확 추정에는 의료 외 변수(병원 수용능력 등) 추가 필요

### 가점 항목 활용

- AI 학습도구 (Claude Code): 5점
- AI 분석도구 (XGBoost + SHAP): 5점
- 데이터 융합 (사고 × 응급의료 × 119 × 행정경계): 5점
"""
    )
```

- [ ] **Step 7.1.2: 커밋**

```powershell
git add src/ui/about.py
git commit -m "feat(ui): About 페이지 — 문제·데이터·방법론·한계·가점 명시"
```

### Task 7.2: README + 배포 준비

**Files:**
- Modify: `README.md`

- [ ] **Step 7.2.1: README 작성**

```markdown
# BlindZone — 보이지 않던 위험지대

> 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙)
>
> 사고는 적은데 죽음은 많은 곳, 데이터로 찾았습니다.

## 무엇

한국 교통사고 골든타임 놓침으로 인한 사망률은 선진국의 2배. BlindZone은 사고 위험 × 응급 도달 시간을 결합해 통계가 가려둔 잠재 위험지대를 발굴하고, 응급 자원 추가 배치를 시뮬레이션하는 웹 서비스입니다.

## 데모

(Streamlit Cloud 배포 후 URL 추가)

## 로컬 실행

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# data/raw/에 5개 공공데이터 파일 다운로드 (자세한 안내: scripts/download_data.py 실행)
python scripts/download_data.py

# 데이터 가공 + 모델 학습
python scripts/build_features.py
python -m src.train

# 앱 실행
streamlit run app.py
```

## 기술 스택

Python · Streamlit · Folium · XGBoost · SHAP · GeoPandas

## 데이터 출처

- TAAS 교통사고분석시스템 (한국도로교통공단)
- 전국응급의료기관표준데이터 (보건복지부)
- 소방청 119구급서비스 통계연보
- 시군구 행정경계 (통계청 SGIS)
```

- [ ] **Step 7.2.2: 커밋**

```powershell
git add README.md
git commit -m "docs: README — 로컬 실행 가이드 + 기술 스택 + 데이터 출처"
```

### Task 7.3: Streamlit Cloud 배포 (수동)

**Files:** (변경 없음, GitHub repo 필요)

- [ ] **Step 7.3.1: GitHub repo 생성 (private 또는 public 선택)**

```powershell
# GitHub에서 repo 생성 후
git remote add origin https://github.com/<USER>/molit-2026.git
git branch -M main
git push -u origin main
```

- [ ] **Step 7.3.2: Streamlit Cloud(share.streamlit.io)에서 앱 배포**

1. share.streamlit.io 접속 → GitHub 연동
2. molit-2026 repo 선택
3. main branch / app.py 지정
4. Deploy

- [ ] **Step 7.3.3: 배포 URL 확인 + README에 추가**

배포 URL을 README의 데모 섹션과 발표자료에 반영. 한 번 더 커밋.

```powershell
git add README.md
git commit -m "docs: Streamlit Cloud 데모 URL 추가"
git push
```

### Task 7.4: 발표 자료 + 데모 영상

**Files:** (산출물은 별도 폴더, 코드 외)

- [ ] **Step 7.4.1: 발표 자료 outline (대회 양식 확인 필수)**

대회 사이트(bigdata-transportation.kr) FAQ에서 1차 심사 제출물 양식 확인. 일반적으로:
1. 문제 정의 (1슬라이드)
2. 데이터 (1슬라이드)
3. 방법론 (1~2슬라이드)
4. 시제품 데모 스크린샷 (2슬라이드)
5. 정책 implication (1슬라이드)
6. 기대 효과·확장성 (1슬라이드)

핵심 메시지: "사고는 적은데 죽음은 많은 곳, 데이터로 찾았습니다"

- [ ] **Step 7.4.2: 데모 영상 (1~2분)**

OBS Studio 또는 Windows 기본 화면녹화로:
1. 시민 모드: 시군구 검색 → 메트릭·SHAP 설명 보여주기 (30초)
2. 지도 줌·호버 (15초)
3. 정책 시뮬레이터: 가상 응급기관 추가 → 결과 변화 (45초)
4. About 페이지 빠른 스크롤 (15초)

영상 파일은 `data/sample/` 또는 별도 폴더에 저장 (커밋 X, 발표 자료에 첨부).

- [ ] **Step 7.4.3: 최종 점검 체크리스트**

```
[ ] Streamlit Cloud 배포 URL 동작
[ ] 모든 모드 (시민/정책/About) 동작
[ ] requirements.txt 누락 없음
[ ] README에 배포 URL + 데이터 출처 명시
[ ] 발표자료에 데모 영상 첨부 또는 URL 안내
[ ] 1차 심사 양식에 맞게 제출 파일 정리
[ ] 대회 사이트에서 접수 완료
```

---

## Self-Review

**1. Spec coverage:** 디자인 스펙의 모든 섹션이 plan에 매핑됨.
- "1. 한 줄 정의" → Task 7.1, 7.2 (About, README)
- "2. 문제 정의" → Task 7.1
- "3. 목표 사용자" → Phase 5, 6 (시민/정책 모드)
- "4. 핵심 기능 V1" → Phase 5, 6
- "5. 데이터 라인업" → Phase 2
- "6. AI 활용" → Phase 4 (XGBoost + SHAP), Phase 1 (Claude Code 학습도구)
- "7. 기술 스택" → Phase 1 (requirements.txt)
- "8. 데이터 파이프라인" → Phase 3
- "9. UI 레이아웃" → Phase 5
- "10. 발표·제출물" → Phase 7
- "11. 성공 기준" → 외부 (대회 결과)
- "12. 일정" → 각 Phase의 일자 매핑
- "13. 리스크" → Phase 3.7 (인사이트 검증), download_data.py (fallback URL 안내)
- "14. 미결 사항" → Phase 3 (수식 EDA 결정), Phase 7 (양식 확인)

**2. Placeholder scan:** "TBD" / "TODO" / "Add appropriate error handling" 등 빈 placeholder 없음. 모든 step에 실제 코드. 단, "1차 심사 양식 확인" 같은 한태영 외부 액션은 명시적 step으로 표기.

**3. Type consistency:**
- `normalize_sgg_code` 모든 호출에서 string 반환 일관 ✓
- `nearest_ems_distance_km`의 출력 컬럼 `ems_distance_km` 일관 ✓
- `load_ems_response_time`의 출력 컬럼 `ems_response_min` 일관 ✓
- `FEATURE_COLS`에 `area_km2` 포함되었는지 — Task 3.5에서 추출하므로 매칭 ✓
- 단, Task 4.1의 `FEATURE_COLS`에 `area_km2` 있는데 Task 3.6의 `build_grid_features`가 area_km2를 features에 포함하는지 — `load_sgg_centers`가 `area_km2`를 반환하고 centers를 merge 기준으로 쓰므로 포함됨 ✓
- `simulate_new_ems` 반환 컬럼 `risk_index_new`, `risk_delta` → policy.py에서 동일 이름으로 사용 ✓

**알려진 한계:**
- TAAS 실제 컬럼명(시군구코드/사고건수/사망자수/부상자수)이 plan의 가정과 다를 수 있음 → Task 3.6에서 inspect_data.py 출력 기반 rename 필요
- 119 통계연보 시트 구조도 마찬가지 — Task 3.4의 rename_map 조정 필요

---

## 다음 단계

1. **한태영 plan 리뷰** — 통째로 OK 받기
2. Execution 모드 선택 (subagent-driven 또는 inline)
3. Phase 1부터 순차 실행
