# CURRENT_STATE — 현재 진행 상황

> 매 세션 끝낼 때 업데이트. 새 세션 시작 시 Claude가 가장 먼저 읽는 파일.

---

## 마지막 업데이트
2026-05-23 — Phase A 백엔드 완전 종료 + Phase B Next.js 셋업 완료. **T8 (RiskMap) 다음 세션 시작점**.

---

## 어디까지 왔는지

### Phase 1~4 (셋업·데이터·가공·모델) ✅ (이전 세션)

생략. 기존 grid_features.parquet + xgb_risk_model.pkl + SHAP 모듈 + What-if inference 모듈 모두 있음.

### Phase 0 (시군구 GeoJSON 갱신) ✅ (이전 세션, commit `0380b82`)

통계청 (센서스경계) VWORLD SHP. 252 시군구. CC BY-NC-ND.

### Phase A (FastAPI 백엔드) ✅ (오늘 완료)

| Task | Commit | 내용 |
|---|---|---|
| T1 (A.0) | `07cbad9` | SHAP 사전 계산 → `backend/data/processed/feature_details.parquet` (252 rows × 13 cols, `shap_top_json` 컬럼) |
| T2 (A.1~A.4) | `a28111f` | FastAPI 셋업. `backend/requirements-api.txt` 분리 (geopandas/shap 제외) + `backend/api/{__init__,main,routes,schemas,deps}.py` + `backend/src/config.py`에 `FEATURE_DETAILS_PATH` 승격 (외부 평가 9번) |
| T3 (A.5~A.8) | `2d57d66` | 4 GET endpoints (`/api/health`, `/api/features`, `/api/features/{sgg_code}`, `/api/top10`) |
| T4 (A.9) | `fda430b` | `POST /api/simulate` (haversine + xgboost 재추론, geopandas 의존 X). 인제군 sanity 통과 (24.2→8.17 km, risk_delta -0.230) |
| T5 (A.10) | `d3d534d` | `GET /api/contrast` (외부 평가 7번 핵심). 사고건수 순위 vs BlindZone 순위 비교 |
| T6 (A.11~A.12) | `fb636b6` | `backend/tests/test_api.py` 8개 통합 테스트. 전체 suite 20 PASS (8 신규 + 11 data pipeline + 1 train). httpx는 dev-only로 .venv 직접 설치, requirements-api.txt에는 미포함 |

### Phase B (Next.js 프론트엔드) — 진행 중

| Task | Commit | 내용 |
|---|---|---|
| T7 (B.1~B.4) | `0d21ec7` | Next.js 14 셋업 (create-next-app + maplibre-gl/react-map-gl/deck.gl). `frontend/lib/types.ts`, `frontend/lib/api.ts` (6 endpoint 매핑), `frontend/components/Nav.tsx`, `frontend/app/layout.tsx` (한국어·BlindZone 메타). `.env.local` (gitignored), `.env.local.example`. `tsc --noEmit` 통과 |
| T8 (B.5) | — | **다음 세션 시작점.** `frontend/components/RiskMap.tsx` 작성. 외부 평가 5번 핵심: `import Map` → `import MapLibreMap` rename + `new globalThis.Map()` (shadowing 버그 fix). dispatch 두 번 실패 (87분 stuck + 529 overloaded) → 아직 시작 안 함 |
| T9 (B.6) | — | MetricCard + ShapExplanation + Top10Table + ContrastPanel 4 컴포넌트 |
| T10 (B.7~B.9) | — | 3 페이지 (시민/정책/About — About에 정직성 8개 정정 적용) |
| T11 (B.10~B.12) | — | `tsc --noEmit` + `npm run build` 최종 검증 + Phase B commit |

### Phase C (배포) — pending

| Task | 내용 |
|---|---|
| T12 (C.1~C.3) | `backend/Procfile` + `backend/railway.json` (requirements-api.txt build) + Vercel 설정. 실제 배포는 한태영 액션 |

### Phase D (정정·증빙·제출) — pending

| Task | 내용 |
|---|---|
| T13 (D.1) | README 정정 — 8개 위험표현 적용 |
| T14 (D.2) | `docs/submission/ai-tool-evidence.md` |
| T15 (D.3) | `docs/submission/case-study.md` — 대표 사례 1개 (인제군 또는 옹진군 추천) |
| T16 (D.0/D.4/D.5/D.6) | 한태영 액션: 통계누리 hNum=283 zip 다운로드 → 참가신청서·서약서·기획서 HWP → 데모 영상 → 제출 |

---

## ⚠️ 중요한 발견 (오늘) — narrative 정정 필요

**`/api/top10`와 `/api/contrast`의 실제 결과가 stale 문서와 어긋남.** 이전 문서의 "blind zone 10개 시군구 (이천·제천·증평·정읍·김천·구미·영천·창원의창/마산합포·서귀포)" 명단은 **현재 모델 출력과 zero overlap**. 

**실제 `/api/top10`** (현재 feature_details.parquet 기준, 위험지수 내림차순):

1. 송파구 (11240) — 0.4078
2. 인제군 (32590) — 0.3963
3. 동대문구 (11060) — 0.3580
4. 옹진군 (23520) — 0.3000
5. 영등포구 (11190) — 0.2996
6. 달서구 (22070) — 0.2913
7. 북구 (22050) — 0.2901
8. 중랑구 (11070) — 0.2525
9. 강동구 (11250) — 0.1872
10. 수성구 (22060) — 0.1826

**실제 `/api/contrast`** (사고 TOP10 vs BlindZone TOP10 비교):

- `blindzone_top10_not_in_accident_top10`: **3** (인제·옹진·수성)
- `accident_top10_not_in_blindzone_top10`: **3** (강북·은평·구로)
- 핵심 outlier:
  - **인제군**: accident_rank=245, risk_rank=2, **rank_diff=+243**, accident_count=1
  - **옹진군**: accident_rank=246, risk_rank=4, **rank_diff=+242**, accident_count=0
  - 수성구: rank_diff=+3 (약함)

**해석**: "통계 사각지대 3곳" 자체는 약한 숫자지만, **인제·옹진 두 사례가 극단적 outlier** — 사고 0~1건인데 BlindZone TOP4 진입. 이게 가장 강한 narrative. 수성구는 묶지 말고 두 사례에 집중하는 게 발표 임팩트 큼.

**정정 대상 (T13 README, T15 case-study, About 페이지 = T10)**:
- "blind zone 10개 시군구 (이천·제천…)" → 갱신된 실제 TOP10
- "blindzone TOP10 중 N곳" → "3곳"
- 대표 사례 1개 = **인제군** (사고 1건 → BlindZone rank 2, EMS 거리 24.2km) 강력 추천
- 모델 가중치 (사고 0.4 / 사망률 0.3 / EMS 0.3)는 도시 편향 — 약점이긴 한데 정직히 인정 (가중치 0.4/0.3/0.3은 임의 선택이라는 표현 이미 PROJECT_SPEC에 있음)

---

## 🔔 새 세션 시작 시 — 한태영에게 먼저 물어볼 것

**없음.** Plan v2 OK + Subagent-driven 모드 a) 이미 확정. T8부터 그대로 이어서 dispatch하면 됨. 

다만 진행 중 어느 시점에든 "narrative 정정은 어디 task에서 묶을지" 결정 필요 (T10 About 작성하면서 같이? 또는 T13 README와 함께?). 메인이 그때그때 자연스럽게 끼워 넣어도 OK.

---

## 다음 할 일

**즉시 (다음 세션 첫 작업)**:
- [ ] T8: `frontend/components/RiskMap.tsx` 작성. plan v2 Task B.5 (line 959~1094) 그대로. 핵심: `import MapLibreMap from "react-map-gl/maplibre"` + `new globalThis.Map(...)`. 외부 평가 5번 권장사항.
- [ ] T8 끝나면 spec + code quality review → T9 (4 컴포넌트, ContrastPanel 포함)

**그 다음**: T9 → T10 → T11 → T12 → T13/T14/T15 → T16 (한태영 액션)

**한태영 액션 대기 (Phase C/D 일부)**:
- [ ] Railway 가입 + 배포 (T12 후)
- [ ] Vercel 가입 + 배포 (T12 후)
- [ ] 통계누리 hNum=283 zip 다운로드 → 참가신청서·서약서·기획서 HWP 확보 (T16)
- [ ] 기획서 3장 작성, 데모 영상 녹화 (T16)

---

## 보조 산출물

- `C:\Users\한태영\Desktop\BlindZone_프로젝트_개요.html` (28 KB, 12 섹션) — 비전공자용 단일 HTML 브리핑. 정직성 8개 표 포함. 가족·친구·심사위원에게 보여주기용. 한태영 직접 더블클릭으로 열기

---

## 막힌 곳 / 미해결 질문

- T7 implementer subagent가 87분 stuck 후 API 500으로 죽음 (npm install + maplibre/deck.gl 단계). 메인이 직접 인수받아 마무리. **T8 subagent 530 overloaded로 시작도 못 함 (2026-05-23)** — 서버 측 일시 이슈. 다시 dispatch하면 됨.
- 향후 npm install 같은 IO 무거운 작업은 메인이 직접 background로 돌리고 그동안 파일 작성을 병행하는 패턴이 더 안정적.

---

## 최근 결정

- 2026-05-22: a) 옵션 선택 — narrative 정정은 T5 결과 본 후 통합 (지금 받음, 위 발견 사항 참조)
- 2026-05-22: deps.py의 `FEATURE_DETAILS_PATH`를 `backend/src/config.py`로 승격 (code reviewer 권장)
- 2026-05-22: 백엔드 6 endpoint 각각 개별 commit (plan v2의 A.12 한방 commit 의도와 deviate). 결과적으로 git 이력이 더 읽기 좋음
- 2026-05-22: pytest TestClient 의존 `httpx`는 dev-only → `.venv`에 직접 설치, `requirements-api.txt`에는 미포함 (Railway 런타임 최소화)

---

## Skill 모드 메모

- Subagent-driven-development 모드 사용 중. 각 task: implementer dispatch → spec review subagent → code quality review subagent → complete.
- 단순 셋업·파일 작성은 메인 직접 처리하는 게 더 빠르고 안정적임 (T7 후반부 사례). 무거운 task (RiskMap, 페이지 3개)는 subagent dispatch 유지.
