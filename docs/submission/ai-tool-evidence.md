# AI 도구 활용 증빙

> 2026 국토교통 데이터 활용 경진대회 가점 신청 증빙. 부여 여부는 심사위원단 판단.
> 증빙 그림은 `docs/submission/evidence/` 폴더.

## 가점 신청 항목

1. **AI 학습도구** — XGBoost 회귀로 정의된 위험지수를 학습·재현 (R²=0.90)
2. **AI 분석도구** — SHAP TreeExplainer로 시군구별 위험 기여요인 분석

> 데이터 융합(3종 + 119 교차검증)은 §3에 구현 내역으로 제시한다. 양식 가점의 "주관기관 융합데이터" 해당 여부가 불확실하여(본 데이터는 도로교통공단·국립중앙의료원·통계청 등으로 대회 주관기관과 별개), 기획서 자가체크에서는 데이터 융합을 신청하지 않았다. 해당 여부는 운영사무국 기준 확인 후 결정한다.
> (참고) 생성형 AI(Claude Code)는 코드·문서 작성 보조에 활용했고, 데이터 선정·지표 설계·해석 판단은 사람이 직접 수행했다(아래 §4).

---

## 1. AI 학습도구 — XGBoost 회귀

- **모델**: `xgboost.XGBRegressor`
- **목적**: min-max 정규화 후 가중합으로 정의한 잠재 위험지수를, 입력 변수(사고 빈도·사망사고 비율·응급기관 거리·도착 추정시간·면적)로 **학습·재현**.
- **성능**: R²=0.90, MAE=0.0079. 단 이는 사고·사망 예측 성능이 아니라 **정의식 재현도**다(과장 금지).
- **코드/산출물**: 학습 `backend/src/train.py`, 모델 `backend/models/xgb_risk_model.pkl`. 재현 `py -3.12 backend/src/train.py`.
- **증빙 그림**: `evidence/01_xgboost_feature_importance.png` (변수 중요도 — 사고 건수·응급거리 상위).

## 2. AI 분석도구 — SHAP TreeExplainer

- 학습된 모델에 `shap.TreeExplainer`로 **시군구별 기여요인**(위험 증가/감소 방향 포함)을 분해.
- 결과를 `feature_details.parquet`에 사전계산 → 시민 모드에서 시군구 선택 시 "왜 위험한가"로 노출.
- 인제군 예: 응급기관 거리(+0.173) > 사고 빈도(+0.072) > 사망사고 비율(+0.065) — 응급 접근성이 최대 기여.
- **증빙 그림**: `evidence/02_shap_summary.png`·`03_shap_bar.png`·`04_shap_inje_waterfall.png`.
- 코드: `backend/scripts/precompute_shap.py`, 재현 그림: `backend/scripts/make_evidence.py`.

## 3. 데이터 융합 — 3종 융합 + 119 교차검증

| 출처 | 형식 | 시군구 단위 변환 |
|---|---|---|
| 전국교통사고다발지역표준데이터 (한국도로교통공단 TAAS) | CSV | 다발지점 좌표 → 시군구 polygon spatial join → 사고 건수·사망/부상자 합산 |
| 국립중앙의료원 응급의료기관 정보 (B552657, 공공데이터 API) | API JSON | 시군구 중심점 → 최근접 응급기관 거리 |
| 시군구 행정구역 경계 (통계청 센서스경계, 브이월드) | SHP/GeoJSON | spatial join 기준 폴리곤 (CC BY-NC-ND) |
| 소방청 구급통계서비스 (1661000, 공공데이터 API) | API JSON | **risk_index 변수 미사용**. 도착시간 추정 현실성·다발지점 한계 교차검증 (인제 다발 1건 vs 119 교통구급 188건) |

- 융합 산출물: `grid_features.parquet`(252 시군구 피처), `feature_details.parquet`(+ SHAP). 세부: [data_manifest.md](data_manifest.md).

## 4. (참고) 생성형 AI 개발보조 — Claude Code

- **활용 범위**: 코드 작성·오류 수정·배포 설정·문서화 보조.
- **사람이 직접 수행**: 데이터 선정, 위험지수·가중치 설계, 발견 해석, 정직성 표현, 정책적 의미 도출.
- **투명성**: AI가 실질적으로 보조한 주요 커밋에 `Co-Authored-By: Claude Opus`를 명시해 활용 내역을 투명하게 기록했다. 자동 commit 없이 모든 출력은 검토 후 반영했다. 그중 대표 16건을 선별해 증빙하며, 전체 커밋 이력은 제출 시점 GitHub 저장소(`PHONE-BOOT-H/blindzone`) 기준으로 확인 가능하다.
- 별도 외부 AI 평가를 받아 위험 표현·방법론을 정정하는 등, 단일 도구에 의존하지 않고 교차 검증했다.

---

## 부여 여부

위 항목의 가점 부여는 **심사위원단 판단**에 따른다. (생성형 AI 개발보조는 가점 항목이 아니라 개발 투명성 차원의 고지다.)
