# CURRENT_STATE — 현재 진행 상황

> 매 세션 끝낼 때 업데이트. 새 세션 시작 시 Claude가 가장 먼저 읽는 파일.

---

## 마지막 업데이트

2026-05-26 — **발견 임팩트 강화 세션 (Phase F) 완료**. 처음 지적한 약점 6개를 전부 데이터로 해소: 레버2 도로 실거리(OSRM 252개 재산출해도 robust 인제·옹진 불변)·레버3 외부검증(정부 응급의료취약지 수렴타당도)·119 가점표현 정직화(B)·옹진 시뮬(-81%)·인제 119 188건·**레버1·4(고령 수요 교차분석+수혜인구)**. 핵심 신규: 인제 고령 28.0%·옹진 37.2%(대도시 robust 평균 20.9%의 1.5배) → "사고 0건이 아니라 고령 수요 큰데 응급 멀어 구조적 취약" 정량 입증. 거점 추가 시 수혜 인제 30,773명·옹진 19,397명. 환경 복구(py-3.12). **외부 AI 3차 평가 반영**: 1분 발표 스크립트·예상질문 방어 추가, "사고 0건"→"다발지점 기준" 정정, **전체 교통사고 통계(도로교통공단 2024) 대조로 다발지점 한계 직접 입증 — 인제 다발1/전체83, 옹진 다발0/전체27 (다발지점 포착률 1.2%·0% vs 대도시 80%+)**. **2026-05-27 배포 완료** — 백엔드 HF Spaces 라이브(`hananhan-blindzone-backend.hf.space/api/health` ok)·프론트 Vercel 라이브(인증 해제, 배포 상세 `docs/DEPLOY.md`). GitHub `PHONE-BOOT-H/blindzone`(main). 기획서 본문 초안(`proposal-draft.md`)+데모 영상 대본(`demo-script.md`) 작성. **남은 건 순수 한태영 액션: HWP 기획서 작성·데모 영상 녹화·통계누리 접수(5/29 마감).**

---

## 어디까지 왔는지

### Phase 1~4 (데이터·모델 셋업) ✅
기존 grid_features.parquet + xgb_risk_model.pkl + SHAP 모듈 + What-if inference 모듈 모두 있음.

### Phase 0 (시군구 GeoJSON 갱신) ✅ `0380b82`
통계청 (센서스경계) VWORLD SHP. 252 시군구. CC BY-NC-ND.

### Phase A (FastAPI 백엔드) ✅ 
6 endpoint + 8 통합 테스트. 자세히는 이전 commit 이력.

### Phase B (Next.js 프론트엔드) ✅

| Task | Commit | 내용 |
|---|---|---|
| T7 셋업 | `0d21ec7` | Next.js 14 + TS + Tailwind + maplibre/deck.gl, types/api/Nav/layout |
| T8 RiskMap | `7901b81` | deck.gl ScatterplotLayer + maplibre basemap (외부평가 5번 shadowing fix) |
| T9 4 컴포넌트 | `688e7aa` | MetricCard·ShapExplanation·Top10Table·ContrastPanel |
| T10 3 페이지 | `0f36492` | 시민 모드·정책 시뮬레이터·About + 정직성 정정 + 인제·옹진 narrative |
| T11 build 검증 | T10에서 같이 | tsc + lint + next build 7/7 prerender 성공 |

### Phase C (배포 prerequisite) ✅

| Task | Commit | 내용 |
|---|---|---|
| T12 | `422260d` | backend/Procfile + railway.json (NIXPACKS + requirements-api.txt + healthcheck /api/health) |

CORS는 main.py에 `https://*.vercel.app` regex 이미 허용. **실제 Railway/Vercel 배포는 한태영 액션**.

### Phase D (정정·증빙) ✅

| Task | Commit | 내용 |
|---|---|---|
| T13 README | `d161ed5` | 위험표현 8개 정정 + 인제·옹진 narrative + Next.js/FastAPI 스택 갱신 |
| T15 case-study | `92368dd` | 인제군 (사고 1건/위험 2위, EMS 24.2km, SHAP top1=거리, 시뮬레이션 -58%) |
| T14 ai-tool-evidence | `305b689` | 가점 3건 증빙 (Claude Code 활용 영역 + 한태영 판단 영역 + XGBoost/SHAP + 4종 융합) |
| Prior-art | `aca8af2` | 선행 연구 조사 (Jung & Qin 시리즈) + README/case-study 인용 |

### Phase E (외부 AI 2차 평가 반영) ✅ — 커밋됨 (d0dd250 + 후속)

외부 평가 방법론 1순위 약점 = **가중치 0.4/0.3/0.3 임의성**. 대응: 단일 순위 대신 **robust blind zone** 프레임으로 전환.

| 산출물 | 내용 |
|---|---|
| `backend/scripts/weight_sensitivity.py` | 재현 검증(오차 0) + 가중치 126개 시나리오 + 사망률 smoothing(empirical Bayes) |
| `docs/submission/weight-sensitivity.md` | 방법·결과·해석·한계·재현 (핵심 방법론 증빙) |
| `weight_sensitivity_summary.csv` / `smoothing_effect.csv` | 252개 시군구 강건성 지표 / 보정 전후 |
| `presentation-outline.md` | 발표 초안 — XGBoost 4순위 격하 + robust 핵심 슬라이드 (한태영 재구성 필요) |
| case-study/model_card/data_manifest/README/about/ContrastPanel 수정 | 가중치 한계 고지를 실제 수치로 교체, 순위 "기준 가중치" 명시 |

**핵심 결과** (실제 계산값, 검증 오차 0):
- robust(top10_share≥0.6) 8곳 중 6곳 대도시 → 비대도시 robust는 **인제·옹진뿐**
- **옹진군**: 거리 75.3km 단독, 가중치+사망률 보정 양쪽 강건(4→3위) = 가장 안정적 사각지대
- **인제군**: 가중치엔 강건(top10 0.905)하나 사망률 보정 시 2→15위 (사망률 1.0 = 사고 1건 산물) → 정직 고지, 거리 24.2km는 남음
- frontend tsc/lint/build 7/7 통과

**후속 강건성 점검(완료 2026-05-26, weight-sensitivity.md §6)**: 직선거리 균일배수→순위 불변 입증, 거리 구간별 차등 보정에도 인제·옹진 유지. 사고건수 log1p→인제 1위·옹진 113위(정규화 방식별 부각 사각지대 차이). 남은 보강(도로망 실거리·수요변수)은 V2 과제.

### T16 (한태영 액션 — 최종 제출 준비)

- [ ] 통계누리 hNum=283 zip 다운로드 → 참가신청서·서약서·기획서 HWP 확보
- [ ] 기획서 3장 작성 (BlindZone narrative 기반)
- [ ] 데모 영상 녹화 (시민 모드 → 시군구 클릭 → SHAP → 정책 시뮬레이터 → About 발견 섹션)
- [ ] 2026-05-29 마감 전 접수

---

## 핵심 narrative (발표·기획서용)

### 한 줄
**사고 빈도 지도가 놓치는 응급 사각지대를, 시군구 단위 4종 데이터 융합으로 발굴한다.**

### 대표 사례 — 인제군 (T15 case-study)
- TAAS 다발지점 사고 1건 (전국 245위) → BlindZone 위험지수 2위 (0.396)
- 응급의료기관까지 직선거리 24.2km, 도착 추정 24분
- SHAP top1: 응급기관까지 거리 (+0.173)
- 가상 EMS 1곳 추가 시뮬레이션: 거리 24.2 → 8.23km, 위험지수 0.396 → 0.166 (-58%)

### 보조 사례 — 옹진군
- TAAS 다발지점 사고 0건 (전국 246위) → BlindZone 위험지수 4위 (도서 지역 응급 접근성)

### 차별점 5개 (prior-art 기반)
1. 시군구 252개 전국 단위 (선행은 점단위/고속도로/광역시)
2. 4종 데이터 동시 융합 (TAAS+응급의료+119+행정경계)
3. 가중합 + XGBoost surrogate + SHAP 파이프라인
4. What-if 인터랙티브 시뮬레이션
5. 풀스택 웹서비스 (선행은 학술)

### 선행 인지 (포지셔닝)
- Jung & Qin (2024 MDPI, 2025 TRR) — 가장 가까운 선행. EMS+사고 융합, XGBoost+SHAP. **분석 단위·도구·산출 형태가 BlindZone과 다름**. 발표 시 명시 인용 권장.

---

## 🔔 새 세션 시작 시 — 한태영에게 먼저 물어볼 것

**현재 상태 (2026-05-26): 발견 임팩트 강화(Phase F) 완료·커밋됨.**

먼저 물어볼 것:

- **(a) 레버1·4 완료.** 행안부 고령인구현황 CSV(2026-04)가 들어와 `merge_population.py`로 252개 매칭 → `demand_analysis.py`로 교차분석·수혜인구 산출. 인제 28.0%·옹진 37.2%(대도시 robust 평균 20.9%의 1.5배), 수혜 인제 30,773명·옹진 19,397명. `grid_features_demo.parquet` 생성. **약점 6개 전부 해소 → 다음은 T16(배포·기획서·영상).**
- **(b) 119 방향 = B 적용됨** ("4종 동시 융합"→"3종 융합+119 교차검증"으로 정직화). A(변수 통합) 원하면 되돌릴 수 있으나, A는 119의 경기·대구 본부 누락+옹진 도서 미포착으로 risk_index 왜곡 → 비추천.
- **(c) T16 한태영 액션** (Railway/Vercel 배포·통계누리 zip·HWP 기획서·데모 영상) → 어디 막혔나, 무엇 도와줄지.

### Phase F 커밋됨
`feat(analysis): 외부검증·도로실거리 robust 재산출 + 119 가점표현 정직화`. 신규: `external-validation.md`·`road_distance_252.csv`·`road_robustness_summary.csv` + 스크립트 3개(`road_distance_validation`·`build_road_distances`·`road_robustness`). 수정: README·case-study·weight-sensitivity·data_manifest·presentation-outline·ai-tool-evidence. **다음 커밋은 인구 데이터 들어온 뒤 레버1·4.**

### 환경 주의 (중요)
`.venv`는 Python 3.14 base 소실로 **깨짐** (쓰지 말 것). **모든 백엔드 Python은 `py -3.12`로 실행** — 2026-05-26 geopandas 1.1.3 / xgboost 3.2.0 / shap 0.51.0 / sklearn / shapely / pyproj / openpyxl 설치 완료해 build_features·train·inference·OSRM 검증 모두 py-3.12로 가능. venv 재생성 불필요.

---

## 다음 할 일

**한태영 액션 대기**:
- [ ] Phase E 변경 커밋 confirm (위 '커밋 대기')
- [ ] Railway 가입 + 백엔드 배포 (Root Directory: `backend/`, NIXPACKS 자동)
- [ ] Vercel 가입 + 프론트 배포 (Root Directory: `frontend/`, NEXT_PUBLIC_API_BASE_URL = Railway URL)
- [ ] 통계누리 hNum=283 zip 다운로드 → HWP 확보
- [ ] 기획서 3장 작성 (`presentation-outline.md` + `weight-sensitivity.md` 기반), 데모 영상 녹화
- [ ] 2026-05-29 접수

**Claude 도울 수 있는 것 (한태영 요청 시)**:
- 외부 평가 후속 과제 (직선거리 보정 시나리오, 사고건수 log 변환)
- HWP 본문 텍스트 초안 (`presentation-outline.md` 기반, 한태영이 HWP에 붙여넣기)
- 데모 영상 시나리오 텍스트
- 배포 후 CORS·환경변수 갱신

---

## 보조 산출물

- `C:\Users\한태영\Desktop\BlindZone_프로젝트_개요.html` (28 KB, 12 섹션) — 비전공자용 단일 HTML 브리핑. 한태영 직접 더블클릭으로 열기

---

## 최근 결정 (이번 세션)

- 2026-05-25: 외부 AI 2차 평가 핵심 = 가중치 임의성. **robust blind zone** 프레임 채택. 가중치 126 시나리오 + 사망률 smoothing 실제 계산 → 인제는 사망률 보정에 민감(2→15위)이라 정직 고지, **옹진이 더 robust한 대표 사례로 격상**. 발표 outline에서 XGBoost를 4순위 설명 보조로 격하. 정규화 재현 검증 오차 0 → 분석 신뢰.
- 2026-05-25: `.venv` 깨짐 발견 (Python 3.14 base 소실) → `py -3.12` + pyarrow로 분석 우회. 민감도 분석은 순수 pandas라 geopandas 불필요했음.
- 2026-05-23: T8 메인 직접 작성 (subagent 두 번 실패 회피). 이후 T9·T10·T13·T14·T15·T12·prior-art 모두 메인 직접 + tsc/build 즉시 검증 패턴이 안정적이라 그대로 유지
- 2026-05-23: 정직성 정정 — page.tsx의 "사고는 적은데 죽음은 많은" → "사고 건수만으로는 드러나지 않는 응급 사각지대", MetricCard 라벨 "연간 사고 건수" → "사고 건수 (TAAS 다발지점)", "평균 응급 도착시간" → "응급 도착시간 (추정)"
- 2026-05-23: prior-art researcher subagent 1회 실행. Jung & Qin 시리즈 (2024 MDPI, 2025 TRR, 2020 ASCE)가 가장 가까운 선행으로 발견됨 → README·case-study에 짧은 인용 + prior-art.md 별도 정리. 발표·기획서에 "선행 인지 + 확장" 프레임 권장

---

## Skill 모드 메모

- 이번 세션은 메인 직접 + 즉시 tsc/build 검증 패턴 사용. subagent는 prior-art researcher 1회만 사용 (선행 조사 — 외부 조사라 적합)
- 무거운 컴포넌트·페이지 작성도 메인 직접이 더 안정적임 (T7 후반부 + T8~T10 사례)
- 다음 세션도 동일 패턴 권장
