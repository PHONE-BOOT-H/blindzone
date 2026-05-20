# External AI Review — 2026-05-20

> BlindZone implementation plan (`2026-05-20-blindzone-fullstack-implementation.md`)에 대한 외부 AI 평가 본문 보존.
> 한태영이 외부 AI 도구에 plan을 제출하고 받은 응답을 그대로 기록 (논리·표현 수정 X).

## 평가 요약

| 항목 | 등급 |
|---|---|
| 실현 가능성 | B- / 가능하나 범위 과다 |
| 구현 계획 완성도 | B+ / 매우 구체적 |
| 공모전 전략성 | B / 기술 중심, 성장성 설득 부족 |
| 정직성·검증 가능성 | C+ / 중요한 표현 리스크 있음 |
| 입상 가능성 | 중상위권 가능성은 있음. 단, 문서 전략과 데모 완성도가 좌우 |

## 핵심 권장사항 10가지

1. **Phase 0보다 먼저 공식 제출서류 확인** — 참가신청서·서약서·기획서 HWP를 국토부 공지(https://stat.molit.go.kr/portal/notice/noticeView.do?gubun=1&hNum=283)에서 선확보, `docs/submission/checklist.md`
2. **`data_manifest.md` + `model_card.md` 추가** — 정직성 핵심
3. **VWORLD `dsId=30604` 대신 `dsId=30015` 검토** — 30604는 공공누리 4유형(상업적 X·변경 X), 30015는 제한 없음 (한태영 결정: 통계청 (센서스경계) VWORLD `dsId=10825` 선택, CC BY-NC-ND)
4. **SHAP 사전 계산** — API 실시간 계산 X. `precompute_shap.py` → `feature_details.parquet`. Railway 메모리·응답속도 안정성
5. **RiskMap.tsx의 `Map` shadowing 버그 수정** — `import Map from "react-map-gl/maplibre"` + `new Map(...)` 충돌. `import MapLibreMap` + `new globalThis.Map(...)`
6. **정책 시뮬레이터 용어 통일** — "응급기관·분서" → "가상 응급의료 거점". 응급의료기관 ≠ 119안전센터
7. **사고건수 TOP10 vs BlindZone TOP10 비교 API** — `/api/contrast`. 독창성 30점 강화. "통계 사각지대 N개 발굴" 메시지
8. **About/README 첫 문단 정직하게** — "예측 모델" X → "탐색형 위험지수·민감도 분석"
9. **배포용 의존성 분리** — `requirements-api.txt` (FastAPI 런타임 최소), GeoPandas/SHAP은 학습용에만
10. **D-9 일정 다시 자르기** — 한태영 결정: 기한 무관 모드라 적용 X

## 위험 표현 6가지 (반드시 정정)

| 위험 표현 | 정정 |
|---|---|
| "사고 위험을 예측한다" | "공개 데이터로 정의한 잠재 위험지수를 계산하고 설명한다" |
| "응급 도착시간" | "응급의료기관 거리 기반 추정 접근시간 (60km/h 가정)" |
| "정책 시뮬레이터가 응급기관 추가 효과를 예측한다" | "가상 응급거점 추가 시 거리 기반 접근성 지표 변화 민감도 분석" |
| "연간 사고 건수" | "TAAS 사고다발지역 데이터 내 사고 건수" |
| "기존 일반인용 서비스는 부재했다" | "기존 사고다발지역 정보는 빈도 중심, 본 프로젝트는 응급 접근성을 결합한 탐색" |
| "주관기관 4종 결합" | "공공데이터 4종 결합" |
| "AI 가점 15점 확보" | "가점 신청 (부여는 심사위원단 판단)" |
| "R² > 0.5 = 모델 성능" | "정의된 잠재 위험지수에 대한 surrogate model 재현도" |

## 입상 가능성 강화 (선택, 시간 무관이라 모두 적용)

- 사고건수 TOP10 vs BlindZone TOP10 비교 (`/api/contrast`)
- 대표 사례 1개 발굴 ("이 지역은 사고 80위인데 BlindZone 7위")
- Polygon choropleth (centroid scatter 대신 시군구 면 색칠) — 시각 임팩트
- 사전 계산된 SHAP을 기획서 표로 첨부 (구체성 30점)
- 성장성 스토리 — 지자체·소방·응급의료 자원 배치 의사결정 도구 포지셔닝 (성장성 40점)

## 데이터·라이선스 노트

- TAAS 사고다발지역 = 전체 교통사고 X, 다발지점만. About/README에서 정확히 명시
- 119 출동 raw 비공개 → 거리×속도 추정. 추정임을 명시
- 시군구 경계 = CC BY-NC-ND, 비영리 출품 + 출처 명시로 사용 OK
- "주관기관 4종 결합" 검증 어려움 → "공공데이터 4종 결합"으로 약화

## 모델 한계

XGBoost는 **위험 예측 모델이 아니라 가중합 정의 위험지수를 재현하는 surrogate model**. R²/MAE는 사고 예측 성능이 아니라 surrogate 재현도. About/기획서에 명시 필요. → `model_card.md` 참고.

## 발표·심사 어필 스토리

> 사고가 많은 곳은 이미 모두가 압니다.
> BlindZone은 사고 빈도 지도에서 덜 보이지만, 사망위험과 응급 접근성이 결합될 때 위험해지는 지역을 찾습니다.

데모는 반드시 대표 지역 1곳을 잡아서 "사고건수 순위 X위, BlindZone 위험지수 순위 Y위" 비교 보여줄 것.

---

## 출처

- 외부 AI 평가 (한태영 전달, 2026-05-20)
- 인용 출처:
  - 국토교통부 통계누리 공지: https://stat.molit.go.kr/portal/notice/noticeView.do?gubun=1&hNum=283
  - 공공데이터포털 dsId=30604: https://www.data.go.kr/data/15125045/fileData.do
  - 공공데이터포털 dsId=30015 (센서스경계): https://www.data.go.kr/data/15125064/fileData.do
