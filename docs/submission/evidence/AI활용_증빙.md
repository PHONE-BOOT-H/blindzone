# AI 활용 증빙 — BlindZone

> 2026 국토교통 데이터 활용 경진대회 가점(AI 학습도구·AI 분석도구) 증빙자료.
> HWP/DOCX/PDF 별첨용. 그림은 같은 폴더의 PNG, Claude Code 대화 캡처만 직접 추가하면 완성.

---

## 1. AI 분석도구 — XGBoost + SHAP

정의한 잠재 위험지수를 XGBoost 회귀로 학습(재현도 R²=0.90, MAE=0.0079)하고,
SHAP TreeExplainer로 **지역별로 어떤 요인이 위험지수를 끌어올렸는지** 설명했다.
(사고·사망 예측이 아니라, 정의식의 기여요인을 분해하는 설명 레이어다.)

### 그림
- **01_xgboost_feature_importance.png** — XGBoost 변수 중요도(gain). 사고 건수와
  응급기관 거리가 상위 기여.
- **02_shap_summary.png** — SHAP 요약(beeswarm). 각 시군구 위험지수에 변수가 미친
  방향·크기. `ems_distance_km`(응급기관 거리)가 핵심 요인으로 확인.
- **03_shap_bar.png** — 변수별 평균 기여도(mean |SHAP|).
- **04_shap_inje_waterfall.png** — 인제군 한 곳의 위험지수를 변수별 기여로 분해
  (응급거리 기여가 가장 큼).

### 코드·서비스 반영
- 학습: `backend/src/train.py` (XGBRegressor)
- SHAP 사전계산: `backend/scripts/precompute_shap.py` → `feature_details.parquet`
- 재현: `backend/scripts/make_evidence.py` (위 그림 생성)
- 서비스: 시민 모드에서 시군구 클릭 시 "왜 위험한가" 기여요인으로 표출

---

## 2. AI 학습도구 — Claude Code

코드 작성·수정·디버깅·배포 전 과정에서 Claude Code(Anthropic)를 보조 도구로 활용했다.
**모든 커밋 메시지에 `Co-Authored-By: Claude Opus`를 명시**해 기여를 투명하게 기록했다.
(단순 검색이 아니라, 실제 코드·문서·분석 산출물 생성에 직접 사용.)

- 총 74개 커밋 중 Co-Authored-By: Claude 명시 16건(검증 기간 집중분).
- 활용 예시(커밋 로그):

| 커밋 | 내용 |
|---|---|
| 08a56a1 | 외부검증·도로 실거리 robust 재산출 + 가점표현 정직화 |
| 84d3845 | 레버1·4 — 고령 수요 교차분석 + 수혜인구 |
| 68a5a76 | 다발지점 vs 전체 교통사고 대조 분석 |
| f08ee6b | 정적 fallback + 배포 — 백엔드 다운 시에도 데모 동작 |
| 3ea4a71 | HF Spaces Docker 설정 + 배포 |
| 3754f3d | About 페이지 공개용 재작성 |

- 활용 영역: Next.js 지도 UI·정적 fallback(`frontend/lib/api.ts`), FastAPI 엔드포인트,
  HF Spaces 배포(`Dockerfile`), 분석 스크립트(가중치 민감도·OSRM 실거리·SHAP) 등.
- 판단 영역(사람): 데이터셋 선택, 지표·가중치 설계, 발견 해석, 정직성 표현은 직접 결정.

### 추가 첨부 (캡처 — 직접 넣기)
- [ ] Claude Code 대화 화면 1~2장: "질문 → 생성 코드/해결책 → 실제 반영 파일" 흐름
  (예: fallback 구현, 배포 오류 수정). 터미널/대화 캡처라 본인 화면에서 캡처 필요.
- [ ] GitHub 커밋 상세 1장: 커밋 메시지의 `Co-Authored-By: Claude Opus` 줄이 보이게.

---

## 첨부 파일
- 01_xgboost_feature_importance.png
- 02_shap_summary.png
- 03_shap_bar.png
- 04_shap_inje_waterfall.png
- (추가) Claude Code 대화 캡처 · GitHub 커밋 상세 캡처
