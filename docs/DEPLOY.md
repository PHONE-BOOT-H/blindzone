# 배포 가이드 (Hugging Face Spaces + Vercel)

> 백엔드는 HF Spaces(Docker), 프론트는 Vercel. alrimi+ 배포 패턴 재사용(HANANHAN/PHONE-BOOT-H 계정).
> **핵심: 백엔드가 죽어도 프론트는 정적 fallback(`frontend/public/data/`)으로 지도·위험지수·SHAP·대조가 동작한다** — 심사 중 API가 죽거나 cold start여도 데모는 살아있음. (그래서 alrimi가 겪은 sleep 문제도 BlindZone에선 치명적이지 않음.)

## 0. 사전 (완료 상태)

- ✅ GitHub: `https://github.com/PHONE-BOOT-H/blindzone` (main 브랜치 push 완료)
- ✅ fallback 스냅샷: `frontend/public/data/*.json` (커밋됨). 분석 바뀌면 재생성: `py -3.12 backend/scripts/export_static.py`
- ✅ `backend/Dockerfile`·`backend/README.md`(HF config)·`.dockerignore` 준비됨

## 1. 백엔드 — Hugging Face Spaces (Docker)

1. https://huggingface.co/new-space → **Owner: HANANHAN, Space name: `blindzone-backend`, SDK: Docker**, 빈 Space 생성.
2. `backend/` 내용을 Space repo에 push (alrimi 패턴 그대로):
   ```powershell
   # 임시 폴더에 Space repo 클론 (토큰 URL)
   git clone https://HANANHAN:<HF_TOKEN>@huggingface.co/spaces/HANANHAN/blindzone-backend $env:TEMP\bz_hf
   # backend 내용 복사 (Dockerfile·README·api·src·models·data/processed·requirements-api.txt)
   Copy-Item -Recurse -Force backend\* $env:TEMP\bz_hf\
   cd $env:TEMP\bz_hf
   git add . ; git commit -m "deploy: blindzone backend" ; git push
   ```
   (`.dockerignore`가 data/raw·tests·scripts·csv를 빌드에서 제외 — 경량.)
3. HF가 Dockerfile로 자동 빌드 (~3–5분). 완료 URL: **`https://HANANHAN-blindzone-backend.hf.space`**
4. 확인: `https://HANANHAN-blindzone-backend.hf.space/api/health` → `{"status":"ok","model_loaded":true,...}`
5. **secret 등록 불필요** — BlindZone API는 런타임 환경변수가 없다(데이터·모델만 읽음). alrimi처럼 NEIS/Supabase 키 등록 안 해도 됨.

> data/processed의 `feature_details.parquet`(SHAP 사전계산)·`models/xgb_risk_model.pkl`이 Space repo에 포함돼야 함. 둘 다 git 추적 중이라 backend 복사 시 따라감.

## 2. 프론트 — Vercel

1. https://vercel.com/new → GitHub `PHONE-BOOT-H/blindzone` import (alrimi 쓰던 계정 그대로).
2. **Root Directory = `frontend`**.
3. **Environment Variables**:
   - `NEXT_PUBLIC_API_BASE_URL` = `https://HANANHAN-blindzone-backend.hf.space`
   - (없어도 정적 fallback은 동작하지만, 라이브 시뮬레이터를 위해 넣을 것)
4. **Deploy** → URL 확보 (예: `https://blindzone.vercel.app`).
5. CORS: `api/main.py`에 `https://*.vercel.app` regex 허용됨. 커스텀 도메인이면 추가.

## 3. 데모 동작 검증 (필수)

| 확인 | 방법 | 정상 |
|---|---|---|
| 지도·위험지수 | Vercel URL 접속 | 시군구 지도 표시 |
| 상세·SHAP | 인제군·옹진군 클릭 | 위험지수 + "왜 위험한가" |
| 정책 시뮬레이터 | 가상 거점 추가 | 위험지수 변화 |
| 대조(사각지대) | contrast 화면 | 사고순위 vs 위험순위 격차 |
| **fallback** | HF Space sleep/중단 상태에서 접속 | 지도·위험지수·SHAP·대조 **여전히 동작**(라이브 시뮬만 예시 대체) |

## 4. 데모 시나리오 (심사·영상용 고정 경로)

1. 메인 지도 — 대도시가 진하게 ("사고 많은 곳은 다 안다")
2. 시민 모드 → **옹진군** 클릭 — 다발지점 0건인데 위험 상위, 응급거리 75km, 고령 37%
3. SHAP — "왜 위험한가" = 응급기관 거리
4. 정책 시뮬레이터 → 옹진 인근 거점 추가 → 위험지수 급감
5. 대조/About — 다발지점 vs 전체(인제 1/83·옹진 0/27), 정부 취약지 일치, 5중 검증
6. 마무리 — "사고 많은 곳에서, 사고 나면 못 구하는 곳으로"

> HF Space는 미사용 시 sleep → 데모/녹화 직전 `/api/health` 한 번 호출해 깨워둘 것. 깜빡해도 프론트 fallback이 핵심 데모를 커버.

## 5. (대안) 백엔드 — Railway

HF 대신 Railway를 쓰려면 `backend/railway.json`·`Procfile`이 이미 준비됨:
1. railway.app → New Project → GitHub `blindzone` → **Root Directory = `backend`**.
2. 자동: `pip install -r requirements-api.txt` → `uvicorn api.main:app --port $PORT`, healthcheck `/api/health`.
3. Generate Domain → URL을 Vercel `NEXT_PUBLIC_API_BASE_URL`에 사용.
(단 alrimi 메모상 Railway는 sleep 이슈가 있었음 — BlindZone은 fallback으로 커버되나 HF 권장.)

## 6. 트러블슈팅

- **HF 빌드 실패**: Space SDK가 Docker인지, `requirements-api.txt`·`Dockerfile`이 Space repo 루트에 있는지 확인.
- **지도 안 뜸**: 콘솔 확인. fallback이 있어 `/data/features.json`이 200이면 지도는 떠야 함.
- **CORS 에러**: `NEXT_PUBLIC_API_BASE_URL`이 정확한 HF URL인지, main.py CORS regex 확인.
- **시뮬레이터만 안 됨**: HF cold start. `/api/health`로 깨우거나 fallback 예시로 데모.
