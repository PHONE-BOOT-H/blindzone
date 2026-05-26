---
title: BlindZone API
emoji: 🚑
colorFrom: red
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# BlindZone API (FastAPI)

사고 위험 × 응급 사각지대 분석 API — 탐색형 surrogate. Hugging Face Spaces(Docker)에 배포.

## 엔드포인트

- `GET /api/health` — 상태·모델·피처 로드 확인 (HF Space 헬스체크)
- `GET /api/features` — 시군구 252개 위험지수 요약 (지도용)
- `GET /api/features/{sgg_code}` — 시군구 상세 + SHAP 기여요인
- `GET /api/top10` — 위험지수 상위 10
- `GET /api/contrast` — 사고건수 순위 vs 위험지수 순위 격차 (사각지대 발굴)
- `POST /api/simulate` — 가상 응급거점 추가 시 거리 재계산 + 위험지수 재추론

## 런타임

- 데이터: `data/processed/feature_details.parquet` (SHAP 사전계산), `models/xgb_risk_model.pkl`
- geopandas·shap은 사전계산(build_features·precompute_shap)용이라 런타임 미포함 → 컨테이너 경량.
- CORS: `https://*.vercel.app` 허용 (프론트는 Vercel).

## 로컬 실행

```
py -3.12 -m uvicorn api.main:app --reload --port 8000
```

## 정적 fallback

프론트(`frontend/lib/api.ts`)는 이 API가 다운돼도 `frontend/public/data/*.json`
스냅샷으로 지도·위험지수·SHAP·대조를 표시한다. 스냅샷 재생성:
`py -3.12 backend/scripts/export_static.py`.
