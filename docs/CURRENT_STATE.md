# CURRENT_STATE — 현재 진행 상황

> 매 세션 끝낼 때 업데이트. 새 세션 시작 시 Claude가 가장 먼저 읽는 파일.

---

## 마지막 업데이트
2026-05-20 — Streamlit prototype 폐기, 풀스택(Next.js + FastAPI) 전환 진행 중. 시군구 GeoJSON 새 출처 다운로드 대기.

---

## 어디까지 왔는지

**Phase 1~2 (셋업·데이터)** ✅
- Python venv + requirements (backend로 이동)
- 디렉토리 구조 + `backend/src/config.py`
- raw 데이터: TAAS 다발지역 (12,780행), 응급의료기관 (534행), 119 구급통계 (12,789행)
- 시군구 경계 GeoJSON — **출처 미확인 (구 파일)**. 새로 받기 예정.

**Phase 3 (가공, TDD)** ✅
- 7개 함수 + 11 unit tests
- TAAS 시도시군구명 → sgg_code 매핑 (100% 성공, alias 처리 포함)
- `grid_features.parquet`: 250 시군구 × 12 컬럼 (0 NaN)

**Phase 4 (모델)** ✅
- XGBoost R²=0.90, MAE=0.0087
- SHAP 설명 모듈
- 가상 응급기관 What-if inference 모듈

**Phase 5~7 (Streamlit prototype)** → **폐기** (풀스택 전환)
- 기존 Streamlit UI 코드 모두 삭제 (commit `eb9a1f5`)
- 디렉토리 재구조화: 모든 Python 코드 → `backend/`, `frontend/` placeholder (commit `0c30...` 또는 마지막 commit)

**문서 작업**
- 디자인 스펙: `docs/superpowers/specs/2026-05-19-blindzone-design.md`
- 이전 implementation plan: `docs/superpowers/plans/2026-05-19-blindzone-implementation.md` (Streamlit 기준 — 새 plan으로 교체 예정)
- PROJECT_SPEC: 풀스택 + 심사 기준 + 가점 신청(15점) + 1차 양식 (기획서 3장) 반영
- About 페이지·README: 정정 필요 (이전 Streamlit 시기 산출물에 출처 부정확 — 풀스택 전환 후 같이 정정)

---

## 다음 할 일

**즉시**:
- [ ] **한태영이 VWORLD에서 시군구 경계 받기** (https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?dsId=30604)
- [ ] 받은 파일 `backend/data/raw/` 배치 (기존 `시군구_경계.geojson` 교체 또는 새 파일명)
- [ ] `backend/scripts/inspect_data.py` 재실행해서 컬럼 확인 (SHP면 .shp/.dbf/.shx/.prj 함께)
- [ ] 필요 시 `backend/src/data_pipeline.py`의 컬럼 alias 조정
- [ ] `backend/scripts/build_features.py` 재실행 → grid_features.parquet 갱신
- [ ] `backend/src/train.py` 재실행 → xgb_risk_model.pkl 갱신
- [ ] commit (새 데이터 출처 명시)

**그 다음**:
- [ ] 새 implementation plan 작성 (writing-plans skill) — 풀스택 Phase 분해
- [ ] FastAPI 백엔드 작성 (Phase A): endpoints, CORS, 로컬 테스트, 모델 로드
- [ ] Next.js 프론트 작성 (Phase B): 페이지 3개, 지도, 차트, API 연동
- [ ] 배포 (Phase C): Vercel + Railway
- [ ] About/README 정정 + 가점 약화 + 출처 정확화
- [ ] 기획서 (3장, 한글 양식) 작성
- [ ] 데모 영상 (1~2분) 녹화
- [ ] AI 학습도구 증빙자료 (Claude Code 사용 로그) 준비
- [ ] 최종 점검 + 제출 (2026-05-29 마감)

---

## 막힌 곳 / 미해결 질문

- 시군구 GeoJSON 새 출처 다운로드 — 한태영 작업 중
- FastAPI endpoint 정확한 응답 schema 설계 (새 plan에서)
- Railway 배포 시 모델 파일 처리 (git 포함 vs build-time train)
- AI 학습도구 증빙 형식 (스크린샷? 로그? 코드 PR?)

---

## 최근 결정 (자세히는 `docs/superpowers/specs/...`)

- 2026-05-19: 코드네임 `BlindZone`, 제품/서비스 트랙, K-MaaS 제외
- 2026-05-19: 도메인 = 교통안전, G2-β (사고위험 × 응급사각지대 융합 발굴)
- 2026-05-19: ~~T1 (Streamlit + Folium)~~ → **Next.js + FastAPI 풀스택로 변경** (2026-05-20)
- 2026-05-19: V1 = 시군구 단위, V1.1 = 1km 격자
- 2026-05-19: AI 가점 신청 — Claude Code(학습) + XGBoost·SHAP(분석) + 데이터 융합 = 합 15점 신청 가능 (심사위원 결정)
- 2026-05-20: 절대 원칙 — **"없는 것을 지어내지 않는다"** (memory 저장됨). 모든 산출물에 적용.
- 2026-05-20: 시군구 GeoJSON 출처 미확인 → VWORLD([dsId=30604](https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?dsId=30604))로 새로 받기
- 2026-05-20: 이전 Streamlit UI 코드 삭제 (`eb9a1f5`), backend/+frontend/ 재구조화
- 2026-05-20: 시간 제한 없이 깊이 추구 모드 (한태영 페이스)
