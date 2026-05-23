# Prior Art — 선행 연구 인지

> BlindZone과 가까운 선행 연구를 사전 조사하고, 본 프로젝트의 차별점을 정리한 문서. 발표·기획서 작성 시 출처 인용 백업.

조사 일자: 2026-05-23
검색 범위: Google Scholar (영문), KCI/DBpia (국문), 정부 공식 채널(국토교통부 통합 데이터 채널, KOTI, MDPI, ASCE, Sage), 약 40여 건 제목 스캔 + 핵심 5건 본문 추적

---

## 1. 가장 가까운 선행 — Jung & Qin 시리즈

### [A] Jung, S. & Qin, X. (2025). "Data-Driven Analysis to Inform National Strategies on Improving Post-Crash Care."

- 출처: *Transportation Research Record*, Sage
- 링크: https://journals.sagepub.com/doi/10.1177/03611981251351888
- 핵심: 한국 데이터 사용 + **XGBoost + SHAP** 정확히 적용. 사고 심각도(crash severity) 영향 요인 식별 목적. 시공간 속성(현장도착시간, 고속도로 본선, 야간) 핵심 요인 도출
- **BlindZone과 차이**:
  - 분석 단위가 **개별 사고건**이지 시군구 252개 행정단위가 아님
  - "사각지대 발굴"이나 "가상 응급거점 추가 시뮬레이션"은 없음
  - 풀스택 웹서비스가 아니라 학술 분석

### [B] Jung, S. & Qin, X. (2024). "Promoting Emergency Medical Service Infrastructure Equality to Reduce Road Crash Fatalities."

- 출처: *Sustainability* 16(3): 1000, MDPI
- 링크: https://www.mdpi.com/2071-1050/16/3/1000
- 핵심: **한국 EMS 인프라 + 사고 사상자 데이터 융합**. 16-20분 응급 대응시간 구간이 사망률 유의 증가와 연결. 지리가중 이항 로짓 회귀(GWLR) 사용. EMS 스테이션·병원·헬기·헬리포트 입지 우선순위 제안
- **BlindZone과 차이**: 목적은 가장 유사하나
  - XGBoost/SHAP 아님 (GWLR)
  - **What-if 시뮬레이션 없음**
  - 시군구가 아니라 **충청권 중심 점단위 분석**
  - 웹서비스 아님

### [C] Jung, S., Qin, X., & Oh, C. (2020). "Connecting Motor Vehicle Crashes with EMS Performance: Spatial Assessment for the Korean Freeway System."

- 출처: *J. Transp. Eng. A: Systems* 146(6), ASCE
- 링크: https://ascelibrary.org/doi/10.1061/JTEPBS.0000354
- 핵심: 한국 **고속도로 한정** + EMS 응답시간 + 사고 공간자기상관 분석. 동남/서남/수도권 3지역이 심각사고 군집 + 응답시간 길고 EMS 시설 적음 확인
- **BlindZone과 차이**: 고속도로 전용, 시군구 단위 행정 사각지대 발굴 아님, 국도/지방도 미포함

### [D] Jang et al. (2020). "Analysis of accessibility to emergency rooms by dynamic population from mobile phone data."

- 출처: *PLOS One*
- 링크: https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0231079
- 핵심: 모바일 통신 동적 인구 + 응급실 접근성 결합. 한국 사회 불평등 지리 분석
- **BlindZone과 차이**: 응급실 접근성에 집중 (교통사고 결합 X), 시군구 단위 위험지수 산출이 목적 아님

### 기타 인접 연구

- 인천광역시 응급의료 취약지 GIS 서비스 권역 분석 (KCI 등재) — 시 단위, 사고 미결합
- 서울시 응급의료 취약지역 분석 (국민대 학부 문헌연구보고서, 2025) — 학부 수준, 사고 미결합
- 전국 보행자 사망사고 XGBoost 모델 (ScienceDirect, 2025) — 보행자 한정, 응급의료 미결합

---

## 2. 데이터 융합 측면 (TAAS + 응급의료 + 119 + 행정경계 4종)

**4종 모두 한 분석에서 융합한 선행: 검색 범위 내 발견되지 않음.**

- TAAS + EMS 결합: 다수 존재 ([A][B][C])
- TAAS + 119 구급통계 결합: KOTI/소방청 별도 분석 존재하나 학술 결합 사례 미발견
- 4종 동시 + 시군구 252개 전국 단위: 검색 범위 내 미발견

가장 가까운 [B]도 사고 + EMS 인프라 2종 중심이며, 119 구급통계나 시군구 행정경계 폴리곤 매칭은 부수적.

---

## 3. 방법론 측면

### XGBoost + SHAP을 한국 교통/응급 도메인에 적용

이미 다수 존재 (특히 [A] Jung & Qin 2025). 보행자 사고 심각도, 고속도로 사고 검지 등 응용 풍부.

### "가중합 위험지수 → XGBoost surrogate 학습" 패턴

위험지수 자체를 가중합으로 정의 후 ML로 재학습하는 surrogate 방식은 검색 결과에서 한국 교통 도메인 직접 사례 미발견. (위험성 평가/환경 점수 산정에서 min-max + 가중합은 표준 기법이지만 ML surrogate화는 드묾.)

### What-if 시뮬레이션 (가상 응급거점 추가 → 거리 피처 재계산 → 동일 모델 재추론)

한국 EMS 도메인에서 인터랙티브 What-if 패턴 미발견. 시설 입지 최적화는 별도 분야(robust optimization, location-allocation)로 존재하나, 학습된 ML 모델에 피처 재주입하는 BlindZone식 접근과는 다름.

---

## 4. BlindZone 차별점 정리

### Unique (선행 미발견)

1. **시군구 252개 전국 단위** 잠재 위험지수 산출 — 점단위/고속도로/광역시 한정 선행과 다른 분석 단위
2. **4종 데이터 동시 융합** (TAAS + 응급의료기관 + 119 구급통계 + 행정경계)
3. **가중합 위험지수 + XGBoost surrogate + SHAP 기여요인** 결합 파이프라인
4. **인터랙티브 What-if 시뮬레이션** (가상 응급거점 추가 → 거리 재계산 → 동일 모델 재추론)으로 정책 시나리오 평가
5. **풀스택 웹서비스** (MapLibre + deck.gl + FastAPI) — 선행은 모두 학술 분석 산출물

### 기존 방법론 활용 (독창성 X, 그러나 정상)

- XGBoost + SHAP 자체는 한국 교통 도메인 응용 풍부 ([A], 그 외 다수)
- min-max + 가중합 위험지수는 환경/안전 평가 표준 기법
- 응급의료 접근성 직선거리/네트워크거리 계산은 다수 선행

---

## 5. 입상 가능성 시사점

**독창성 강도: 중상(中上)**. 개별 구성요소는 선행이 존재하나, **(a) 시군구 252개 전국 단위 + (b) 4종 융합 + (c) What-if 인터랙티브 시뮬레이션 + (d) 풀스택 웹서비스**의 결합은 검색 범위 내 동등 사례 미발견. Jung & Qin 시리즈가 가장 가까운 선행이지만 분석 단위·도구·산출 형태가 다름.

### 권장 포지셔닝

- 발표자료·기획서에 Jung & Qin (2024 Sustainability, 2025 TRR) **명시 인용**하여 "선행 인지 + 확장" 프레임으로 포지셔닝. 모르는 척하면 심사위원이 알 때 신뢰 손상.
- "What-if 시뮬레이션 + 시군구 행정단위 + 119 구급통계 결합"을 핵심 차별점으로 강조. 이 세 가지가 동시 존재하는 선행은 미발견.
- AI 학습·분석·데이터융합 가점 신청은 모두 정당화 가능 — surrogate 학습은 AI 학습, SHAP은 분석, 4종 결합은 융합.

### 한계 보강 권장 (시간 되면)

- 직선거리 → 실제 도로망 거리/응급차 평균 속도 미반영
- 인구밀도·고령자 비율 등 수요측 변수 추가 시 정합성 ↑

---

## 6. 검색 한계 (정직 고지)

- Google Scholar/KCI/DBpia 키워드 상위 결과 + WebSearch 도구 한계
- **KOTI/KoROAD 비공개 내부 보고서, 미발표 공모전 출품작은 확인 불가**
- "발견되지 않음 = 존재하지 않음"이 아님을 주의
- 본 문서는 BlindZone의 절대적 독창성을 단정하지 않으며, 검색 범위 내 동등 사례가 발견되지 않았음을 보고함

---

## 부록 — 출처 URL

### 직접 선행 연구

- Jung & Qin (2025) "Data-Driven Analysis to Inform National Strategies on Improving Post-Crash Care" (Sage TRR): https://journals.sagepub.com/doi/10.1177/03611981251351888
- Jung & Qin (2024) "Promoting EMS Infrastructure Equality to Reduce Road Crash Fatalities" (MDPI Sustainability): https://www.mdpi.com/2071-1050/16/3/1000
- Jung, Qin & Oh (2020) "Connecting Motor Vehicle Crashes with EMS Performance: Korean Freeway" (ASCE JTE): https://ascelibrary.org/doi/10.1061/JTEPBS.0000354
- Jang et al. (2020) "Analysis of accessibility to emergency rooms by dynamic population" (PLOS One): https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0231079
- Real-Time Traffic Information EMS Vulnerability (MDPI Applied Sciences 2020): https://mdpi.com/2076-3417/10/18/6492/htm

### 인접/방법론 선행

- Pedestrian Crash High-Risk Areas, Korea (ScienceDirect 2025): https://www.sciencedirect.com/science/article/pii/S0966692325001073
- XGBoost + SHAP for Freight Truck Crashes (ScienceDirect): https://www.sciencedirect.com/science/article/abs/pii/S0001457521001846
- Predicting Road Traffic Injury Severity with Boosting + SHAP (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC8910532/
- Urban-Rural Crash Injury Severity Korea (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC7141985/
- Bayesian Spatial Logit EMS Response Time Korea (PMC): https://pmc.ncbi.nlm.nih.gov/articles/PMC11540930/

### 한국 국내 자료

- GIS 서비스 권역 분석을 활용한 인천광역시 응급의료 취약지 분석 (KCI): https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002966067
- 서울시 응급의료 취약지역 분석 (국민대 2025 학부 문헌연구): https://culture.kookmin.ac.kr/gulmal/contests/5/applicants/731/attach
- GIS 노인·어린이 교통사고 다발지역 분석 (KCI): https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002840789
- 의료시설 접근성의 지역 간 격차와 결정 요인 (KPAJ): https://www.kpaj.or.kr/xml/41208/41208.pdf
- 응급의료서비스 접근성 천차만별 (의협신문): https://www.doctorsnews.co.kr/news/articleView.html?idxno=140560
- TAAS 교통사고분석시스템: https://taas.koroad.or.kr/
- 응급의료통계포털 (NEMC): https://e-medis.nemc.or.kr/
- 소방안전 빅데이터 플랫폼: https://bigdata-119.kr/
- 국토교통부 데이터 통합 채널 (경진대회): https://data.molit.go.kr/
