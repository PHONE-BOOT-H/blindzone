# BlindZone — 사고 빈도 지도가 놓치는 응급 사각지대

> 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙)
>
> 사고 건수만으로는 드러나지 않는 잠재 위험지대를, 사망률·응급 접근성과 결합해 탐색합니다.

## 무엇을 푸는가

한국 교통사고 골든타임 대응 부족이 보도·연구에서 지적되어 왔다 (예: 머니S 2025-04-10, "선진국 대비 사망률 2배"·"사고 후 1시간 내 수술실 도착률 50%"). 기존 사고 다발지도는 사고 빈도 위주라는 점에 주목해, BlindZone은 **사고 빈도·사망사고 비율·응급의료 접근성을 결합한 시군구 단위 탐색형 위험 지수**를 산출하고, 가상 응급의료 거점 추가 시 거리 기반 접근성이 어떻게 변하는지 보여주는 surrogate 도구다.

> BlindZone은 사고를 직접 예측하는 모델이 아니다. 공개 데이터로 정의한 잠재 위험지수를 계산·설명한다. 자세히는 [docs/submission/model_card.md](docs/submission/model_card.md).

## 발견 — 사고 빈도만으로 안 보이는 사각지대

본 데이터로 산출한 위험지수 TOP10 중 **3곳(인제·옹진·수성)** 은 TAAS 사고다발지역 데이터의 사고건수 TOP10에 포함되지 않는다. 특히:

- **인제군**: TAAS 다발지점 사고 1건(전국 245위)인데 위험지수 2위 — 가장 가까운 응급의료기관까지 직선거리 24.2km, 도착 추정시간 24분
- **옹진군**: TAAS 다발지점 사고 0건(전국 246위)인데 위험지수 4위 — 도서 지역의 응급 접근성 한계 누적

→ 사고 빈도만 보면 덜 위험해 보이지만, 응급 접근성을 결합하면 잠재 위험이 큰 지역으로 발굴된다.

## 데모

- 프론트엔드 (Vercel): _배포 후 URL 추가_
- 백엔드 (Railway): _배포 후 URL 추가_

## 기술 스택

- **프론트엔드**: Next.js 14 (App Router) · TypeScript · Tailwind CSS · MapLibre GL · deck.gl
- **백엔드**: FastAPI · Pydantic · XGBoost · SHAP TreeExplainer · GeoPandas
- **배포**: Vercel (프론트) · Railway (백엔드)

## 데이터 출처

| 출처 | 라이선스/이용약관 |
|---|---|
| 전국교통사고다발지역표준데이터 (공공데이터포털, 한국도로교통공단 TAAS) — **전체 교통사고가 아닌 다발지점 한정** | 공공데이터 개방 |
| 국립중앙의료원 응급의료기관 정보 (공공데이터포털 오픈 API, B552657) | 공공데이터 개방 |
| 소방청 구급통계서비스 (공공데이터포털 오픈 API, 1661000) — **출동시간 raw 비공개, 본 프로젝트는 응급기관 거리 기반 추정 사용** | 공공데이터 개방 |
| 시군구 행정구역 경계 — 통계청 (센서스경계)시군구경계 (브이월드 다운로드) | **CC BY-NC-ND** (비영리 출품 + 출처 명시) |

## 로컬 실행

### 백엔드

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt

# data/raw/ 에 4개 공공데이터 + .env에 API 키
python backend\scripts\fetch_api_data.py
python backend\scripts\build_features.py
python -m backend.src.train

# API 서버
cd backend
uvicorn api.main:app --reload --port 8000
```

### 프론트엔드

```powershell
cd frontend
npm install
copy .env.local.example .env.local   # NEXT_PUBLIC_API_BASE_URL 설정
npm run dev   # http://localhost:3000
```

## 방법론 요약

1. 시군구 단위 변수 산출 — 사고 빈도(TAAS 다발지역 내), 사망사고 비율, 응급의료기관 거리(km), 응급 도착 추정 시간(거리×60km/h), 면적
2. min-max 정규화 후 가중합 (0.4 / 0.3 / 0.3) → **잠재 위험 지수** 정의
3. XGBoost 회귀로 정의된 위험 지수를 재학습 → **SHAP 값으로 시군구별 상위 기여 요인 추출** (사고 예측이 아닌 surrogate 설명)
4. 가상 응급의료 거점 추가 시뮬레이션 — 거리 피처 재계산 + 동일 모델 inference → 위험 지수 변화 (정책 효과 예측이 아니라 거리 기반 접근성 민감도 분석)

## 한계 및 정직 고지

- 본 모델은 실제 사고·사망을 예측하지 않는다. 정의된 위험지수에 대한 surrogate model이며, R²는 사고 예측 성능이 아니라 정의식 재현도다.
- TAAS 사고다발지역 데이터는 전체 사고 X — 다발지점 한정. "연간 사고 건수" 대신 "TAAS 사고다발지역 데이터 내 사고 건수" 표기.
- 119 출동 사건별 raw 비공개 → 응급 도착시간은 응급기관 거리 + 평균 속도(60km/h) 가정 추정.
- 시군구 단위 평균 — 격자 내 변동성 평준화 (V1.1에서 1km 격자 검토).
- 가중치 0.4 / 0.3 / 0.3은 실증 근거 없이 선택한 임의 설정. 다른 가중치 조합 시 결과 달라질 수 있음.

## 가점 신청 항목 (부여 여부는 심사위원단 판단)

- **AI 학습도구 (5점 신청)**: Claude Code를 코딩 보조로 활용. 사용 기록·기여 증빙은 [docs/submission/ai-tool-evidence.md](docs/submission/ai-tool-evidence.md)
- **AI 분석도구 (5점 신청)**: XGBoost 회귀 + SHAP TreeExplainer
- **데이터 융합 (5점 신청)**: 공공데이터 4종을 시군구 단위로 결합 (TAAS × 응급의료기관 × 119 통계 × 행정경계)

## 문서

- [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md) — 살아있는 스펙
- [docs/submission/model_card.md](docs/submission/model_card.md) — 모델 카드 (surrogate 정의 등)
- [docs/submission/data_manifest.md](docs/submission/data_manifest.md) — 데이터 매니페스트
- [docs/submission/external-review-2026-05-20.md](docs/submission/external-review-2026-05-20.md) — 외부 평가 1차
- [docs/submission/case-study.md](docs/submission/case-study.md) — 대표 사례 (인제군)
