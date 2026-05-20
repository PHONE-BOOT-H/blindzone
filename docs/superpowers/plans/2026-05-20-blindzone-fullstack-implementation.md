# BlindZone Fullstack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Streamlit prototype을 풀스택(Next.js + FastAPI) 시제품으로 전환하고, 시군구 GeoJSON을 정확한 출처로 갱신하고, Vercel + Railway에 배포해 BlindZone을 2026 국토교통 데이터 활용 경진대회에 제출 가능한 상태로 만든다.

**Architecture:** 백엔드는 FastAPI로 기존 XGBoost 모델·SHAP·시뮬레이션을 HTTP endpoint로 wrap. 프론트엔드는 Next.js 14 (App Router) + TypeScript + Tailwind, 지도는 MapLibre GL + deck.gl, 차트는 Recharts. 백엔드는 Railway, 프론트는 Vercel에 배포하고 환경변수로 연결.

**Tech Stack:**
- Backend: FastAPI, uvicorn, pydantic, 기존 xgboost/shap/geopandas/pandas
- Frontend: Next.js 14, TypeScript, Tailwind CSS, MapLibre GL JS, deck.gl, Recharts
- Deploy: Railway (backend), Vercel (frontend)

---

## Spec Reference

- `docs/PROJECT_SPEC.md` — 풀스택 architecture, 심사 기준, 가점 신청
- `docs/superpowers/specs/2026-05-19-blindzone-design.md` — 원본 디자인 spec (Streamlit 시기, 컨셉·모델·데이터는 유효)
- Deprecated: `docs/superpowers/plans/2026-05-19-blindzone-streamlit-implementation-deprecated.md` (참고용 history)

**절대 원칙**: 없는 것을 지어내지 않는다 — 데이터·통계·작동결과·가점 모두 검증된 사실만. 모호하면 명시 마킹.

---

## File Structure

```
project-root/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app + CORS
│   │   ├── routes.py           # 5개 endpoint
│   │   ├── schemas.py          # Pydantic models
│   │   └── deps.py             # 모델·데이터 싱글톤 로더
│   ├── src/                    # 기존 ML 코드 (변경 없음)
│   ├── data/, models/          # 기존
│   ├── scripts/                # 기존
│   ├── tests/
│   │   ├── test_data_pipeline.py  # 기존
│   │   ├── test_train.py          # 기존
│   │   └── test_api.py            # 신규 — endpoint 통합 테스트
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── layout.tsx          # 공통 레이아웃
│   │   ├── page.tsx            # 시민 모드 (/)
│   │   ├── policy/page.tsx     # 정책 시뮬레이터 (/policy)
│   │   ├── about/page.tsx      # About (/about)
│   │   └── globals.css         # Tailwind
│   ├── components/
│   │   ├── Nav.tsx             # 상단 네비
│   │   ├── RiskMap.tsx         # MapLibre + deck.gl 지도
│   │   ├── SearchSelect.tsx    # 시군구 검색
│   │   ├── MetricCard.tsx      # 메트릭 카드
│   │   ├── ShapExplanation.tsx # SHAP 설명 리스트
│   │   ├── Top10Table.tsx      # TOP 10 테이블
│   │   └── PolicySimulator.tsx # 정책 시뮬레이터 폼·결과
│   ├── lib/
│   │   ├── api.ts              # API 클라이언트
│   │   └── types.ts            # TypeScript 타입 (백엔드 schema 미러)
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.mjs
│   └── .env.local.example
├── docs/, .gitignore, README.md
```

---

## Testing Strategy

- **Backend unit/integration**: pytest. 기존 11 + train 1 + 신규 api 5~6
- **Backend endpoint manual**: `curl` 또는 `httpie` 로 5개 endpoint 검증
- **Frontend manual**: Next.js dev server 띄우고 브라우저 확인 (한태영이 직접)
- **Frontend type check**: `tsc --noEmit` 으로 타입 안전성
- **배포 검증**: 배포 후 URL 직접 접속 → 모든 페이지 로드 + API 호출 동작 확인

---

## Phase 0: 시군구 GeoJSON 새 출처 갱신

### Task 0.1: [한태영 액션] VWORLD에서 시군구 경계 다운로드

**Files:** Modify: `backend/data/raw/시군구_경계.geojson` (또는 SHP 셋)

- [ ] **Step 0.1.1**: 한태영이 https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?dsId=30604 접속, 로그인 후 시군구 경계 zip 다운로드
- [ ] **Step 0.1.2**: 한태영이 zip 풀어서 `backend/data/raw/` 안에 배치 (파일명: `시군구_경계.shp/.dbf/.shx/.prj` 또는 변환된 `시군구_경계.geojson`). 기존 출처 미확인 파일 위에 덮어쓰기

### Task 0.2: 새 GeoJSON inspect + 매핑 조정

**Files:** Modify: `backend/src/data_pipeline.py` (필요 시)

- [ ] **Step 0.2.1**: inspect 실행

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\inspect_data.py
```

Expected: 시군구 데이터의 shape, columns, CRS 출력.

- [ ] **Step 0.2.2**: columns 결과를 보고 `load_sgg_centers`의 column finder가 매칭하는지 확인. VWORLD 표준 컬럼명은 `SIG_CD`, `SIG_KOR_NM` 또는 `BJCD/SGG_NM`. 매칭 안 되면 `load_sgg_centers`의 finder pattern에 추가:

```python
# backend/src/data_pipeline.py — 필요 시 추가
code_col = next(
    (c for c in gdf.columns
     if "SIG_CD" in c.upper() or "시군구코드" in c or c.lower() == "code"
     or c.upper() == "BJCD" or c.upper() == "SGG_CD"),
    None,
)
name_col = next(
    (c for c in gdf.columns
     if "KOR_NM" in c.upper() or "시군구명" in c or c.lower() == "name"
     or c.upper() == "BJNM" or c.upper() == "SGG_NM"),
    None,
)
```

- [ ] **Step 0.2.3**: tests/test_data_pipeline.py 전체 다시 실행 (`pytest -v`) → 11 PASS 유지 확인

### Task 0.3: build_features + train 재실행

**Files:** Regenerate: `backend/data/processed/grid_features.parquet`, `backend/models/xgb_risk_model.pkl`

- [ ] **Step 0.3.1**: build_features 실행

```powershell
cd backend
..\.venv\Scripts\python.exe scripts\build_features.py
```

Expected: "사고 행 매핑 실패: N / 12,780건" 출력, 매핑 실패율 5% 미만 (이전엔 0%). 5% 넘으면 SIDO_NAME_TO_PREFIX 또는 _TAAS_NAME_ALIAS 보강 후 재시도.

- [ ] **Step 0.3.2**: 결과 검증

```powershell
..\.venv\Scripts\python.exe -c "import pandas as pd; df = pd.read_parquet('data/processed/grid_features.parquet'); print(df.shape, df.isnull().sum().sum()); print(df.head(3))"
```

Expected: shape (250, 12) 근처 (시군구 수가 다를 수도 — VWORLD 데이터에 따라). NaN 0. 컬럼 동일.

- [ ] **Step 0.3.3**: 모델 재학습

```powershell
..\.venv\Scripts\python.exe -m src.train
```

Expected: R² > 0.5, MAE < 0.1. saved to models/xgb_risk_model.pkl

- [ ] **Step 0.3.4**: 인사이트 강도 재검증

```powershell
..\.venv\Scripts\python.exe scripts\check_insight.py
```

Expected: "V1 시군구 단위 OK" 판정 (blind zone ≥ 10개).

### Task 0.4: Phase 0 commit

- [ ] **Step 0.4.1**: 커밋

```powershell
cd ..
git add backend/data/processed/grid_features.parquet backend/models/xgb_risk_model.pkl backend/src/data_pipeline.py
git commit -m "data: 시군구 경계 VWORLD 출처(dsId=30604)로 갱신 + 모델 재학습"
```

---

## Phase A: FastAPI 백엔드

### Task A.1: FastAPI 의존성 설치 + 디렉토리 골격

**Files:**
- Create: `backend/api/__init__.py`, `backend/api/main.py`, `backend/api/routes.py`, `backend/api/schemas.py`, `backend/api/deps.py`

- [ ] **Step A.1.1**: 의존성 설치

```powershell
cd backend
..\.venv\Scripts\pip.exe install -r requirements.txt
```

Expected: fastapi, uvicorn, pydantic 신규 설치.

- [ ] **Step A.1.2**: 빈 파일 일괄 생성

```powershell
New-Item -ItemType Directory -Force -Path api
New-Item -ItemType File -Force -Path api\__init__.py, api\main.py, api\routes.py, api\schemas.py, api\deps.py
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
        description="가상 응급기관 좌표 [(lon, lat), ...]"
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


class HealthResponse(BaseModel):
    status: str  # "ok"
    model_loaded: bool
    features_loaded: bool
    feature_count: int
```

### Task A.3: 데이터·모델 싱글톤 로더

**Files:** Create: `backend/api/deps.py`

- [ ] **Step A.3.1**: 작성

```python
# backend/api/deps.py
"""모델·데이터 싱글톤 로드 (모듈 import 시 1회)."""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import pandas as pd

# backend/ 디렉토리를 sys.path에 추가 (uvicorn 실행 시 보장 위해)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.config import GRID_FEATURES_PATH, MODEL_PATH  # noqa: E402

_features: pd.DataFrame | None = None
_model_bundle: dict | None = None


def get_features() -> pd.DataFrame:
    global _features
    if _features is None:
        _features = pd.read_parquet(GRID_FEATURES_PATH)
    return _features


def get_model_bundle() -> dict:
    global _model_bundle
    if _model_bundle is None:
        with open(MODEL_PATH, "rb") as f:
            _model_bundle = pickle.load(f)
    return _model_bundle
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
    description="사고 위험 × 응급 사각지대 분석 API",
    version="0.1.0",
)

# CORS: 개발 시 localhost, 배포 시 Vercel 도메인 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        # 실제 Vercel 배포 후 정확한 도메인 추가
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

- [ ] **Step A.5.1**: routes.py 초기 작성

```python
# backend/api/routes.py
from fastapi import APIRouter, HTTPException

from api import schemas
from api.deps import get_features, get_model_bundle

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

- [ ] **Step A.5.2**: 로컬 실행 검증

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
```

(별도 터미널에서)
```powershell
curl http://localhost:8000/api/health
```

Expected: `{"status":"ok","model_loaded":true,"features_loaded":true,"feature_count":250}` (시군구 수는 VWORLD 데이터에 따라).

확인 후 uvicorn 종료 (Ctrl+C).

### Task A.6: GET /api/features endpoint

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.6.1**: 추가

```python
@router.get("/features", response_model=list[schemas.FeatureSummary])
def list_features():
    df = get_features()
    cols = ["sgg_code", "sgg_name", "lon", "lat", "risk_index",
            "accident_count", "fatality_rate", "ems_distance_km", "ems_response_min"]
    df_small = df[cols].copy()
    df_small["accident_count"] = df_small["accident_count"].astype(int)
    return df_small.to_dict(orient="records")
```

- [ ] **Step A.6.2**: 검증 (uvicorn 재시작 후)

```powershell
curl "http://localhost:8000/api/features" -o features.json
.venv\Scripts\python.exe -c "import json; data = json.load(open('features.json', encoding='utf-8')); print(len(data), data[0])"
```

Expected: 250개 항목, 첫 항목 sgg_code/sgg_name/lon/lat/risk_index 등 포함.

### Task A.7: GET /api/features/{sgg_code} endpoint

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

    # SHAP 계산
    from src.shap_explain import explain_one
    try:
        shap_list = explain_one(row)
    except Exception as exc:
        shap_list = []  # SHAP 실패해도 detail은 반환

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

Expected: 종로구 상세 + shap_top 3개 항목.

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

- [ ] **Step A.8.2**: 검증

```powershell
curl "http://localhost:8000/api/top10"
```

Expected: 10개 항목 risk_index 내림차순.

### Task A.9: POST /api/simulate endpoint

**Files:** Modify: `backend/api/routes.py`

- [ ] **Step A.9.1**: 추가

```python
@router.post("/simulate", response_model=schemas.SimulateResponse)
def simulate(req: schemas.SimulateRequest):
    from src.inference import simulate_new_ems

    result = simulate_new_ems(list(req.virtual_ems))
    # result 컬럼: features 원본 + risk_index_new + risk_delta + ems_distance_km_new

    avg_delta = float(result["risk_delta"].mean())
    max_drop = float(result["risk_delta"].min())
    improved_count = int((result["risk_delta"] < -0.001).sum())

    items_df = result.nsmallest(50, "risk_delta")[[
        "sgg_code", "sgg_name", "lon", "lat",
        "risk_index", "risk_index_new", "risk_delta", "ems_distance_km_new"
    ]].copy()
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
        for _, r in items_df.iterrows()
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

Expected: avg_delta, max_drop, improved_count, items (50개) 응답.

### Task A.10: API 통합 테스트 (pytest + FastAPI TestClient)

**Files:** Create: `backend/tests/test_api.py`

- [ ] **Step A.10.1**: 테스트 작성

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
    first = body[0]
    assert {"sgg_code", "sgg_name", "lon", "lat", "risk_index"}.issubset(first.keys())


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
```

- [ ] **Step A.10.2**: 실행

```powershell
cd backend
..\.venv\Scripts\python.exe -m pytest tests/test_api.py -v
```

Expected: 7 PASS.

### Task A.11: Phase A commit

- [ ] **Step A.11.1**: 커밋

```powershell
cd ..
git add backend/api backend/tests/test_api.py
git commit -m "feat(api): FastAPI 백엔드 — 5개 endpoint (health, features, detail, top10, simulate) + 7 통합 테스트"
```

---

## Phase B: Next.js 프론트엔드

### Task B.1: Next.js init

**Files:** Create: `frontend/` 전체 (Next.js 자동 생성)

- [ ] **Step B.1.1**: frontend/.gitkeep 삭제 후 Next.js init

```powershell
Remove-Item frontend\.gitkeep
cd frontend
npx create-next-app@14 . --typescript --tailwind --app --no-src-dir --import-alias "@/*" --eslint
```

Prompts에 다음으로 답:
- Would you like to use ESLint? **Yes**
- Would you like to use Tailwind CSS? **Yes** (이미 명령에서 지정)
- Would you like to use `src/` directory? **No** (--no-src-dir)
- Would you like to use App Router? **Yes** (--app)
- Customize the default import alias (@/*)? **No** (--import-alias "@/*")

Expected: frontend/ 안에 package.json, tsconfig.json, app/, public/, tailwind.config.ts 등 생성.

- [ ] **Step B.1.2**: 동작 확인

```powershell
npm run dev
```

브라우저 http://localhost:3000 접속 → 기본 Next.js 페이지 보임. Ctrl+C로 종료.

- [ ] **Step B.1.3**: 추가 의존성 설치

```powershell
npm install maplibre-gl react-map-gl deck.gl @deck.gl/react @deck.gl/layers @deck.gl/geo-layers recharts
```

Expected: package.json에 dependencies 추가.

- [ ] **Step B.1.4**: shadcn/ui (선택) — 우선 skip. 직접 Tailwind로 진행.

### Task B.2: TypeScript 타입 + API 클라이언트

**Files:** Create: `frontend/lib/api.ts`, `frontend/lib/types.ts`

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
  FeatureSummary,
  FeatureDetail,
  SimulateResponse,
  HealthResponse,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!resp.ok) {
    throw new Error(`API ${path} failed: ${resp.status}`);
  }
  return resp.json();
}

export const api = {
  health: () => fetchJson<HealthResponse>("/api/health"),
  listFeatures: () => fetchJson<FeatureSummary[]>("/api/features"),
  getFeature: (sggCode: string) =>
    fetchJson<FeatureDetail>(`/api/features/${sggCode}`),
  top10: () => fetchJson<FeatureSummary[]>("/api/top10"),
  simulate: (virtualEms: [number, number][]) =>
    fetchJson<SimulateResponse>("/api/simulate", {
      method: "POST",
      body: JSON.stringify({ virtual_ems: virtualEms }),
    }),
};
```

### Task B.3: .env.local.example + 환경변수

**Files:** Create: `frontend/.env.local.example`

- [ ] **Step B.3.1**: 작성

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

- [ ] **Step B.3.2**: 본인 환경용 `.env.local` 생성 (gitignore)

```powershell
Copy-Item .env.local.example .env.local
```

### Task B.4: 공통 레이아웃 + 네비게이션

**Files:** Modify: `frontend/app/layout.tsx`, Create: `frontend/components/Nav.tsx`

- [ ] **Step B.4.1**: Nav.tsx 작성

```tsx
// frontend/components/Nav.tsx
import Link from "next/link";

export default function Nav() {
  return (
    <nav className="border-b bg-white">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-xl font-bold">
          BlindZone
        </Link>
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

- [ ] **Step B.4.2**: layout.tsx 수정

```tsx
// frontend/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "BlindZone — 보이지 않던 위험지대",
  description: "사고 위험 × 응급 사각지대 융합 발굴 서비스",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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

### Task B.5: 지도 컴포넌트 (MapLibre + deck.gl)

**Files:** Create: `frontend/components/RiskMap.tsx`

- [ ] **Step B.5.1**: 작성

```tsx
// frontend/components/RiskMap.tsx
"use client";

import { useMemo } from "react";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import Map from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

import type { FeatureSummary, SimulationItem } from "@/lib/types";

interface Props {
  features: FeatureSummary[];
  selectedSgg?: string | null;
  simulationItems?: SimulationItem[];  // 정책 모드용 (delta 색칠)
  virtualEms?: [number, number][];      // 정책 모드용 (가상 응급기관 marker)
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
  if (delta < -0.001) return [44, 160, 44, 200]; // 개선 = 녹색
  return [200, 200, 200, 120]; // 변화 없음 = 회색
}

export default function RiskMap({
  features,
  selectedSgg,
  simulationItems,
  virtualEms,
  onClickFeature,
}: Props) {
  const layers = useMemo(() => {
    if (simulationItems && simulationItems.length > 0) {
      // 정책 모드: 시뮬레이션 결과 색칠
      const itemMap = new Map(simulationItems.map((s) => [s.sgg_code, s]));
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
    // 시민 모드: risk_index 색칠
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
          if (info.object && onClickFeature) {
            onClickFeature(info.object.sgg_code);
          }
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
              응급도착: ${object.ems_response_min.toFixed(1)}분
            </div>`,
            style: { background: "transparent", color: "#fff" },
          }
        }
      >
        <Map
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
          attributionControl={true}
        />
      </DeckGL>
    </div>
  );
}
```

### Task B.6: MetricCard + ShapExplanation + Top10Table 컴포넌트

**Files:** Create: `frontend/components/MetricCard.tsx`, `frontend/components/ShapExplanation.tsx`, `frontend/components/Top10Table.tsx`

- [ ] **Step B.6.1**: MetricCard.tsx

```tsx
// frontend/components/MetricCard.tsx
export default function MetricCard({
  label,
  value,
  unit,
}: {
  label: string;
  value: string | number;
  unit?: string;
}) {
  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <div className="text-xs text-gray-500 mb-1">{label}</div>
      <div className="text-2xl font-semibold">
        {value}
        {unit && <span className="text-sm text-gray-500 ml-1">{unit}</span>}
      </div>
    </div>
  );
}
```

- [ ] **Step B.6.2**: ShapExplanation.tsx

```tsx
// frontend/components/ShapExplanation.tsx
import type { ShapItem } from "@/lib/types";

export default function ShapExplanation({ items }: { items: ShapItem[] }) {
  if (items.length === 0) {
    return <div className="text-sm text-gray-500">설명 로드 실패</div>;
  }
  return (
    <ul className="space-y-2">
      {items.map((item) => {
        const arrow = item.shap_value > 0 ? "↑" : "↓";
        const color = item.shap_value > 0 ? "text-red-600" : "text-green-600";
        return (
          <li key={item.feature} className="flex items-center gap-2">
            <span className={`font-medium ${color}`}>{arrow}</span>
            <span className="font-medium">{item.feature}</span>
            <span className="text-sm text-gray-500">
              (영향도 {item.shap_value >= 0 ? "+" : ""}
              {item.shap_value.toFixed(3)})
            </span>
          </li>
        );
      })}
    </ul>
  );
}
```

- [ ] **Step B.6.3**: Top10Table.tsx

```tsx
// frontend/components/Top10Table.tsx
import type { FeatureSummary } from "@/lib/types";

export default function Top10Table({ items }: { items: FeatureSummary[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border">
        <thead className="bg-gray-100">
          <tr>
            <th className="px-3 py-2 text-left">시군구</th>
            <th className="px-3 py-2 text-right">위험지수</th>
            <th className="px-3 py-2 text-right">사고건수</th>
            <th className="px-3 py-2 text-right">사망사고비율</th>
            <th className="px-3 py-2 text-right">평균출동(분)</th>
            <th className="px-3 py-2 text-right">응급기관거리(km)</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row) => (
            <tr key={row.sgg_code} className="border-t">
              <td className="px-3 py-2">{row.sgg_name}</td>
              <td className="px-3 py-2 text-right">
                {row.risk_index.toFixed(3)}
              </td>
              <td className="px-3 py-2 text-right">{row.accident_count}</td>
              <td className="px-3 py-2 text-right">
                {row.fatality_rate.toFixed(3)}
              </td>
              <td className="px-3 py-2 text-right">
                {row.ems_response_min.toFixed(1)}
              </td>
              <td className="px-3 py-2 text-right">
                {row.ems_distance_km.toFixed(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Task B.7: 시민 모드 페이지

**Files:** Modify: `frontend/app/page.tsx`

- [ ] **Step B.7.1**: 작성

```tsx
// frontend/app/page.tsx
"use client";

import { useEffect, useState } from "react";
import RiskMap from "@/components/RiskMap";
import MetricCard from "@/components/MetricCard";
import ShapExplanation from "@/components/ShapExplanation";
import Top10Table from "@/components/Top10Table";
import { api } from "@/lib/api";
import type { FeatureSummary, FeatureDetail } from "@/lib/types";

export default function CitizenPage() {
  const [features, setFeatures] = useState<FeatureSummary[]>([]);
  const [top, setTop] = useState<FeatureSummary[]>([]);
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  const [detail, setDetail] = useState<FeatureDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([api.listFeatures(), api.top10()])
      .then(([f, t]) => {
        setFeatures(f);
        setTop(t);
      })
      .catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    if (!selectedCode) {
      setDetail(null);
      return;
    }
    api.getFeature(selectedCode).then(setDetail).catch((e) => setError(String(e)));
  }, [selectedCode]);

  if (error) return <div className="text-red-600">에러: {error}</div>;

  const sortedNames = [...features]
    .map((f) => f.sgg_name)
    .sort((a, b) => a.localeCompare(b, "ko"));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">우리 동네 응급 사각지대 확인</h1>
        <p className="text-gray-600">
          사고는 적은데 죽음은 많은 곳 — 데이터로 발굴한 잠재 위험지대
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">지역 검색</label>
            <select
              className="w-full border rounded px-3 py-2"
              value={selectedCode ?? ""}
              onChange={(e) => setSelectedCode(e.target.value || null)}
            >
              <option value="">시군구를 선택하세요</option>
              {features.map((f) => (
                <option key={f.sgg_code} value={f.sgg_code}>
                  {f.sgg_name}
                </option>
              ))}
            </select>
          </div>

          {detail && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <MetricCard
                  label="잠재 위험 지수"
                  value={detail.risk_index.toFixed(3)}
                />
                <MetricCard
                  label="연간 사고 건수"
                  value={detail.accident_count}
                  unit="건"
                />
                <MetricCard
                  label="평균 응급 도착시간"
                  value={detail.ems_response_min.toFixed(1)}
                  unit="분"
                />
                <MetricCard
                  label="응급기관 거리"
                  value={detail.ems_distance_km.toFixed(1)}
                  unit="km"
                />
              </div>
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold mb-2">왜 위험한가</h3>
                <ShapExplanation items={detail.shap_top} />
              </div>
            </>
          )}
        </div>

        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold mb-3">전국 위험지도</h2>
          <RiskMap
            features={features}
            selectedSgg={selectedCode}
            onClickFeature={setSelectedCode}
          />
        </div>
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-3">전국 상위 잠재 위험지대 TOP 10</h2>
        <Top10Table items={top} />
      </div>
    </div>
  );
}
```

### Task B.8: 정책 시뮬레이터 페이지

**Files:** Create: `frontend/app/policy/page.tsx`

- [ ] **Step B.8.1**: 작성

```tsx
// frontend/app/policy/page.tsx
"use client";

import { useEffect, useState } from "react";
import RiskMap from "@/components/RiskMap";
import MetricCard from "@/components/MetricCard";
import { api } from "@/lib/api";
import type { FeatureSummary, SimulateResponse } from "@/lib/types";

export default function PolicyPage() {
  const [features, setFeatures] = useState<FeatureSummary[]>([]);
  const [virtualEms, setVirtualEms] = useState<[number, number][]>([]);
  const [lonInput, setLonInput] = useState("127.0");
  const [latInput, setLatInput] = useState("37.5");
  const [sim, setSim] = useState<SimulateResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listFeatures().then(setFeatures).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    api.simulate(virtualEms).then(setSim).catch((e) => setError(String(e)));
  }, [virtualEms]);

  function addEms() {
    const lon = parseFloat(lonInput);
    const lat = parseFloat(latInput);
    if (Number.isFinite(lon) && Number.isFinite(lat)) {
      setVirtualEms([...virtualEms, [lon, lat]]);
    }
  }

  if (error) return <div className="text-red-600">에러: {error}</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold mb-2">정책 시뮬레이터</h1>
        <p className="text-gray-600">
          가상 응급기관·분서를 추가하면 어떤 변화가 생기나?
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white border rounded-lg p-4 space-y-3">
            <h3 className="font-semibold">가상 응급기관 추가</h3>
            <div>
              <label className="block text-sm">경도</label>
              <input
                className="w-full border rounded px-3 py-1"
                value={lonInput}
                onChange={(e) => setLonInput(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-sm">위도</label>
              <input
                className="w-full border rounded px-3 py-1"
                value={latInput}
                onChange={(e) => setLatInput(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={addEms}
                className="px-3 py-1 bg-blue-600 text-white rounded text-sm"
              >
                추가
              </button>
              <button
                onClick={() => setVirtualEms([])}
                className="px-3 py-1 border rounded text-sm"
              >
                초기화
              </button>
            </div>
            <div className="text-sm">
              현재 추가: <b>{virtualEms.length}</b>개
              <ul className="mt-1 text-xs text-gray-600">
                {virtualEms.map((p, i) => (
                  <li key={i}>
                    {i + 1}. ({p[0].toFixed(4)}, {p[1].toFixed(4)})
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {sim && (
            <div className="grid grid-cols-1 gap-3">
              <MetricCard
                label="평균 위험지수 변화"
                value={`${sim.avg_delta >= 0 ? "+" : ""}${sim.avg_delta.toFixed(4)}`}
              />
              <MetricCard
                label="가장 큰 위험 감소"
                value={sim.max_drop.toFixed(4)}
              />
              <MetricCard
                label="개선된 시군구 수"
                value={sim.improved_count}
                unit="개"
              />
            </div>
          )}
        </div>

        <div className="lg:col-span-2">
          <h2 className="text-xl font-semibold mb-3">시뮬레이션 결과 지도</h2>
          <RiskMap
            features={features}
            simulationItems={sim?.items ?? []}
            virtualEms={virtualEms}
          />
        </div>
      </div>

      {sim && sim.items.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-3">개선 효과 TOP 10 시군구</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-3 py-2 text-left">시군구</th>
                  <th className="px-3 py-2 text-right">기존 위험</th>
                  <th className="px-3 py-2 text-right">신규 위험</th>
                  <th className="px-3 py-2 text-right">변화</th>
                  <th className="px-3 py-2 text-right">신규 응급기관거리(km)</th>
                </tr>
              </thead>
              <tbody>
                {sim.items.slice(0, 10).map((row) => (
                  <tr key={row.sgg_code} className="border-t">
                    <td className="px-3 py-2">{row.sgg_name}</td>
                    <td className="px-3 py-2 text-right">
                      {row.risk_index.toFixed(3)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {row.risk_index_new.toFixed(3)}
                    </td>
                    <td className="px-3 py-2 text-right text-green-700">
                      {row.risk_delta.toFixed(4)}
                    </td>
                    <td className="px-3 py-2 text-right">
                      {row.ems_distance_km_new.toFixed(1)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
```

### Task B.9: About 페이지

**Files:** Create: `frontend/app/about/page.tsx`

- [ ] **Step B.9.1**: 작성

```tsx
// frontend/app/about/page.tsx
export default function AboutPage() {
  return (
    <article className="prose prose-gray max-w-3xl">
      <h1>About — BlindZone</h1>

      <h2>무엇을 푸는가</h2>
      <p>
        한국 교통사고 골든타임 대응이 부족하다는 점이 보도·연구에서 지적되어 왔다.
        머니S 2025-04-10 기사 등에서 "선진국 대비 2배 사망률"·"사고 후 1시간 내
        수술실 도착률 50%"가 언급된다. 그러나 기존 사고 통계 지도는 사고가
        자주 나는 곳만 보여주며, <b>사고 위험 × 응급 도달 시간</b>을 결합해
        잠재 위험지대를 발굴하는 일반인용 서비스는 부재했다.
      </p>
      <p>
        BlindZone은 사고 통계와 응급 의료 접근성을 결합해{" "}
        <b>&quot;사고는 평균인데 죽음은 많은 곳&quot;</b>을 발굴하는 서비스다.
      </p>

      <h2>사용한 데이터</h2>
      <ul>
        <li>
          전국교통사고다발지역표준데이터 (공공데이터포털, 한국도로교통공단 TAAS)
        </li>
        <li>
          국립중앙의료원 응급의료기관 정보 (공공데이터포털 오픈 API,
          End Point <code>B552657/ErmctInfoInqireService</code>)
        </li>
        <li>
          소방청 구급통계서비스 (공공데이터포털 오픈 API,
          End Point <code>1661000/EmergencyStatisticsService</code>)
        </li>
        <li>
          시군구 행정구역 경계 (브이월드 공간정보 다운로드 dsId=30604,
          국토교통부 관할)
        </li>
      </ul>

      <h2>방법론</h2>
      <ol>
        <li>
          시군구 단위로 사고 빈도·사망사고 비율·응급 도달 시간·응급기관 거리·
          면적 등 변수 산출
        </li>
        <li>
          변수들의 가중합(min-max 정규화 후 0.4/0.3/0.3 가중)으로 "잠재 위험
          지수" 정의
        </li>
        <li>
          XGBoost 회귀로 위험 지수를 재학습 → SHAP 값으로 시군구별 "왜
          위험한가" 상위 3개 요인 추출
        </li>
        <li>
          가상 응급기관 추가 시뮬레이션은 응급기관 거리 피처만 재계산해 동일
          모델 inference loop으로 처리
        </li>
      </ol>

      <h2>한계</h2>
      <ul>
        <li>
          시군구 단위 평균 데이터를 사용 — 격자 내 변동성은 평준화됨 (V1.1에서
          1km 격자 세분화 검토)
        </li>
        <li>
          119 출동 사건별 raw 데이터가 비공개라 응급 도달 시간은 응급기관까지
          거리 × 평균 속도(60 km/h 가정)로 추정
        </li>
        <li>
          사망률 정확 추정에는 의료 외 변수(병원 수용능력, 도로 등급별 통행
          속도 등) 추가 필요
        </li>
      </ul>

      <h2>가점 신청 항목</h2>
      <p>
        대회 가점 항목 중 다음 세 가지를 신청한다 (가점 부여 여부는 심사위원단
        판단):
      </p>
      <ul>
        <li>
          AI 학습도구 (5점 신청): Claude Code를 코딩 보조로 활용. 사용 로그·
          기여 흔적 증빙 첨부
        </li>
        <li>
          AI 분석도구 (5점 신청): XGBoost 회귀 + SHAP 설명. 학습 코드·로그 첨부
        </li>
        <li>
          데이터 융합 (5점 신청): 사고(TAAS) × 응급의료기관 × 119 통계 × 행정
          경계 = 주관기관 4종 결합
        </li>
      </ul>
    </article>
  );
}
```

### Task B.10: 타입 체크 + 빌드 검증

- [ ] **Step B.10.1**: 타입 체크

```powershell
cd frontend
npx tsc --noEmit
```

Expected: 에러 0개.

- [ ] **Step B.10.2**: 빌드

```powershell
npm run build
```

Expected: 빌드 성공. 경고 일부 OK.

- [ ] **Step B.10.3**: 로컬 동작 확인 (한태영 직접)

```powershell
# 터미널 1: 백엔드
cd ..\backend
..\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000

# 터미널 2: 프론트
cd ..\frontend
npm run dev
```

브라우저 http://localhost:3000 접속:
- `/` 시민 모드: 시군구 선택 → 메트릭 + SHAP + 지도
- `/policy` 정책: 경위도 입력 → 추가 → 지도·메트릭 변화
- `/about` About: 텍스트

문제 없으면 Ctrl+C로 둘 다 종료.

### Task B.11: Phase B commit

- [ ] **Step B.11.1**: 커밋

```powershell
cd ..
git add frontend/
git commit -m "feat(frontend): Next.js 14 풀스택 — 3개 페이지, MapLibre + deck.gl 지도, API 클라이언트"
```

---

## Phase C: 배포

### Task C.1: Railway 백엔드 배포

**Files:** Create: `backend/Procfile`, Modify: `backend/api/main.py` (CORS origin 추가)

- [ ] **Step C.1.1**: Procfile 작성

```
web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

저장 위치: `backend/Procfile`

- [ ] **Step C.1.2**: [한태영 액션] Railway 가입 + 프로젝트 생성
  - https://railway.app 접속 → GitHub 로그인
  - "New Project" → "Deploy from GitHub repo" → 본 repo 선택
  - **Root directory를 `backend`로 설정** (중요)
  - Environment variables 추가:
    - `DATA_GO_KR_API_KEY` = `.env`의 키
  - Build & Deploy 자동 시작

- [ ] **Step C.1.3**: Railway 콘솔에서 배포 도메인 확인 (예: `https://blindzone-backend.up.railway.app`)

- [ ] **Step C.1.4**: 검증

```powershell
curl https://blindzone-backend.up.railway.app/api/health
```

Expected: `{"status":"ok",...}`

### Task C.2: Vercel 프론트 배포

**Files:** Modify: `frontend/.env.local.example` (참고 갱신)

- [ ] **Step C.2.1**: [한태영 액션] Vercel 가입 + Import Project
  - https://vercel.com 접속 → GitHub 로그인
  - "Add New" → "Project" → repo 선택
  - **Root directory를 `frontend`로 설정**
  - Framework Preset: Next.js (자동 감지)
  - Environment Variables 추가:
    - `NEXT_PUBLIC_API_BASE_URL` = Railway 도메인 (예: `https://blindzone-backend.up.railway.app`)
  - Deploy

- [ ] **Step C.2.2**: Vercel 도메인 확인 (예: `https://blindzone.vercel.app`)

### Task C.3: CORS 갱신

**Files:** Modify: `backend/api/main.py`

- [ ] **Step C.3.1**: Vercel 정확한 도메인을 CORS 화이트리스트에 명시

```python
# backend/api/main.py — allow_origins 부분 수정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://blindzone.vercel.app",  # 실제 Vercel 도메인으로 교체
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step C.3.2**: 커밋 + Railway 자동 재배포

```powershell
git add backend/api/main.py backend/Procfile
git commit -m "deploy: Railway Procfile + 정확한 Vercel CORS 도메인"
git push
```

### Task C.4: 통합 동작 검증

- [ ] **Step C.4.1**: [한태영 액션] Vercel URL 접속

브라우저에서:
- `https://blindzone.vercel.app/` → 시민 모드 동작
- `https://blindzone.vercel.app/policy` → 정책 시뮬레이터 동작
- `https://blindzone.vercel.app/about` → About 텍스트

API 호출 실패 시 (CORS 오류 등) Network 탭에서 확인, 문제는 Task C.3 도메인 정확화 또는 Railway 로그 확인.

---

## Phase D: 정정 + 제출 패키지 준비

### Task D.1: README 정정

**Files:** Modify: `README.md`

- [ ] **Step D.1.1**: 통째 교체 (풀스택 기준)

```markdown
# BlindZone — 보이지 않던 위험지대

> 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙)
>
> 사고는 적은데 죽음은 많은 곳, 데이터로 찾았습니다.

## 무엇

한국 교통사고 골든타임 대응 부족이 보도·연구에서 지적되어 왔다(머니S 2025-04-10 기사 등). BlindZone은 사고 위험 × 응급 도달 시간을 결합해 통계가 가려둔 잠재 위험지대를 발굴하고, 응급 자원 추가 배치를 시뮬레이션하는 풀스택 웹 서비스다.

## 데모

- 프론트: https://blindzone.vercel.app  (배포 후 URL 교체)
- API: https://blindzone-backend.up.railway.app  (배포 후 URL 교체)

## 아키텍처

- 프론트엔드: Next.js 14 (App Router) + TypeScript + Tailwind CSS + MapLibre GL JS + deck.gl + Recharts
- 백엔드: FastAPI + XGBoost + SHAP + GeoPandas
- 배포: Vercel (프론트) + Railway (백엔드)

## 디렉토리

```
backend/   FastAPI + ML 코드
frontend/  Next.js 14
docs/      스펙·플랜·디자인 문서
```

## 로컬 실행

### 백엔드
```bash
cd backend
# (Python venv는 프로젝트 루트의 .venv 또는 backend/.venv 사용)
pip install -r requirements.txt
# data/raw/ 에 raw 데이터 다운로드 (자세히는 scripts/download_data.py 실행)
python scripts/fetch_api_data.py   # 응급의료기관·119 API 호출
python scripts/build_features.py   # 가공
python -m src.train                # 모델 학습
uvicorn api.main:app --reload --port 8000
```

### 프론트엔드
```bash
cd frontend
npm install
cp .env.local.example .env.local
# .env.local의 NEXT_PUBLIC_API_BASE_URL 확인
npm run dev
```

브라우저: http://localhost:3000

## 데이터 출처

- 전국교통사고다발지역표준데이터 (공공데이터포털, TAAS)
- 국립중앙의료원 응급의료기관 정보 (공공데이터포털 오픈 API, B552657)
- 소방청 구급통계서비스 (공공데이터포털 오픈 API, 1661000)
- 시군구 행정구역 경계 (브이월드 공간정보 다운로드 dsId=30604)

통계 인용 출처: 머니S 2025-04-10 기사 (선진국 대비 사망률, 골든타임 도착률 관련)

## 가점 신청 항목

- AI 학습도구: Claude Code (5점 신청)
- AI 분석도구: XGBoost + SHAP (5점 신청)
- 데이터 융합: 사고 × 응급의료기관 × 119 × 행정경계 (5점 신청)

가점 부여는 심사위원단 판단.
```

- [ ] **Step D.1.2**: 커밋

```powershell
git add README.md
git commit -m "docs: README 풀스택·정확한 출처·가점 신청 약화 반영"
```

### Task D.2: AI 학습도구 증빙 자료 준비

**Files:** Create: `docs/submission/ai-tool-evidence.md`

- [ ] **Step D.2.1**: 디렉토리 + 파일 작성

```powershell
New-Item -ItemType Directory -Force -Path docs\submission
```

```markdown
# AI 학습도구 활용 증빙 — Claude Code

본 프로젝트는 Claude Code (Anthropic, Claude 모델 기반)를 코딩 보조 도구로 활용했다.

## 활용 범위

- 데이터 파이프라인 코드 작성 (`backend/src/data_pipeline.py`) — 시군구 매핑 로직, 좌표계 변환, 집계 함수 등
- 모델 학습 코드 (`backend/src/train.py`) — XGBoost 설정, 평가 메트릭, pickle 직렬화
- SHAP 설명 모듈 (`backend/src/shap_explain.py`) — TreeExplainer wrapper
- 시뮬레이션 inference (`backend/src/inference.py`) — sjoin_nearest 기반 거리 재계산
- FastAPI 백엔드 (`backend/api/`) — endpoint, schema, CORS
- Next.js 프론트엔드 (`frontend/`) — 페이지, 컴포넌트, 지도 통합
- API fetch 스크립트 (`backend/scripts/fetch_api_data.py`) — XML 파싱, 페이지네이션

## 활용 방식

- 한태영(출품자)이 요구사항·아키텍처·데이터 분석 방향을 결정
- Claude Code가 결정을 코드로 구현 (한태영의 검토·수정 후 반영)
- 단순 검색이 아닌 코드 작성·디버깅·구조 설계에 활용

## 증빙

- git log 전체 (commit 메시지에 단계별 진행 기록)
- 본 문서
- 대화 로그 (요청 시 제출 가능)
```

- [ ] **Step D.2.2**: 커밋

```powershell
git add docs/submission/ai-tool-evidence.md
git commit -m "docs(submission): AI 학습도구 (Claude Code) 활용 증빙 문서"
```

### Task D.3: 기획서 (3장, 한글 양식) 작성 [한태영 액션]

**Files:** Create (한태영 직접): `docs/submission/BlindZone_기획서.hwp` 또는 `.docx`

- [ ] **Step D.3.1**: [한태영 액션] 대회 페이지에서 `경진대회_참가서류.zip` 다운로드 → 기획서 한글 양식 추출
- [ ] **Step D.3.2**: [한태영 액션] 양식에 다음 내용으로 3장 채우기 (메인이 텍스트 초안 제공 가능):
  - **문제 정의**: 골든타임 부족, 통계 사각지대
  - **데이터**: 4종 출처 명시
  - **방법론**: 가중합 위험 지수 + XGBoost + SHAP + 시뮬레이션
  - **시제품**: Vercel URL + 스크린샷
  - **정책 implication**: 응급 자원 추가 배치 가이드
  - **기대 효과·확장성**: 격자 세분화, 실시간 알림 등 V2

- [ ] **Step D.3.3**: 완성된 기획서 PDF로도 export → `docs/submission/`에 저장

### Task D.4: 데모 영상 (1~2분) [한태영 액션]

- [ ] **Step D.4.1**: [한태영 액션] OBS Studio 또는 Windows + Shift + R 기본 녹화 사용 — Vercel URL에서 다음 흐름 녹화:
  1. 시민 모드 (30초): 시군구 선택 → 메트릭 + SHAP + 지도 확인
  2. 지도 줌·호버 (15초)
  3. 정책 시뮬레이터 (45초): 가상 응급기관 좌표 추가 → 결과 메트릭·지도 변화
  4. About 페이지 빠른 스크롤 (15초)

- [ ] **Step D.4.2**: [한태영 액션] 영상 파일 mp4로 저장 → `docs/submission/BlindZone_demo.mp4`. 100MB 넘으면 별도 클라우드 (YouTube unlisted 추천)

### Task D.5: 최종 점검 + 제출

- [ ] **Step D.5.1**: 체크리스트
  - [ ] Vercel URL 동작 (3개 페이지 모두)
  - [ ] Railway API 동작 (`/api/health` 200)
  - [ ] README 데이터 출처 정확
  - [ ] About 페이지 출처·통계 출처 명시
  - [ ] AI 증빙 문서 (`docs/submission/ai-tool-evidence.md`)
  - [ ] 기획서 (3장, 한글 양식)
  - [ ] 데모 영상 (1~2분)
  - [ ] 1차 심사 양식 (제출물·첨부) 준비 완료

- [ ] **Step D.5.2**: [한태영 액션] 국가교통 데이터 오픈마켓 (https://www.bigdata-transportation.kr) 에서 제출:
  - 참가신청서
  - 기획서 (3장)
  - 시제품: Vercel URL + Railway API URL
  - 첨부: 데모 영상, AI 증빙 문서
  - 제출 마감: 2026-05-29

---

## Self-Review

### Spec coverage

- **데이터 융합 4종** → Phase 0~1에 backend/data, Phase A endpoints에 그대로 반영
- **AI 학습+분석도구 신청** → Phase D.2 증빙 문서, About에 명시 (Phase B.9)
- **풀스택 architecture** → Phase A/B 분리, 정확 디렉토리 구조
- **시군구 GeoJSON 정확한 출처** → Phase 0 VWORLD
- **심사 기준 (독창성·구체성·성장성)** → 산출물에서 충족하지만 task로는 직접 매핑 없음. 기획서 작성(D.3)에서 명시.
- **1차 양식 (기획서 3장, 시제품 URL 첨부)** → Phase D.3, D.5

### Placeholder scan

- "TBD"/"TODO" 없음
- 한태영 액션 task들은 명시적으로 [한태영 액션] 마킹
- VWORLD 받은 후 컬럼 매핑은 Task 0.2의 alias 패턴 확장으로 명시 (실제 컬럼은 받아봐야)
- Vercel/Railway 실제 도메인은 Task C.3에서 명시적 교체 단계

### Type consistency

- TypeScript 타입 (`FeatureSummary`, `FeatureDetail`, `SimulationItem` 등)이 Pydantic schema와 1:1 매칭
- Endpoint path (`/api/features/{sgg_code}`)와 frontend api.ts (`getFeature(sggCode)`)에서 동일 형식
- `risk_index_new`, `risk_delta`, `ems_distance_km_new` 컬럼 이름 backend Pydantic + frontend types 일치

### Known gaps (구현 단계에서 결정)

- VWORLD GeoJSON 정확한 컬럼명 (SIG_CD vs BJCD 등) — Task 0.2 inspect 결과로 alias 보강
- Railway 무료 티어 한도 (50시간/월 sleeping) — 한태영이 paid plan 또는 다른 호스팅 결정 가능
- 모델 파일 크기·메모리 — Railway 무료 티어 메모리(512MB) 안에서 동작해야. 현재 401KB 모델 + ~30MB 라이브러리라 OK.

---

## 다음 단계

1. **한태영 plan 리뷰** — 통째로 OK 받기
2. Execution: `superpowers:subagent-driven-development` skill로 task-by-task 진행 (추천)
3. Phase 0 (VWORLD 받기)부터 순차 실행
