# BlindZone — 사고 빈도 지도가 놓치는 응급 사각지대

> 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙)
>
> 사고 건수만으로는 드러나지 않는 잠재 위험지대를, 사망률·응급 접근성과 결합해 탐색합니다.

## 무엇을 푸는가

한국 교통사고 골든타임 대응 부족이 보도·연구에서 지적되어 왔다 (예: 머니S 2025-04-10, "선진국 대비 사망률 2배"·"사고 후 1시간 내 수술실 도착률 50%"). 기존 사고 다발지도는 사고 빈도 위주라는 점에 주목해, BlindZone은 **사고 빈도·사망사고 비율·응급의료 접근성을 결합한 시군구 단위 탐색형 위험 지수**를 산출하고, 가상 응급의료 거점 추가 시 거리 기반 접근성이 어떻게 변하는지 보여주는 surrogate 도구다.

> BlindZone은 사고를 직접 예측하는 모델이 아니다. 공개 데이터로 정의한 잠재 위험지수를 계산·설명한다. 자세히는 [docs/submission/model_card.md](docs/submission/model_card.md).

## 발견 — 사고 빈도만으로 안 보이는 사각지대

기준 가중치(0.4/0.3/0.3) 위험지수 TOP10 중 인제·옹진·수성 등은 TAAS 사고건수 TOP10에 없다. 나아가 단일 가중치에 기대지 않으려 **126개 가중치 시나리오 + 사망률 소표본 보정**으로 순위 강건성을 검증했다(→ [docs/submission/weight-sensitivity.md](docs/submission/weight-sensitivity.md)). 그 결과 사고건수가 전국 하위인데도 대부분의 가중치에서 상위에 남는 곳은 **인제군·옹진군 두 곳**이다(robust blind zone).

- **옹진군**: TAAS **다발지점 기준** 사고 0건(전체 사고가 0이라는 뜻이 아님)인데 응급거리 75.3km(전국 최대)로 위험지수 4위. 사망률에 의존하지 않아 가중치·사망률 보정 양쪽에 강건한, 가장 안정적인 사각지대.
- **인제군**: 사고 1건(전국 245위)인데 기준 가중치 2위. 단 이 2위는 사망률 1.0(사고 1건의 산물)에 의존해 소표본 보정 시 15위권으로 내려간다 — 숨기지 않고, 거리 24.2km라는 구조적 요인과 분리해 해석한다.
- 수성구처럼 기준 가중치에서만 상위인 곳은 가중치를 바꾸면 빠지므로 robust로 보지 않는다.

→ 단일 순위가 아니라, 여러 합리적 가중치에서 반복적으로 드러나는 응급 사각지대를 발굴한다.

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
5. 가중치 민감도 검증 — 126개 가중치 시나리오 + 사망률 소표본 보정으로 robust blind zone 산출 ([weight-sensitivity.md](docs/submission/weight-sensitivity.md))
6. 외부 타당성 검증 — robust 사각지대(인제·옹진)가 정부 응급의료취약지 공식 지정(도달시간+인구 기반, 방법 독립)과 같은 곳을 가리킴 = 수렴 타당도 ([external-validation.md](docs/submission/external-validation.md))
7. 수요(고령) 교차분석 — robust 사각지대는 고령비율도 대도시 robust의 1.5배(인제·옹진 평균 32.6% vs 대도시 20.9%) → 공급(응급거리)+수요(고령) 양쪽 취약 ([demand-analysis.md](docs/submission/demand-analysis.md))

## 선행 연구와의 관계

한국 데이터로 사고·응급의료를 결합한 선행 연구가 존재한다. 본 프로젝트는 이를 인지하고, 분석 단위·방법론·산출 형태를 확장한다.

- **Jung & Qin (2024, MDPI Sustainability)** — 한국 EMS 인프라 + 사고 데이터 융합, 16-20분 응급 대응시간 구간이 사망률 유의 증가와 연결. EMS 입지 우선순위 제안. **BlindZone과 차이**: GWLR 사용(XGBoost X), What-if 시뮬레이션 없음, 충청권 중심 점단위 분석.
- **Jung & Qin (2025, Sage TRR)** — 한국 데이터 + XGBoost + SHAP으로 사고 심각도 영향 요인 식별. **BlindZone과 차이**: 분석 단위가 개별 사고건이지 시군구 행정단위가 아님, "사각지대 발굴"이나 가상 거점 시뮬레이션 없음, 학술 분석.

본 프로젝트의 차별점은 **(a) 시군구 252개 전국 단위 + (b) TAAS·응급의료기관·행정경계 3종을 시군구 단위로 융합(+119 구급통계 교차검증) + (c) 인터랙티브 What-if 시뮬레이션 + (d) 풀스택 웹서비스**의 결합이다. 자세한 선행 조사 결과는 [docs/submission/prior-art.md](docs/submission/prior-art.md).

## 한계 및 정직 고지

- 본 모델은 실제 사고·사망을 예측하지 않는다. 정의된 위험지수에 대한 surrogate model이며, R²는 사고 예측 성능이 아니라 정의식 재현도다.
- TAAS 사고다발지역 데이터는 전체 사고 X — 다발지점 한정. "연간 사고 건수" 대신 "TAAS 사고다발지역 데이터 내 사고 건수" 표기. **전체 교통사고 통계(도로교통공단 2024) 대조 결과 인제 83건·옹진 27건으로, 다발지점은 각각 1.2%·0%만 포착** — 대도시(다발지점이 전체의 80%+ 포착)와 달리 분산형 사각지대를 구조적으로 놓침을 직접 확인(다발지점이 사각지대를 놓친다는 본 프로젝트 문제의식의 증거).
- 119 출동 사건별 raw 비공개 → 응급 도착시간은 응급기관 거리 + 평균 속도(60km/h) 가정 추정.
- 시군구 단위 평균 — 격자 내 변동성 평준화 (V1.1에서 1km 격자 검토).
- 가중치 0.4 / 0.3 / 0.3은 실증 근거 없는 선택이다. 이를 방어하기 위해 126개 가중치 시나리오 + 사망률 소표본 보정으로 순위 강건성을 검증했다([weight-sensitivity.md](docs/submission/weight-sensitivity.md)). 모든 순위는 기준 가중치 기준이며, 확정 위험 순위가 아니라 탐색 우선순위다.
- 응급 접근성을 **직선거리**로 계산. 단 252개 전체를 OSRM 도로망 실거리로 재산출했고(인제 직선 24.2→실거리 37.2km/48.7분, 옹진 75.3→151.7km/183.5분, 우회율 중앙값 1.49x), **직선거리가 외진 사각지대를 오히려 과소추정**하며 **실거리로 재산출해도 robust 사각지대(인제·옹진) 결론은 불변**임을 확인했다(weight-sensitivity §6.1). 수요측 변수(인구·고령자 비율)도 행안부 주민등록 고령인구현황으로 교차분석했다 — robust 사각지대는 고령비율도 상위(인제 28.0%·옹진 37.2% vs 대도시 robust 평균 20.9%, [demand-analysis.md](docs/submission/demand-analysis.md)).

## 가점 신청 항목 (부여 여부는 심사위원단 판단)

- **AI 학습도구 (5점 신청)**: Claude Code를 코딩 보조로 활용. 사용 기록·기여 증빙은 [docs/submission/ai-tool-evidence.md](docs/submission/ai-tool-evidence.md)
- **AI 분석도구 (5점 신청)**: XGBoost 회귀 + SHAP TreeExplainer
- **데이터 융합 (5점 신청)**: 공공데이터 3종(TAAS × 응급의료기관 × 행정경계)을 시군구 단위로 융합해 위험지수 산출 + 119 구급통계로 교차검증 (도착시간 추정 현실성·다발지점 한계)

## 문서

- [docs/submission/model_card.md](docs/submission/model_card.md) — 모델 카드 (surrogate 정의 등)
- [docs/submission/data_manifest.md](docs/submission/data_manifest.md) — 데이터 매니페스트
- [docs/submission/case-study.md](docs/submission/case-study.md) — 대표 사례 (인제군)
- [docs/submission/weight-sensitivity.md](docs/submission/weight-sensitivity.md) — 가중치 민감도 분석 (robust blind zone 검증)
- [docs/submission/external-validation.md](docs/submission/external-validation.md) — 외부 타당성 검증 (정부 응급의료취약지 일치)
- [docs/submission/demand-analysis.md](docs/submission/demand-analysis.md) — 수요(고령) 교차분석 + 수혜인구 (구조적 취약 입증)
- [docs/submission/prior-art.md](docs/submission/prior-art.md) — 선행 연구 인지 + 차별점 정리
- [docs/submission/ai-tool-evidence.md](docs/submission/ai-tool-evidence.md) — AI 도구 활용 증빙
