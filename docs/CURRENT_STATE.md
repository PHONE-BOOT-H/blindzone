# CURRENT_STATE — 현재 진행 상황

> 매 세션 끝낼 때 업데이트. 새 세션 시작 시 Claude가 가장 먼저 읽는 파일.

---

## 마지막 업데이트
2026-05-19 — 브레인스토밍·디자인 확정, implementation plan 작성 직전

---

## 어디까지 왔는지

- 프로젝트 셋업 완료 (goingmerry 템플릿, CLAUDE.md, git 초기화)
- 대회 요건 파악 완료 (제품/서비스 트랙, 1인 출품, K-MaaS 제외)
- **아이디어 확정**: BlindZone — 사고위험 × 응급사각지대 융합 발굴 서비스
- **시제품 형태 확정**: S3 하이브리드 단일 웹앱 (시민 ↔ 정책 모드 토글)
- **기술 스택 확정**: Streamlit + Folium + XGBoost + SHAP (T1)
- **데이터 가용성 검증 완료**: TAAS, 전국응급의료기관, 119 통계, 도로망 모두 공개
- **디자인 스펙 작성·커밋 완료**: `docs/superpowers/specs/2026-05-19-blindzone-design.md` (커밋 `edf858e`)

---

## 다음 할 일

- [ ] **`writing-plans` skill로 implementation plan 작성** (현재 단계)
- [ ] Plan 승인 후 데이터 다운로드·EDA 시작 (D+1~2)
- [ ] 한태영이 [국가교통 데이터 오픈마켓](https://www.bigdata-transportation.kr) FAQ 확인해서 1차 심사 제출물 양식 파악 (병행)

---

## 막힌 곳 / 미해결 질문

- 1차 심사 제출물 정확한 양식·매수 — 대회 사이트 FAQ 확인 필요
- "잠재 위험 지수" 정확한 수식 — EDA 단계에서 결정
- 시군구 단위 인사이트 강도 — EDA로 검증, 약하면 1km 격자 전환

---

## 최근 결정 (자세히는 `docs/superpowers/specs/2026-05-19-blindzone-design.md`)

- 2026-05-19: 프로젝트명 `molit-2026`, 코드네임 `BlindZone`
- 2026-05-19: 제품/서비스 트랙 + 일반 시상 트랙 (K-MaaS 특별상 제외)
- 2026-05-19: 도메인 = 교통안전 (C), 영역 = G2-β (사고위험 × 응급사각지대 융합 발굴)
- 2026-05-19: 시제품 = S3 하이브리드 (시민 모드 메인 + 정책 시뮬레이터 보조)
- 2026-05-19: 스택 T1 (Streamlit + Folium + XGBoost + SHAP, Python 단일)
- 2026-05-19: V1 = 시군구 단위, V1.1 = 1km 격자
- 2026-05-19: AI 가점 = Claude Code(학습 5점) + XGBoost·SHAP(분석 5점) + 데이터융합(5점) = 합 15/25
