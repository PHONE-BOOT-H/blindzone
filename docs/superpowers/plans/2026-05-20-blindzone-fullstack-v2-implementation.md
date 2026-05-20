# BlindZone Fullstack Implementation Plan v2

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit prototype → 풀스택(Next.js + FastAPI) 시제품 전환. 시군구 GeoJSON을 정확한 출처(통계청 센서스경계 SHP)로 갱신. **외부 AI 평가 권장사항 모두 반영** (정직성·SHAP 사전계산·RiskMap 버그 fix·requirements 분리·`/api/contrast` 신규 등). Vercel + Railway 배포해 BlindZone을 2026 국토교통 데이터 활용 경진대회 제출 가능한 상태로.

**Architecture:** 백엔드는 FastAPI로 SHAP 사전계산된 feature table을 HTTP endpoint로 제공 (런타임 SHAP 계산 X — Railway 안정성). 프론트엔드는 Next.js 14 + TypeScript + Tailwind, 지도는 MapLibre GL + deck.gl (centroid scatter + 시간 허락 시 polygon choropleth). Railway (백) + Vercel (프) 배포.

**Tech Stack:**
- Backend: FastAPI, uvicorn, pydantic. 학습용: xgboost, shap, geopandas, pandas. 배포 런타임: 최소화 (geopandas/shap 제외)
- Frontend: Next.js 14, TypeScript, Tailwind CSS, MapLibre GL JS, deck.gl, (선택) Recharts
- Deploy: Railway (backend), Vercel (frontend)

---

## Spec References (필수 참고)

- `docs/PROJECT_SPEC.md` — 풀스택 architecture, 심사 기준, 가점 신청, **정직성 8개 위험표현·정정 표**, 데이터 출처 표
- `docs/submission/external-review-2026-05-20.md` — **외부 AI 평가 본문** (이 v2 plan의 근거)
- `docs/submission/data_manifest.md` — 데이터 출처·라이선스·가공식 한 표
- `docs/submission/model_card.md` — surrogate model 명시 (위험 예측 X)
- `docs/superpowers/specs/2026-05-19-blindzone-design.md` — 원본 디자인 spec (컨셉·모델·데이터는 유효)
- Deprecated: `docs/superpowers/plans/2026-05-19-blindzone-streamlit-implementation-deprecated.md`, `docs/superpowers/plans/2026-05-20-blindzone-fullstack-v1-deprecated.md`

**절대 원칙**: 없는 것을 지어내지 않는다. 데이터·통계·작동결과·가점 모두 검증된 사실만. 모호하면 명시 마킹.

---

## v1 대비 주요 변경 사항

1. **Phase 0 (시군구 갱신) — 완료** ✅ (한태영 VWORLD 다운로드 + build + train 재실행 + commit `0380b82` 완료)
2. **Phase A 보강**:
   - `precompute_shap.py` 추가 → SHAP을 런타임이 아닌 사전 계산. `feature_details.parquet` 산출
   - `/api/contrast` endpoint 신규 — 사고건수 TOP10 vs BlindZone TOP10 비교 (독창성 강화)
   - `requirements-api.txt` 분리 — 배포 런타임 최소화 (geopandas/shap 제외)
3. **Phase B 보강**:
   - **RiskMap `Map` shadowing 버그 fix** — `import MapLibreMap` + `new globalThis.Map(...)`
   - **Polygon choropleth** (선택) — GeoJsonLayer로 시군구 면 색칠 (시각 임팩트)
   - 사고건수 vs BlindZone 비교 컴포넌트
   - 용어 통일: "응급기관·분서" → "응급의료 거점"
4. **Phase D 보강**:
   - **D.0 (제출서류 확인)** 신규 — 참가신청서·서약서·기획서 HWP 선확보
   - About/README **8개 위험표현 정정** (정직성)
   - 대표 사례 1개 발굴 task 추가
5. 일정 가이드 제거 (한태영 "기한 무관" 모드 — strict X)

---

## File Structure

```
project-root/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app + CORS
│   │   ├── routes.py           # 6개 endpoint (health/features/detail/top10/simulate/contrast)
│   │   ├── schemas.py          # Pydantic models
│   │   └── deps.py             # 정적 데이터 싱글톤 로더 (모델 + features + feature_details)
│   ├── src/                    # 기존 ML 코드
│   ├── data/                   # raw, processed (feature_details.parquet 신규)
│   ├── models/
│   ├── scripts/                # build_features.py, precompute_shap.py (신규), train.py 모듈, fetch_api_data.py, ...
│   ├── tests/
│   │   ├── test_data_pipeline.py
│   │   ├── test_train.py
│   │   └── test_api.py            # 신규
│   ├── requirements.txt        # 학습용 전체
│   ├── requirements-api.txt    # 배포 런타임 최소 (신규)
│   └── Procfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx            # 시민 모드 (/)
│   │   ├── policy/page.tsx     # 정책 시뮬레이터 (/policy)
│   │   ├── about/page.tsx      # About (/about) — 정직성 정정 적용
│   │   └── globals.css
│   ├── components/
│   │   ├── Nav.tsx
│   │   ├── RiskMap.tsx         # MapLibreMap rename, choropleth 옵션
│   │   ├── MetricCard.tsx
│   │   ├── ShapExplanation.tsx
│   │   ├── Top10Table.tsx
│   │   ├── ContrastPanel.tsx   # 신규 — 사고건수 vs BlindZone 비교
│   │   └── PolicySimulator.tsx
│   ├── lib/
│   │   ├── api.ts              # /api/contrast 포함
│   │   └── types.ts
│   ├── public/
│   ├── package.json
│   └── ...
├── docs/
│   ├── PROJECT_SPEC.md
│   ├── CURRENT_STATE.md
│   ├── submission/
│   │   ├── external-review-2026-05-20.md
│   │   ├── data_manifest.md
│   │   ├── model_card.md
│   │   ├── checklist.md            # D.0에서 작성
│   │   └── ai-tool-evidence.md     # D.2에서 작성
│   └── superpowers/...
└── README.md
```

---

## Testing Strategy

- **Backend unit/integration**: pytest. 기존 11 + train 1 + 신규 API 7
- **Backend endpoint manual**: curl로 6개 endpoint 검증
- **Frontend manual**: 한태영이 브라우저 직접 확인
- **Frontend type check**: `tsc --noEmit`
- **배포 검증**: 배포 후 URL 접속, 모든 페이지 로드 + API 호출 + 콘솔 에러 0

---

## Phase 0: 시군구 GeoJSON 갱신 (완료 ✅)

| Task | 상태 | Commit |
|---|---|---|
| 0.1 VWORLD 통계청 (센서스경계) SHP 다운로드 | ✅ | (한태영 액션) |
| 0.2 inspect + 컬럼 매핑 (SIGUNGU_CD/SIGUNGU_NM alias) | ✅ | `0380b82` |
| 0.3 build_features + train 재실행 | ✅ | `0380b82` |
| 0.4 commit | ✅ | `0380b82` |

**결과**: 252 시군구, R²=0.900, MAE=0.0079, blind zone 10개 발굴 동일 패턴.

---

## Phase A: FastAPI 백엔드

### Task A.0: SHAP 사전 계산 (신규, **외부 평가 4번**)

**Files:**
- Create: `backend/scripts/precompute_shap.py`
- Create: `backend/data/processed/feature_details.parquet`

런타임에서 SHAP 계산하면 Railway 메모리·응답속도 위험. 사전 계산해서 parquet에 저장 → API는 read-only.

- [ ] **Step A.0.1**: `backend/scripts/precompute_shap.py` 작성

```python
"""모든 시군구에 대해 SHAP 상위 3개 피처를 사전 계산하여 parquet에 저장."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.config import GRID_FEATURES_PATH, DATA_PROCESSED  # noqa: E402
from src.shap_explain import explain_one  # noqa: E402


def main():
    df = pd.read_parquet(GRID_FEATURES_PATH)
    print(f"computing SHAP for {len(df)} rows ...")
    shap_rows = []
    for _, row in df.iterrows():
        try:
            items = explain_one(row)
        except Exception as exc:
            print(f"  [WARN] sgg {row['sgg_code']}: {exc}")
            items = []
        shap_rows.append(json.dumps(items, ensure_ascii=False))
    df_out = df.copy()
    df_out["shap_top_json"] = shap_rows
    out_path = DATA_PROCESSED / "feature_details.parquet"
    df_out.to_parquet(out_path, index=False)
    print(f"saved: {out_path} ({len(df_out)} rows)")


if __name__ == "__main__":
    main()
```

- [ ] **Step A.0.2**: 실행

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\precompute_shap.py
```

Expected: `data/processed/feature_details.parquet` 생성, 252 rows, `shap_top_json` 컬럼 추가.

- [ ] **Step A.0.3**: commit

```powershell
cd ..
git add backend/scripts/precompute_shap.py backend/data/processed/feature_details.parquet
git commit -m "feat(model): SHAP 사전 계산 — 런타임 부담 제거, feature_details.parquet 생성"
```

### Task A.1: FastAPI 의존성 + 디렉토리 골격 + requirements 분리 (**외부 평가 9번**)

**Files:**
- Create: `backend/api/__init__.py`, `main.py`, `routes.py`, `schemas.py`, `deps.py`
- Create: `backend/requirements-api.txt` (배포 런타임 최소)

- [ ] **Step A.1.1**: `backend/requirements-api.txt` 작성

```
# 배포 런타임 최소 (Railway용)
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
pandas>=2.2.0
pyarrow>=15.0.0
numpy>=1.26.0
scikit-learn>=1.4.0
xgboost>=2.0.0
python-dotenv>=1.0.0
# 주의: geopandas, shap, openpyxl, requests는 학습/사전계산용. 배포 런타임 X
```

- [ ] **Step A.1.2**: 디렉토리 + 빈 파일 생성

```powershell
cd backend
New-Item -ItemType Directory -Force -Path api
New-Item -ItemType File -Force -Path api\__init__.py, api\main.py, api\routes.py, api\schemas.py, api\deps.py
```

- [ ] **Step A.1.3**: requirements-api.txt 설치 확인 (학습용 .venv에 이미 fastapi 설치되어 있으면 skip)

```powershell
..\.venv\Scripts\pip.exe install -r requirements-api.txt
```

### Task A.2: Pydantic schemas

**Files:** Create: `backend/api/schemas.py`

- [ ] **Step A.2.1**: 작성

```python
# backend/api/schemas.py
from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureSummary(BaseModel):
    sgg_code: str
    sgg_name: str
    lon: float
    lat: float
    risk_index: float
    accident_count: int
    fatality_rate: float
    ems_distance_km: float
    ems_response_min: float


class ShapItem(BaseModel):
    feature: str
    shap_value: float
    direction: str  # "위험 증가" | "위험 감소"


class FeatureDetail(FeatureSummary):
    area_km2: float
    fatality_count: int
    injury_count: int
    shap_top: list[ShapItem]


class SimulateRequest(BaseModel):
    virtual_ems: list[tuple[float, float]] = Field(
        default_factory=list,
        description="가상 응급의료 거점 좌표 [(lon, lat), ...]"
    )


class SimulationItem(BaseModel):
    sgg_code: str
    sgg_name: str
    lon: float
    lat: float
    risk_index: float
    risk_index_new: float
    risk_delta: float
    ems_distance_km_new: float


class SimulateResponse(BaseModel):
    avg_delta: float
    max_drop: float
    improved_count: int
    items: list[SimulationItem]


class ContrastItem(BaseModel):
    sgg_code: str
    sgg_name: str
    accident_count: int
    accident_rank: int  # 사고건수 순위
    risk_rank: int       # BlindZone 순위
    rank_diff: int       # 사고 순위 - BlindZone 순위 (양수면 BlindZone에서 더 위험)


class ContrastResponse(BaseModel):
    blindzone_top10_not_in_accident_top10: int
    accident_top10_not_in_blindzone_top10: int
    items: list[ContrastItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    features_loaded: bool
    feature_count: int
```

### Task A.3: 데이터·모델 싱글톤 로더 (precomputed feature_details 활용)

**Files:** Create: `backend/api/deps.py`

- [ ] **Step A.3.1**: 작성

```python
# backend/api/deps.py
"""SHAP 사전 계산된 feature_details와 모델 싱글톤 로드."""
from __future__ import annotations

import json
import pickle
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import DATA_PROCESSED, MODEL_PATH  # noqa: E402

FEATURE_DETAILS_PATH = DATA_PROCESSED / "feature_details.parquet"

_features: pd.DataFrame | None = None
_model_bundle: dict | None = None


def get_features() -> pd.DataFrame:
    """SHAP 사전 계산된 feature_details parquet 로드."""
    global _features
    if _features is None:
        _features = pd.read_parquet(FEATURE_DETAILS_PATH)
    return _features


def get_model_bundle() -> dict:
    """XGBoost 모델 로드 — simulate endpoint에서만 사용."""
    global _model_bundle
    if _model_bundle is None:
        with open(MODEL_PATH, "rb") as f:
            _model_bundle = pickle.load(f)
    return _model_bundle


def parse_shap(json_str: str) -> list[dict]:
    """parquet에 저장된 shap_top_json 문자열 → 리스트."""
    if not json_str:
        return []
    return json.loads(json_str)
```

### Task A.4: FastAPI app 진입점 + CORS

**Files:** Create: `backend/api/main.py`

- [ ] **Step A.4.1**: 작성

```python
# backend/api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="BlindZone API",
    description="사고 위험 × 응급 사각지대 분석 API (탐색형 surrogate)",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
```

### Task A.5: GET /api/health endpoint

**Files:** Create: `backend/api/routes.py` (시작)

- [ ] **Step A.5.1**: routes.py 초기

```python
# backend/api/routes.py
from fastapi import APIRouter, HTTPException

from api import schemas
from api.deps import get_features, get_model_bundle, parse_shap

router = APIRouter()


@router.get("/health", response_model=schemas.HealthResponse)
def health():
    try:
        features = get_features()
        bundle = get_model_bundle()
        return schemas.HealthResponse(
            status="ok",
            model_loaded=bundle is not None,
            features_loaded=features is not None,
            feature_count=len(features),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

- [ ] **Step A.5.2**: 실행 + curl 검증

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
# 별도 터미널에서
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","model_loaded":true,"features_loaded":true,"feature_count":252}`

### Task A.6: GET /api/features endpoint

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.6.1**: 추가

```python
@router.get("/features", response_model=list[schemas.FeatureSummary])
def list_features():
    df = get_features()
    cols = ["sgg_code", "sgg_name", "lon", "lat", "risk_index",
            "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min"]
    out = df[cols].copy()
    out["accident_count"] = out["accident_count"].astype(int)
    return out.to_dict(orient="records")
```

- [ ] **Step A.6.2**: 검증

```powershell
curl "http://localhost:8000/api/features" -o features.json
..\.venv\Scripts\python.exe -c "import json; d = json.load(open('features.json', encoding='utf-8')); print(len(d), d[0])"
```

Expected: 252개 항목.

### Task A.7: GET /api/features/{sgg_code} endpoint (사전계산 SHAP 활용)

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.7.1**: 추가

```python
@router.get("/features/{sgg_code}", response_model=schemas.FeatureDetail)
def get_feature_detail(sgg_code: str):
    df = get_features()
    row = df[df["sgg_code"] == sgg_code]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"sgg_code {sgg_code} not found")
    row = row.iloc[0]
    shap_list = parse_shap(row.get("shap_top_json", ""))
    return schemas.FeatureDetail(
        sgg_code=row["sgg_code"],
        sgg_name=row["sgg_name"],
        lon=float(row["lon"]),
        lat=float(row["lat"]),
        risk_index=float(row["risk_index"]),
        accident_count=int(row["accident_count"]),
        fatality_rate=float(row["fatality_rate"]),
        ems_distance_km=float(row["ems_distance_km"]),
        ems_response_min=float(row["ems_response_min"]),
        area_km2=float(row["area_km2"]),
        fatality_count=int(row["fatality_count"]),
        injury_count=int(row["injury_count"]),
        shap_top=[schemas.ShapItem(**item) for item in shap_list],
    )
```

- [ ] **Step A.7.2**: 검증

```powershell
curl "http://localhost:8000/api/features/11010"
```

Expected: 종로구 상세 + shap_top 3개 (사전계산값).

### Task A.8: GET /api/top10 endpoint

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.8.1**: 추가

```python
@router.get("/top10", response_model=list[schemas.FeatureSummary])
def top10():
    df = get_features()
    top = df.nlargest(10, "risk_index")
    cols = ["sgg_code", "sgg_name", "lon", "lat", "risk_index",
            "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min"]
    out = top[cols].copy()
    out["accident_count"] = out["accident_count"].astype(int)
    return out.to_dict(orient="records")
```

### Task A.9: POST /api/simulate endpoint

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.9.1**: simulate_new_ems는 geopandas 의존. **배포 환경에서 geopandas 없으면 import 실패**. 두 가지 선택:

**옵션 1 (권장)**: simulate는 사전 계산된 거리 + numpy로 근사. geopandas 의존 제거.

```python
import numpy as np
from api.deps import get_features, get_model_bundle


def _haversine_km(lon1, lat1, lon2, lat2):
    """단순 haversine 거리 (km)."""
    R = 6371.0
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))


@router.post("/simulate", response_model=schemas.SimulateResponse)
def simulate(req: schemas.SimulateRequest):
    df = get_features()
    bundle = get_model_bundle()
    model = bundle["model"]
    cols = bundle["feature_cols"]

    if not req.virtual_ems:
        # 빈 시뮬레이션: 변화 없음
        items = []
        return schemas.SimulateResponse(
            avg_delta=0.0, max_drop=0.0, improved_count=0, items=items
        )

    # 각 시군구 중심점에서 가상 ems까지 거리 (km, haversine)
    new_dist_arr = df["ems_distance_km"].values.copy()
    for vlon, vlat in req.virtual_ems:
        d = _haversine_km(df["lon"].values, df["lat"].values, vlon, vlat)
        new_dist_arr = np.minimum(new_dist_arr, d)

    # 모델 재추론
    X_new = df[cols].copy().fillna(0)
    X_new["ems_distance_km"] = new_dist_arr
    risk_new = model.predict(X_new)

    result = df.copy()
    result["risk_index_new"] = risk_new
    result["risk_delta"] = result["risk_index_new"] - result["risk_index"]
    result["ems_distance_km_new"] = new_dist_arr

    avg_delta = float(result["risk_delta"].mean())
    max_drop = float(result["risk_delta"].min())
    improved_count = int((result["risk_delta"] < -0.001).sum())

    top_items = result.nsmallest(50, "risk_delta")
    items = [
        schemas.SimulationItem(
            sgg_code=r["sgg_code"],
            sgg_name=r["sgg_name"],
            lon=float(r["lon"]),
            lat=float(r["lat"]),
            risk_index=float(r["risk_index"]),
            risk_index_new=float(r["risk_index_new"]),
            risk_delta=float(r["risk_delta"]),
            ems_distance_km_new=float(r["ems_distance_km_new"]),
        )
        for _, r in top_items.iterrows()
    ]
    return schemas.SimulateResponse(
        avg_delta=avg_delta,
        max_drop=max_drop,
        improved_count=improved_count,
        items=items,
    )
```

- [ ] **Step A.9.2**: 검증

```powershell
curl -X POST "http://localhost:8000/api/simulate" -H "Content-Type: application/json" -d '{"virtual_ems":[[127.0,37.5]]}'
```

Expected: avg_delta, max_drop, improved_count 응답.

### Task A.10: GET /api/contrast endpoint (신규, **외부 평가 7번**)

**Files:** Modify: `backend/api/routes.py`

사고건수 순위와 BlindZone 위험지수 순위가 얼마나 다른지. **독창성 30점 강화 핵심**.

- [ ] **Step A.10.1**: 추가

```python
@router.get("/contrast", response_model=schemas.ContrastResponse)
def contrast():
    df = get_features().copy()
    # 사고건수 순위 (1위 = 가장 사고 많음)
    df["accident_rank"] = df["accident_count"].rank(method="min", ascending=False).astype(int)
    df["risk_rank"] = df["risk_index"].rank(method="min", ascending=False).astype(int)
    df["rank_diff"] = df["accident_rank"] - df["risk_rank"]

    blindzone_top10 = set(df.nlargest(10, "risk_index")["sgg_code"])
    accident_top10 = set(df.nlargest(10, "accident_count")["sgg_code"])

    # BlindZone TOP10에 들어있지만 사고 TOP10에는 없는 시군구 = 통계 사각지대
    bz_only = blindzone_top10 - accident_top10
    acc_only = accident_top10 - blindzone_top10

    # 응답 items: 두 그룹 합쳐서 차이 큰 순으로 (BlindZone TOP10 우선)
    items_df = df[df["sgg_code"].isin(blindzone_top10 | accident_top10)].copy()
    items_df = items_df.sort_values("rank_diff", ascending=False)

    items = [
        schemas.ContrastItem(
            sgg_code=r["sgg_code"],
            sgg_name=r["sgg_name"],
            accident_count=int(r["accident_count"]),
            accident_rank=int(r["accident_rank"]),
            risk_rank=int(r["risk_rank"]),
            rank_diff=int(r["rank_diff"]),
        )
        for _, r in items_df.iterrows()
    ]
    return schemas.ContrastResponse(
        blindzone_top10_not_in_accident_top10=len(bz_only),
        accident_top10_not_in_blindzone_top10=len(acc_only),
        items=items,
    )
```

- [ ] **Step A.10.2**: 검증

```powershell
curl "http://localhost:8000/api/contrast"
```

Expected: `{"blindzone_top10_not_in_accident_top10": N, ...}` — N이 발표 임팩트 핵심 숫자.

### Task A.11: API 통합 테스트 (pytest + TestClient)

**Files:** Create: `backend/tests/test_api.py`

- [ ] **Step A.11.1**: 테스트 작성

```python
# backend/tests/test_api.py
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert body["features_loaded"] is True
    assert body["feature_count"] > 0


def test_features_list():
    resp = client.get("/api/features")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) >= 200
    assert {"sgg_code", "sgg_name", "lon", "lat", "risk_index"}.issubset(body[0].keys())


def test_feature_detail_known_sgg():
    list_resp = client.get("/api/features").json()
    sample_code = list_resp[0]["sgg_code"]
    resp = client.get(f"/api/features/{sample_code}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["sgg_code"] == sample_code
    assert "shap_top" in body


def test_feature_detail_unknown():
    resp = client.get("/api/features/99999")
    assert resp.status_code == 404


def test_top10():
    resp = client.get("/api/top10")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 10


def test_simulate_empty():
    resp = client.post("/api/simulate", json={"virtual_ems": []})
    assert resp.status_code == 200
    body = resp.json()
    assert body["improved_count"] == 0


def test_simulate_with_virtual_ems():
    resp = client.post("/api/simulate", json={"virtual_ems": [[127.0, 37.5]]})
    assert resp.status_code == 200
    body = resp.json()
    assert body["improved_count"] >= 0
    assert len(body["items"]) > 0


def test_contrast():
    resp = client.get("/api/contrast")
    assert resp.status_code == 200
    body = resp.json()
    assert body["blindzone_top10_not_in_accident_top10"] >= 0
    assert len(body["items"]) >= 10
```

- [ ] **Step A.11.2**: 실행

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/test_api.py -v
```

Expected: 8 PASS.

### Task A.12: Phase A commit

- [ ] **Step A.12.1**:

```powershell
cd ..
git add backend/api backend/requirements-api.txt backend/tests/test_api.py
git commit -m "feat(api): FastAPI 백엔드 — 6 endpoint (health/features/detail/top10/simulate/contrast) + 사전계산 SHAP + 배포 런타임 분리 + 8 통합 테스트"
```

---

## Phase B: Next.js 프론트엔드

### Task B.1: Next.js init

**Files:** Create: `frontend/` 전체

- [ ] **Step B.1.1**: init

```powershell
Remove-Item frontend\.gitkeep
cd frontend
npx create-next-app@14 . --typescript --tailwind --app --no-src-dir --import-alias "@/*" --eslint
```

- [ ] **Step B.1.2**: 의존성

```powershell
npm install maplibre-gl react-map-gl deck.gl @deck.gl/react @deck.gl/layers @deck.gl/geo-layers
```

### Task B.2: TypeScript types + API client (+ contrast)

**Files:** Create: `frontend/lib/types.ts`, `frontend/lib/api.ts`

- [ ] **Step B.2.1**: types.ts

```typescript
// frontend/lib/types.ts
export interface FeatureSummary {
  sgg_code: string;
  sgg_name: string;
  lon: number;
  lat: number;
  risk_index: number;
  accident_count: number;
  fatality_rate: number;
  ems_distance_km: number;
  ems_response_min: number;
}

export interface ShapItem {
  feature: string;
  shap_value: number;
  direction: string;
}

export interface FeatureDetail extends FeatureSummary {
  area_km2: number;
  fatality_count: number;
  injury_count: number;
  shap_top: ShapItem[];
}

export interface SimulationItem {
  sgg_code: string;
  sgg_name: string;
  lon: number;
  lat: number;
  risk_index: number;
  risk_index_new: number;
  risk_delta: number;
  ems_distance_km_new: number;
}

export interface SimulateResponse {
  avg_delta: number;
  max_drop: number;
  improved_count: number;
  items: SimulationItem[];
}

export interface ContrastItem {
  sgg_code: string;
  sgg_name: string;
  accident_count: number;
  accident_rank: number;
  risk_rank: number;
  rank_diff: number;
}

export interface ContrastResponse {
  blindzone_top10_not_in_accident_top10: number;
  accident_top10_not_in_blindzone_top10: number;
  items: ContrastItem[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  features_loaded: boolean;
  feature_count: number;
}
```

- [ ] **Step B.2.2**: api.ts

```typescript
// frontend/lib/api.ts
import type {
  FeatureSummary, FeatureDetail, SimulateResponse, HealthResponse,
  ContrastResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!resp.ok) throw new Error(`API ${path} failed: ${resp.status}`);
  return resp.json();
}

export const api = {
  health: () => fetchJson<HealthResponse>("/api/health"),
  listFeatures: () => fetchJson<FeatureSummary[]>("/api/features"),
  getFeature: (sggCode: string) => fetchJson<FeatureDetail>(`/api/features/${sggCode}`),
  top10: () => fetchJson<FeatureSummary[]>("/api/top10"),
  simulate: (virtualEms: [number, number][]) =>
    fetchJson<SimulateResponse>("/api/simulate", {
      method: "POST",
      body: JSON.stringify({ virtual_ems: virtualEms }),
    }),
  contrast: () => fetchJson<ContrastResponse>("/api/contrast"),
};
```

### Task B.3: .env.local.example

**Files:** Create: `frontend/.env.local.example`

- [ ] **Step B.3.1**: 작성

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

```powershell
Copy-Item .env.local.example .env.local
```

### Task B.4: Nav + layout

**Files:** Create: `frontend/components/Nav.tsx`, Modify: `frontend/app/layout.tsx`

- [ ] **Step B.4.1**: Nav.tsx — 동일 (v1 참조)

```tsx
import Link from "next/link";

export default function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">BlindZone</Link>
        <div className="flex gap-6 text-sm">
          <Link href="/" className="hover:underline">시민 모드</Link>
          <Link href="/policy" className="hover:underline">정책 시뮬레이터</Link>
          <Link href="/about" className="hover:underline">About</Link>
        </div>
      </div>
    </nav>
  );
}
```

- [ ] **Step B.4.2**: layout.tsx

```tsx
import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "BlindZone — 보이지 않던 위험지대",
  description: "사고 위험 × 응급 사각지대 융합 탐색 서비스 (탐색형 surrogate 모델)",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body className="bg-gray-50 text-gray-900">
        <Nav />
        <main className="max-w-7xl mx-auto px-6 py-8">{children}</main>
      </body>
    </html>
  );
}
```

### Task B.5: RiskMap 컴포넌트 (**`Map` shadowing 버그 fix, 외부 평가 5번**)

**Files:** Create: `frontend/components/RiskMap.tsx`

**핵심 fix**: `import Map` → `import MapLibreMap` 하고 `new Map(...)` → `new globalThis.Map(...)`.

- [ ] **Step B.5.1**: 작성 (버그 수정 적용)

```tsx
// frontend/components/RiskMap.tsx
"use client";

import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import MapLibreMap from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import type { FeatureSummary, SimulationItem } from "@/lib/types";

interface Props {
  features: FeatureSummary[];
  selectedSgg?: string | null;
  simulationItems?: SimulationItem[];
  virtualEms?: [number, number][];
  onClickFeature?: (sgg_code: string) => void;
}

const KOREA_VIEW = {
  longitude: 127.8,
  latitude: 36.5,
  zoom: 6,
};

function getColor(value: number, qmin: number, qmax: number): [number, number, number, number] {
  const norm = Math.max(0, Math.min(1, (value - qmin) / (qmax - qmin + 1e-9)));
  const r = Math.floor(255 * norm);
  const g = Math.floor(200 * (1 - norm));
  return [r, g, 64, 200];
}

function getDeltaColor(delta: number): [number, number, number, number] {
  if (delta < -0.001) return [44, 160, 44, 200];
  return [200, 200, 200, 120];
}

export default function RiskMap({
  features, selectedSgg, simulationItems, virtualEms, onClickFeature,
}: Props) {
  const layers = useMemo(() => {
    if (simulationItems && simulationItems.length > 0) {
      // globalThis.Map으로 명시 — react-map-gl의 Map 컴포넌트와 충돌 방지
      const itemMap = new globalThis.Map(simulationItems.map((s) => [s.sgg_code, s]));
      return [
        new ScatterplotLayer({
          id: "sim-points",
          data: features,
          getPosition: (d: FeatureSummary) => [d.lon, d.lat],
          getRadius: (d: FeatureSummary) => {
            const sim = itemMap.get(d.sgg_code);
            const delta = sim ? sim.risk_delta : 0;
            return Math.max(3000, Math.min(15000, Math.abs(delta) * 500000));
          },
          getFillColor: (d: FeatureSummary) => {
            const sim = itemMap.get(d.sgg_code);
            return getDeltaColor(sim ? sim.risk_delta : 0);
          },
          pickable: true,
        }),
        new ScatterplotLayer({
          id: "virtual-ems",
          data: virtualEms ?? [],
          getPosition: (d: [number, number]) => d,
          getRadius: 5000,
          getFillColor: [255, 0, 0, 220],
          stroked: true,
          getLineColor: [120, 0, 0, 220],
          lineWidthMinPixels: 2,
        }),
      ];
    }
    const risks = features.map((f) => f.risk_index);
    const sorted = [...risks].sort((a, b) => a - b);
    const qmin = sorted[Math.floor(sorted.length * 0.05)] ?? 0;
    const qmax = sorted[Math.floor(sorted.length * 0.95)] ?? 1;
    return [
      new ScatterplotLayer({
        id: "risk-points",
        data: features,
        getPosition: (d: FeatureSummary) => [d.lon, d.lat],
        getRadius: (d: FeatureSummary) =>
          d.sgg_code === selectedSgg ? 15000 : 6000,
        getFillColor: (d: FeatureSummary) =>
          getColor(d.risk_index, qmin, qmax),
        stroked: true,
        getLineColor: (d: FeatureSummary) =>
          d.sgg_code === selectedSgg ? [0, 0, 0, 255] : [0, 0, 0, 60],
        lineWidthMinPixels: 1,
        pickable: true,
        onClick: (info: { object?: FeatureSummary }) => {
          if (info.object && onClickFeature) onClickFeature(info.object.sgg_code);
        },
      }),
    ];
  }, [features, selectedSgg, simulationItems, virtualEms, onClickFeature]);

  return (
    <div className="relative w-full h-[600px] rounded-lg overflow-hidden border">
      <DeckGL
        initialViewState={KOREA_VIEW}
        controller={true}
        layers={layers}
        getTooltip={({ object }: { object?: FeatureSummary }) =>
          object && {
            html: `<div style="padding:8px;background:#fff;color:#111;border:1px solid #ccc;border-radius:4px">
              <b>${object.sgg_name}</b><br/>
              위험지수: ${object.risk_index.toFixed(3)}<br/>
              사고: ${object.accident_count}건<br/>
              응급도착 추정: ${object.ems_response_min.toFixed(1)}분
            </div>`,
            style: { background: "transparent", color: "#fff" },
          }
        }
      >
        <MapLibreMap
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          attributionControl={true}
        />
      </DeckGL>
      <div className="absolute bottom-2 left-2 bg-white/90 text-xs px-2 py-1 rounded">
        시군구 중심점 기준 · risk_index (탐색형)
      </div>
    </div>
  );
}
```

### Task B.6: MetricCard + ShapExplanation + Top10Table + ContrastPanel

**Files:** Create: 4개 컴포넌트

- [ ] **Step B.6.1**: MetricCard.tsx, ShapExplanation.tsx, Top10Table.tsx — v1 plan 코드 그대로 (Nav.tsx와 동일 패턴)

- [ ] **Step B.6.2**: ContrastPanel.tsx (신규)

```tsx
// frontend/components/ContrastPanel.tsx
"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { ContrastResponse } from "@/lib/types";

export default function ContrastPanel() {
  const [data, setData] = useState<ContrastResponse | null>(null);

  useEffect(() => {
    api.contrast().then(setData).catch(() => setData(null));
  }, []);

  if (!data) return null;

  return (
    <div className="bg-white border rounded-lg p-4 space-y-3">
      <h3 className="font-semibold">사고 빈도 지도와 BlindZone의 차이</h3>
      <p className="text-sm text-gray-700">
        BlindZone TOP10 중 <b>{data.blindzone_top10_not_in_accident_top10}곳</b>은
        사고건수 TOP10에 포함되지 않습니다. 즉 사고 빈도만 보면 덜 위험해 보이지만,
        응급 접근성을 결합하면 잠재 위험이 큰 지역입니다.
      </p>
      <div className="overflow-x-auto">
        <table className="w-full text-xs border">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-2 py-1 text-left">시군구</th>
              <th className="px-2 py-1 text-right">사고 순위</th>
              <th className="px-2 py-1 text-right">BlindZone 순위</th>
              <th className="px-2 py-1 text-right">순위 차이</th>
            </tr>
          </thead>
          <tbody>
            {data.items.slice(0, 12).map((it) => (
              <tr key={it.sgg_code} className="border-t">
                <td className="px-2 py-1">{it.sgg_name}</td>
                <td className="px-2 py-1 text-right">{it.accident_rank}</td>
                <td className="px-2 py-1 text-right">{it.risk_rank}</td>
                <td className="px-2 py-1 text-right">{it.rank_diff > 0 ? `+${it.rank_diff}` : it.rank_diff}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-gray-500">
        해석: 순위 차이가 큰 양수는 사고는 적은데 BlindZone에서 높은 위험으로 발굴된 곳 (응급 접근성 등 결합 효과).
      </p>
    </div>
  );
}
```

### Task B.7: 시민 모드 페이지 (+ ContrastPanel 통합)

**Files:** Modify: `frontend/app/page.tsx`

v1 plan의 page.tsx + ContrastPanel 추가.

- [ ] **Step B.7.1**: 작성 (v1 plan 페이지 기준, ContrastPanel 하단 추가)

(전체 코드는 v1 plan Task B.7과 동일 + 끝에 다음 추가)

```tsx
// page.tsx의 return 끝부분, Top10Table 다음에
      <ContrastPanel />
```

import 추가:
```tsx
import ContrastPanel from "@/components/ContrastPanel";
```

### Task B.8: 정책 시뮬레이터 페이지 (용어 통일)

**Files:** Create: `frontend/app/policy/page.tsx`

v1 plan 기준 + 용어 변경:
- "응급기관·분서" → "응급의료 거점"
- 부제: "가상 응급의료 거점을 추가하면 거리 기반 접근성이 어떻게 변하나? (정책 효과 예측 X — 민감도 분석)"

### Task B.9: About 페이지 (**정직성 8개 표현 정정 적용**)

**Files:** Create: `frontend/app/about/page.tsx`

- [ ] **Step B.9.1**: 작성 (정직성 정정 완료된 텍스트)

```tsx
// frontend/app/about/page.tsx
export default function AboutPage() {
  return (
    <article className="prose prose-gray max-w-3xl">
      <h1>About — BlindZone</h1>

      <h2>무엇을 푸는가</h2>
      <p>
        한국 교통사고 골든타임 대응 부족이 보도·연구에서 지적되어 왔다 (예: 머니S 2025-04-10 기사,
        "선진국 대비 사망률 2배"·"사고 후 1시간 내 수술실 도착률 50%"). 본 프로젝트는
        이러한 배경에서, 기존 사고 다발지도가 단순 사고 빈도에 초점을 둔다는 점에 주목하여,
        <b> 사고 빈도와 응급 의료 접근성을 결합한 탐색형 위험 지수</b>를 시군구 단위로 제공한다.
      </p>
      <p>
        BlindZone은 <b>사고 위험을 직접 예측하는 모델이 아니다.</b> 공개 데이터로 정의한
        잠재 위험지수를 계산·설명하고, 가상 응급의료 거점 추가 시 거리 기반 접근성 지표가
        어떻게 변하는지 보여주는 <b>탐색형 surrogate 도구</b>이다 (자세히는{" "}
        <code>docs/submission/model_card.md</code>).
      </p>

      <h2>사용한 데이터</h2>
      <ul>
        <li>전국교통사고다발지역표준데이터 (공공데이터포털, 한국도로교통공단 TAAS) — <b>전체 교통사고가 아닌 다발지점 데이터</b></li>
        <li>국립중앙의료원 응급의료기관 정보 (공공데이터포털 오픈 API, B552657)</li>
        <li>소방청 구급통계서비스 (공공데이터포털 오픈 API, 1661000) — <b>출동시간 raw 비공개, 본 프로젝트는 응급기관 거리 기반 추정 사용</b></li>
        <li>시군구 행정구역 경계 — 통계청 (센서스경계)시군구경계 (브이월드 다운로드, <b>CC BY-NC-ND</b> 라이선스)</li>
      </ul>

      <h2>방법론</h2>
      <ol>
        <li>시군구 단위 변수 산출: 사고 빈도(TAAS 다발지역 내), 사망사고 비율, 응급의료기관까지 거리(km), 응급 도착 추정 시간(거리×60km/h 가정), 면적</li>
        <li>변수들의 min-max 정규화 후 가중합 (0.4/0.3/0.3) → <b>잠재 위험 지수</b> 정의</li>
        <li>XGBoost 회귀로 정의된 위험 지수를 재학습 → <b>SHAP 값으로 시군구별 상위 기여 요인 추출</b> (사고 예측이 아닌 surrogate 설명)</li>
        <li>가상 응급의료 거점 추가 시뮬레이션: 거리 피처 재계산 + 동일 모델 inference → 위험 지수 변화 (정책 효과 예측 X, 거리 기반 접근성 민감도 분석)</li>
      </ol>

      <h2>한계 및 정직 고지</h2>
      <ul>
        <li>본 모델은 실제 사고 또는 사망을 예측하지 않는다. 정의된 위험지수에 대한 surrogate model이며, R²=0.90은 사고 예측 성능이 아니라 정의식 재현도다.</li>
        <li>TAAS 사고다발지역 데이터는 전체 사고 X — 다발지점 한정. "연간 사고 건수"라는 표현 대신 "TAAS 사고다발지역 데이터 내 사고 건수".</li>
        <li>119 출동 사건별 raw 비공개로 응급 도착시간은 응급기관 거리 + 평균 속도(60km/h) 가정 추정.</li>
        <li>시군구 단위 평균 — 격자 내 변동성 평준화 (V1.1에서 1km 격자 검토).</li>
        <li>가중치 0.4/0.3/0.3은 실증 근거 없이 선택한 임의 설정. 다른 가중치 조합 시 결과 달라질 수 있음.</li>
      </ul>

      <h2>가점 신청 항목</h2>
      <p>아래 항목으로 가점 신청 (부여 여부는 심사위원단 판단):</p>
      <ul>
        <li>AI 학습도구 (5점 신청): Claude Code를 코딩 보조로 활용. 사용 기록·기여 증빙은 별도 첨부 (<code>docs/submission/ai-tool-evidence.md</code>)</li>
        <li>AI 분석도구 (5점 신청): XGBoost 회귀 + SHAP TreeExplainer</li>
        <li>데이터 융합 (5점 신청): 공공데이터 4종을 시군구 단위로 결합 (TAAS × 응급의료기관 × 119 통계 × 행정경계)</li>
      </ul>
    </article>
  );
}
```

### Task B.10: 타입 체크 + 빌드 검증

```powershell
cd frontend
npx tsc --noEmit
npm run build
```

Expected: 타입 에러 0, 빌드 성공.

### Task B.11: 로컬 동작 확인 (한태영 직접)

- [ ] 백엔드 + 프론트 동시 실행 → 3개 페이지 + 새 ContrastPanel 동작 확인

### Task B.12: Phase B commit

```powershell
cd ..
git add frontend/
git commit -m "feat(frontend): Next.js 14 풀스택 — 3 페이지, RiskMap Map shadowing 버그 fix, ContrastPanel, 정직성 표현 적용"
```

---

## Phase C: 배포

### Task C.1: Railway 백엔드 배포 (requirements-api.txt 사용)

**Files:** Create: `backend/Procfile`, `backend/railway.json` (선택)

- [ ] **Step C.1.1**: Procfile

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

- [ ] **Step C.1.2**: railway.json (build 시 requirements-api.txt 사용)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements-api.txt"
  },
  "deploy": {
    "startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

- [ ] **Step C.1.3**: [한태영 액션] Railway 배포 (v1 plan과 동일)
- [ ] **Step C.1.4**: `/api/health` 200 확인

### Task C.2: Vercel 프론트 배포

(v1 plan과 동일)

### Task C.3: CORS 갱신 + 통합 동작 검증

(v1 plan과 동일)

---

## Phase D: 정정 + 제출 패키지

### Task D.0: 공식 제출서류 확인 (**외부 평가 1번**, 신규)

**Files:** Create: `docs/submission/checklist.md`

[한태영 액션 위주]

- [ ] **Step D.0.1**: 국토교통부 통계누리 공지 (https://stat.molit.go.kr/portal/notice/noticeView.do?gubun=1&hNum=283)에서 `경진대회_참가서류.zip` 다운로드
- [ ] **Step D.0.2**: zip 안의 파일 확인 — **참가신청서**, **서약서**, **기획서 HWP 양식** 3종 추출
- [ ] **Step D.0.3**: `docs/submission/checklist.md` 작성

```markdown
# 제출 서류 체크리스트

대회: 2026 국토교통 데이터 활용 경진대회 (제품/서비스 트랙)
출처: 국토교통부 통계누리 공지 hNum=283

## 필수 제출 (1차)
- [ ] 참가신청서 (HWP) — 한태영 작성
- [ ] 서약서 (HWP) — 한태영 서명
- [ ] 기획서 (HWP, 최대 3장) — 한태영 작성, 메인 텍스트 초안 제공 가능
- [ ] 시제품 URL (Vercel 프론트) — 배포 후
- [ ] 시제품 API URL (Railway) — 배포 후
- [ ] 기타 첨부 자료
  - [ ] 데모 영상 (1~2분)
  - [ ] AI 학습도구 증빙 (`docs/submission/ai-tool-evidence.md`)
  - [ ] data_manifest.md (선택)
  - [ ] model_card.md (선택)

## 제출 채널
- 국가교통 데이터 오픈마켓 (https://www.bigdata-transportation.kr) 또는 통계누리 안내 채널
- 접수 마감: 2026-05-29
```

- [ ] **Step D.0.4**: 빈 양식들을 `docs/submission/forms/` 에 보관

### Task D.1: README 정정

**Files:** Modify: `README.md`

v1 plan Task D.1 + 정직성 정정 적용 (자세히 PROJECT_SPEC의 8개 위험표현 표).

### Task D.2: AI 학습도구 증빙 자료

**Files:** Create: `docs/submission/ai-tool-evidence.md`

v1 plan Task D.2 동일.

### Task D.3: 대표 사례 발굴 (**외부 평가 7번 강화**, 신규)

**Files:** Create: `docs/submission/case-study.md`

발표·기획서에 사용할 대표 시군구 1개를 골라 "사고건수 N위, BlindZone 순위 Y위, 핵심 SHAP 요인 ..." 형태로 1페이지 정리.

- [ ] **Step D.3.1**: `/api/contrast` 응답에서 rank_diff 큰 순으로 1~3개 후보 추출

```powershell
cd backend
..\.venv\Scripts\python.exe -c "import requests, json; r = requests.get('http://localhost:8000/api/contrast').json(); items = sorted(r['items'], key=lambda x: -x['rank_diff'])[:5]; print(json.dumps(items, ensure_ascii=False, indent=2))"
```

- [ ] **Step D.3.2**: 한태영과 메인이 함께 대표 1개 선정 → `docs/submission/case-study.md` 작성

```markdown
# 대표 사례 — [선정 시군구]

| 지표 | 값 |
|---|---|
| 사고건수 순위 (TAAS 다발지역) | N위 |
| BlindZone 위험지수 순위 | Y위 |
| 순위 차이 | +(N-Y) — 잠재 위험 발굴 |
| SHAP 상위 1: ... | ... |
| 응급기관 거리 | ... km |
| 추정 도착 시간 | ... 분 |

발표 한 줄: "이 지역은 사고건수만 보면 N위지만, 응급 접근성을 결합하면 Y위로 부상한다. 데이터로 발굴한 통계 사각지대다."
```

### Task D.4: 기획서 작성 [한태영 액션]

v1 plan Task D.3 동일 + 정직성 정정 + 대표 사례 인용 + 외부 평가 권장 흐름:
1. 기존 사고다발지도는 빈도 중심
2. BlindZone은 응급 접근성 결합 탐색
3. 결과: 통계 사각지대 N곳 발굴 (`/api/contrast`)
4. 가상 응급의료 거점 추가 시 거리 기반 접근성 변화 (정책 효과 예측 X)
5. 한계 고지

### Task D.5: 데모 영상 [한태영 액션]

v1 plan Task D.4 동일 + 시나리오 강화:
- 대표 사례 1개 등장
- "단, 본 결과는 정책 효과 예측이 아니라 데이터 기반 탐색 시뮬레이션입니다" 마지막 멘트

### Task D.6: 최종 점검 + 제출 [한태영 액션]

체크리스트:
- [ ] Vercel URL 3 페이지 동작
- [ ] Railway API health 200
- [ ] README 데이터 출처·라이선스 정확
- [ ] About 정직성 표현 적용
- [ ] data_manifest, model_card, external-review, case-study, ai-tool-evidence 5종 보관
- [ ] 기획서 (3장, 한글 양식)
- [ ] 데모 영상
- [ ] 참가신청서 + 서약서 (필수)
- [ ] 접수 완료 (마감 2026-05-29)

---

## Self-Review

### 외부 평가 권장사항 반영 매트릭스

| # | 권장사항 | 반영 위치 |
|---|---|---|
| 1 | 공식 제출서류 선확보 | Task D.0 |
| 2 | data_manifest + model_card | 이미 작성 (commit) + Task D.6 점검 |
| 3 | GeoJSON 출처 — 30015 (대안) | 한태영 결정: 통계청 (센서스경계) VWORLD SHP — 외부 평가 권장 정신 부합 |
| 4 | SHAP 사전 계산 | Task A.0 (`precompute_shap.py`), Task A.3 (deps 변경), Task A.7 (detail endpoint) |
| 5 | RiskMap Map shadowing fix | Task B.5 (`MapLibreMap` rename + `globalThis.Map`) |
| 6 | 응급 거점 용어 통일 | Task B.8 (정책 페이지), Task B.9 (About), Task D.1 (README) |
| 7 | 사고 vs BlindZone 비교 | Task A.10 (`/api/contrast`), Task B.6 (`ContrastPanel`), Task D.3 (대표 사례) |
| 8 | About/README 정직 | Task B.9 (About), Task D.1 (README) — 8개 위험표현 정정 |
| 9 | 배포용 의존성 분리 | Task A.1 (`requirements-api.txt`), Task C.1 (railway.json buildCommand) |
| 10 | 일정 재조정 | 한태영 결정: 기한 무관 모드 — strict 일정 적용 X |

### Spec coverage

- 모든 PROJECT_SPEC 항목 매핑 OK
- 정직성 8개 표현 — Task B.9, D.1 정정
- 가점 신청 약화 — 약화된 표현 사용
- 1차 양식 (기획서 3장, 시제품 URL) — Task D.0, D.4, D.6

### Placeholder scan

- TBD/TODO 없음
- 한태영 액션 명시: Task D.0, D.4, D.5, D.6의 일부

### Type consistency

- Pydantic schemas와 TypeScript types 1:1 매핑 (ContrastItem/ContrastResponse 신규 포함)
- API path와 frontend api.ts 일치

---

## 다음 단계

1. **한태영 plan v2 리뷰** — 통째로 OK 받기
2. Execution: `superpowers:subagent-driven-development` (추천) 또는 `executing-plans`
3. Phase A.0 (SHAP 사전 계산)부터 순차 실행
