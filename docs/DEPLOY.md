# 배포 가이드 (Railway + Vercel)

> 한태영이 따라 하는 단계별 가이드. 백엔드는 Railway, 프론트는 Vercel. **핵심: 백엔드가 죽어도 프론트는 정적 fallback(`frontend/public/data/`)으로 지도·위험지수·SHAP·대조가 동작한다** — 심사 중 API가 죽어도 데모는 살아있음.

## 0. 사전 (배포 전 1회)

fallback 데이터를 최신화한다 (분석이 바뀌었으면 다시):
```
py -3.12 backend/scripts/export_static.py
```
→ `frontend/public/data/`에 features·top10·contrast·details·simulate_examples JSON 생성(이미 커밋됨).

그리고 GitHub에 push (Railway/Vercel이 repo를 연동해 자동 배포):
```
git push
```

## 1. 백엔드 — Railway

1. https://railway.app 가입 (GitHub 계정 연동).
2. **New Project → Deploy from GitHub repo** → 이 repo 선택.
3. **Settings → Root Directory = `backend`** (중요. 안 하면 빌드 실패).
4. Railway가 `backend/railway.json`을 읽어 자동 설정:
   - 빌드: `pip install -r requirements-api.txt` (NIXPACKS)
   - 실행: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - 헬스체크: `/api/health`
5. 배포 완료 후 **Settings → Networking → Generate Domain** → 공개 URL 확보 (예: `https://blindzone-xxxx.up.railway.app`).
6. 확인: 브라우저에서 `https://<railway-url>/api/health` → `{"status":"ok",...}` 떠야 정상.

> ⚠️ 무료/저가 플랜은 일정 시간 미사용 시 잠들어(cold start) 첫 요청이 느릴 수 있다. **심사·녹화 직전에 `/api/health`를 한 번 호출해 깨워둘 것.** 깨우는 걸 잊어도 프론트는 fallback으로 동작한다.

## 2. 프론트 — Vercel

1. https://vercel.com 가입 (GitHub 연동).
2. **Add New → Project → Import** → 이 repo 선택.
3. **Root Directory = `frontend`** 설정.
4. **Environment Variables** 추가:
   - `NEXT_PUBLIC_API_BASE_URL` = Railway URL (예: `https://blindzone-xxxx.up.railway.app`)
   - (이 값이 없으면 localhost로 폴백돼 라이브 API가 안 되지만, 정적 fallback은 동작)
5. **Deploy**. 완료 후 Vercel URL 확보 (예: `https://blindzone.vercel.app`).
6. CORS: 백엔드 `api/main.py`에 `https://*.vercel.app` regex가 이미 허용돼 있음. 커스텀 도메인이면 추가 필요.

## 3. 데모 동작 검증 (필수)

배포 후 반드시 확인:

| 확인 | 방법 | 정상 |
|---|---|---|
| 지도·위험지수 | Vercel URL 접속 | 시군구 색칠된 지도 표시 |
| 시군구 상세·SHAP | 인제군·옹진군 클릭 | 위험지수 + "왜 위험한가" 표시 |
| 정책 시뮬레이터 | 가상 거점 추가 | 위험지수 변화 표시 |
| 대조(사각지대) | contrast 화면 | 사고순위 vs 위험순위 격차 |
| **fallback** | Railway 끈 상태에서 Vercel 접속 | 지도·위험지수·SHAP·대조 **여전히 동작**(라이브 시뮬만 예시로 대체) |

## 4. 데모 시나리오 (심사·영상용 고정 경로)

외부 평가 권고: 즉흥 탐색 말고 **고정 경로**로 안정적으로.
1. 메인 지도 — 대도시가 진하게 보임 ("사고 많은 곳은 다 안다")
2. 시민 모드 → **옹진군** 클릭 — 다발지점 0건인데 위험 상위, 응급거리 75km, 고령 37%
3. SHAP — "왜 위험한가" = 응급기관 거리
4. 정책 시뮬레이터 → 옹진 인근 거점 추가 — 위험지수 급감
5. 대조/About — 다발지점 vs 전체(인제 1/83·옹진 0/27), 정부 취약지 일치, 5중 검증
6. 마무리 — "사고 많은 곳에서 사고 나면 못 구하는 곳으로"

## 5. 트러블슈팅

- **Railway 빌드 실패**: Root Directory가 `backend`인지 확인. `requirements-api.txt` 존재 확인.
- **지도 안 뜸**: 브라우저 콘솔 확인. fallback이 있어 `/data/features.json`이 200이면 지도는 떠야 함.
- **CORS 에러**: Railway URL이 `NEXT_PUBLIC_API_BASE_URL`에 정확히 들어갔는지, main.py CORS regex 확인.
- **시뮬레이터만 안 됨**: 백엔드 cold start. `/api/health` 호출로 깨우거나, fallback 예시로 데모.
