# Data Manifest — BlindZone

> 본 프로젝트가 사용한 모든 공공데이터의 출처·다운로드일·가공 방식·라이선스를 한 표로 정리한다.
> 절대 원칙: 사용하지 않은 데이터는 명시하지 않는다.

## 사용 데이터

| 데이터 | 출처 (기관) | URL / End Point | 다운로드일 | 원본 포맷 | 가공 방식 | 라이선스 |
|---|---|---|---|---|---|---|
| 전국교통사고다발지역표준데이터 | 공공데이터포털 / 한국도로교통공단 TAAS | https://www.data.go.kr/data/15029185/standard.do | 2026-05-20 | CSV (cp949, 12,780행) | 시군구 단위 그루핑·집계 (`backend/src/data_pipeline.py` `aggregate_accidents_by_sgg`) | 공공데이터포털 표준데이터 (이용 제한 명시 사항 별도 확인) |
| 국립중앙의료원 응급의료기관 정보 조회 서비스 | 공공데이터포털 오픈 API / 국립중앙의료원 (NMC) | `https://apis.data.go.kr/B552657/ErmctInfoInqireService/getEgytListInfoInqire` | 2026-05-20 | XML → CSV 변환 (`backend/scripts/fetch_api_data.py`, 534행) | wgs84Lat/wgs84Lon으로 GeoDataFrame 생성 → 시군구 중심점과 nearest 거리(km) 계산 | 공공데이터포털 활용 신청 승인 (한태영 인증키 발급, 활용기간 2026-05-20 ~ 2028-05-20) |
| 소방청 구급통계서비스 | 공공데이터포털 오픈 API / 소방청 | `https://apis.data.go.kr/1661000/EmergencyStatisticsService/getTrafficAccidentEmgActStats` | 2026-05-20 | XML → CSV 변환 (12,789행, 2023년 필터링) | 시도본부별 페이지네이션 수집. **현재는 사고-구급 출동 빈도만 수집했고, 사건별 출동시간 컬럼이 없어서 응급 도착시간은 응급기관 거리 기반 추정으로 대체** (`backend/src/data_pipeline.py` `estimate_ems_response_time_min`) | 공공데이터포털 활용 신청 승인 |
| 시군구 행정경계 SHP (센서스경계) | 브이월드(V-World) 공간정보 다운로드 / 통계청 (KOSTAT) | https://www.vworld.kr → 다운로드 → 공간정보 다운로드 → "(센서스경계)시군구경계" | 2026-05-20 | SHP zip (`BND_SIGUNGU_PG.zip`, 252행, BASE_DATE 20250630, CRS EPSG:5186) | EPSG:5179 변환 → 중심점·면적 산출 (`backend/src/data_pipeline.py` `load_sgg_centers`). 폴리곤 원본 변경 없음, 분석 단위 추출(centroid)·CRS 재투영만 수행 | **CC BY-NC-ND** (저작자표시·비영리·변경금지). 출처: 통계청 (센서스경계)시군구경계 |

## 안 쓴 데이터 (참고)

다음은 다운로드만 받고 BlindZone V1에 **사용하지 않음** (혼동 방지용 명시):

- `LSMD_ADM_SECT_UMD_*.zip` (11개 시도 읍면동 단위) — V2 격자 세분화용 보관
- `센서스 공간정보 지역 코드.xlsx`, `센서스 공간정보 테이블 정의서.hwp` — 컬럼 정의서 참고용
- 2025년도 119구급서비스 통계연보 PDF — 데이터 형식상 시군구 단위 추출 어려워 API로 대체

## 데이터 결합 방법 (시군구 단위)

1. 시군구 경계 SHP → 250+개 시군구의 (sgg_code, sgg_name, area_km2, centroid in EPSG:5179)
2. TAAS 사고 다발지역 CSV → `사고다발지역시도시군구` 한글 문자열 파싱 + `SIDO_NAME_TO_PREFIX` 매핑 + `_TAAS_NAME_ALIAS` (행정구역 변경 대응) → sgg_code 부여 → 시군구별 사고 수·사망사고 비율 집계
3. 응급의료기관 → 각 시군구 중심점에서 가장 가까운 응급의료기관까지 거리(km) = `ems_distance_km`
4. `ems_response_min` = `ems_distance_km / 60 * 60` (시군구 평균 속도 60km/h 가정, 추정값)

## 잠재 위험 지수 정의

```
risk_index = 0.4 × minmax(accident_count)
           + 0.3 × minmax(fatality_rate)
           + 0.3 × minmax(ems_response_min + ems_distance_km)
```

각 항목은 min-max 정규화 후 가중합. 가중치는 임의 설정값(EDA에서 조정 가능), **실제 사고·사망을 직접 학습한 모델이 아닌 정의식**. 자세한 모델 한계는 `model_card.md` 참고.

## 좌표계 통일

- 한국 표준 분석 좌표계: **EPSG:5179** (KGD2002 / Korea 2000 Unified CS)
- WGS84 (EPSG:4326) 또는 EPSG:5186 입력은 자동 변환 (`backend/src/data_pipeline.py` `to_korean_crs`)
- 지도 시각화는 WGS84 (lon/lat)로 다시 변환 (Folium/MapLibre 기본)

## 재현성

본 manifest의 모든 데이터는 위 URL에서 동일 절차로 재취득 가능. API는 한태영의 공공데이터포털 인증키(`backend/.env`의 `DATA_GO_KR_API_KEY`)로 호출. 다른 사용자는 본인 키로 재취득.

스크립트:
- `backend/scripts/download_data.py` — 다운로드 가이드 (수동 항목)
- `backend/scripts/fetch_api_data.py` — API 자동 호출
- `backend/scripts/build_features.py` — 가공 + grid_features.parquet 생성
- `backend/src/train.py` — XGBoost 학습 + 직렬화
