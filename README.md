# BlindZone — 보이지 않던 위험지대

> 2026 국토교통 데이터 활용 경진대회 출품작 (제품/서비스 트랙)
>
> 사고는 적은데 죽음은 많은 곳, 데이터로 찾았습니다.

## 무엇

한국 교통사고 골든타임 놓침으로 인한 사망률은 선진국의 2배. BlindZone은 사고 위험 × 응급 도달 시간을 결합해 통계가 가려둔 잠재 위험지대를 발굴하고, 응급 자원 추가 배치를 시뮬레이션하는 웹 서비스입니다.

## 데모

(Streamlit Cloud 배포 후 URL 추가)

## 로컬 실행

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# data/raw/에 4개 공공데이터 파일 배치 (다운로드 가이드: scripts/download_data.py)
# TAAS 다발지역(csv), 시군구 경계(geojson)은 수동 다운로드
# 응급의료기관, 119 구급통계는 API 자동 호출 (인증키 .env에 설정 필요)
python scripts/fetch_api_data.py

# 데이터 가공 + 모델 학습
python scripts/build_features.py
python -m src.train

# 앱 실행
streamlit run app.py
```

## 기술 스택

Python · Streamlit · Folium · XGBoost · SHAP · GeoPandas

## 데이터 출처

- TAAS 교통사고분석시스템 (한국도로교통공단)
- 전국응급의료기관표준데이터 (보건복지부)
- 소방청 119구급서비스 통계
- 시군구 행정경계 (통계청 SGIS)
