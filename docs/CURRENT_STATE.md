# CURRENT_STATE — 현재 진행 상황

> 매 세션 끝낼 때 업데이트. 새 세션 시작 시 Claude가 가장 먼저 읽는 파일.

---

## 마지막 업데이트
2026-05-20 — VWORLD 데이터 갱신·재학습 완료, 외부 AI 평가 받음, 보조 문서 작성 완료, **Plan v2 작성 직전**.

---

## 어디까지 왔는지

**Phase 1~2 (셋업·데이터)** ✅
- Python venv + requirements (backend로 이동)
- 디렉토리 구조 + `backend/src/config.py`
- raw 데이터: TAAS 다발지역 (12,780행), 응급의료기관 (534행), 119 구급통계 (12,789행)
- **시군구 경계 갱신 완료**: 통계청 (센서스경계) VWORLD SHP — `BND_SIGUNGU_PG.shp`, 252 시군구, CC BY-NC-ND, BASE_DATE 20250630
- `load_sgg_centers` finder에 `SIGUNGU_CD`/`SIGUNGU_NM` alias 추가, `build_features.py` 경로 SHP로 변경, 옛 출처 미확인 GeoJSON 삭제

**Phase 3 (가공, TDD)** ✅
- 7개 함수 + 11 unit tests
- TAAS 시도시군구명 → sgg_code 매핑 (이전 100% 성공, 새 SHP에서도 유지)
- `grid_features.parquet`: 252 시군구 × 12 컬럼 (0 NaN)

**Phase 4 (모델)** ✅
- XGBoost R²=0.900, MAE=0.0079 (재학습)
- SHAP 설명 모듈
- 가상 응급기관 What-if inference 모듈
- 인사이트 검증: blind zone 10개 시군구 (이천·제천·증평·정읍·김천·구미·영천·창원의창/마산합포·서귀포)

**디렉토리 재구조화** ✅
- 모든 Python 코드 → `backend/`, `frontend/` placeholder

**외부 AI 평가 + 보조 문서** ✅
- 외부 AI에 plan v1 평가 받음 → 핵심 발견 정리
- `docs/submission/external-review-2026-05-20.md` 보존
- `docs/submission/data_manifest.md` 작성 (출처·라이선스·가공식 표)
- `docs/submission/model_card.md` 작성 (surrogate model 명시)
- PROJECT_SPEC.md에 정직성 8개 위험표현·정정 표 추가

**문서 작업**
- 디자인 스펙: `docs/superpowers/specs/2026-05-19-blindzone-design.md`
- 이전 plan: `docs/superpowers/plans/2026-05-19-blindzone-streamlit-implementation-deprecated.md` (history)
- Plan v1 (Streamlit→풀스택): `docs/superpowers/plans/2026-05-20-blindzone-fullstack-implementation.md` (외부 평가 받은 대상)
- Plan v2 (외부 평가 반영): **작성 직전**

---

## 🔔 새 세션 시작 시 — 한태영에게 먼저 물어볼 것 (BLOCKING)

한태영이 2026-05-20에 세션을 일시 종료하면서 두 결정을 다음 세션으로 미룸. 새 세션의 Claude는 **첫 응답에서 이 두 질문을 한태영에게 직접 물어볼 것**. 답 받은 후 그에 따라 진행.

**Q1. Plan v2 통째 OK?** 또는 수정 의견?
- Plan 파일: `docs/superpowers/plans/2026-05-20-blindzone-fullstack-v2-implementation.md`
- 핵심 결정 사항: Phase 0 완료 ✅ / Phase A (FastAPI 6 endpoint + SHAP 사전계산 + /api/contrast 신규 + requirements 분리) / Phase B (Next.js 3페이지 + RiskMap `Map` shadowing 버그 fix + ContrastPanel + 정직성 8개 표현 정정) / Phase C (Railway + Vercel) / Phase D (제출서류 확인·AI 증빙·대표 사례·기획서·데모영상)

**Q2. Execution 모드?**
- **a) Subagent-driven** (메인 추천 — 각 task 끝 spec/quality review로 정직성 검증, 외부 평가 권장사항 quality control)
- b) Inline (한 세션 batch — 빠르지만 quality 약함)
- c) Hybrid (단순 task는 inline, 핵심 task는 subagent)

한태영 답 받으면:
1. 옛 task list (#10~#35는 Streamlit 시기 history)는 그대로 두거나 정리
2. plan v2의 task들을 새로 TaskCreate로 등록
3. Phase A.0 (SHAP 사전 계산)부터 dispatch 또는 inline 시작

---

## 다음 할 일

**즉시 (위 Q1+Q2 답 받은 후 메인 작업)**:
- [ ] 위 Q1+Q2 답 따라 task list 정리 + Phase A.0 시작
- [ ] 한태영의 추가 변경 요청 있으면 plan v2 부분 수정

**그 다음 (구현, 풀스택)**:
- [ ] Phase A: FastAPI 백엔드 (6 endpoint + SHAP 사전계산 + requirements-api 분리)
- [ ] Phase B: Next.js 프론트엔드 (3 페이지 + polygon choropleth + RiskMap 버그 fix + 비교 컴포넌트)
- [ ] Phase C: 배포 (Railway + Vercel)
- [ ] Phase D: 정정·제출 패키지 (About/README 정직성, AI 증빙, 기획서, 데모영상)

**한태영 액션 대기**:
- [ ] 국토교통부 통계누리 공지에서 참가신청서·서약서·기획서 HWP 다운로드
- [ ] 추후 GitHub repo 생성 + Vercel/Railway 가입·배포
- [ ] 기획서 3장 작성, 데모 영상 녹화

---

## 막힌 곳 / 미해결 질문

- 없음. Plan v2 작성 후 실행 모드 (subagent-driven 추천) 선택만 남음.

---

## 최근 결정

- 2026-05-19: 코드네임 `BlindZone`, 제품/서비스 트랙, K-MaaS 제외
- 2026-05-19: 도메인 = 교통안전, G2-β (사고위험 × 응급사각지대 융합 발굴)
- 2026-05-19: 절대 원칙 — "없는 것을 지어내지 않는다"
- 2026-05-20: ~~Streamlit~~ → **Next.js + FastAPI 풀스택**
- 2026-05-20: 시군구 GeoJSON = 통계청 (센서스경계) VWORLD SHP, CC BY-NC-ND. 옛 출처 미확인 GeoJSON 삭제
- 2026-05-20: 시간 제한 없이 깊이 추구 + 외부 AI 평가 통해 정직성·정확성 강화
- 2026-05-20: 외부 AI 평가 권장사항 **모두 반영** (Plan v2)
