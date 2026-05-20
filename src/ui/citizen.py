import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from src.shap_explain import explain_one
from src.viz import build_risk_map


def render(features: pd.DataFrame):
    st.title("우리 동네 응급 사각지대 확인")
    st.caption("사고는 적은데 죽음은 많은 곳 — 데이터로 발굴한 잠재 위험지대")

    left, right = st.columns([1, 2])

    with left:
        st.subheader("지역 검색")
        sgg_name = st.selectbox(
            "시군구 선택",
            sorted(features["sgg_name"].dropna().unique()),
            index=None,
            placeholder="시군구를 검색·선택하세요",
        )

        if sgg_name:
            row = features[features["sgg_name"] == sgg_name].iloc[0]
            st.metric("잠재 위험 지수", f"{row['risk_index']:.3f}")
            st.metric("연간 사고 건수", f"{int(row['accident_count'])}건")
            st.metric("평균 응급 도착시간", f"{row['ems_response_min']:.1f}분")
            st.metric("가장 가까운 응급기관 거리", f"{row['ems_distance_km']:.1f} km")

            st.subheader("왜 위험한가")
            try:
                explanations = explain_one(row)
                for e in explanations:
                    arrow = "↑" if e["shap_value"] > 0 else "↓"
                    st.write(f"- **{e['feature']}** {arrow} (영향도 {e['shap_value']:+.3f})")
            except Exception as ex:
                st.warning(f"SHAP 설명 로드 실패: {ex}")

    with right:
        st.subheader("전국 위험지도")
        m = build_risk_map(features, selected_sgg=sgg_name)
        st_folium(m, width=None, height=600, returned_objects=[])

    st.divider()
    st.subheader("전국 상위 잠재 위험지대 TOP 10")
    top = features.nlargest(10, "risk_index")[
        ["sgg_name", "risk_index", "accident_count", "fatality_rate", "ems_response_min", "ems_distance_km"]
    ].rename(
        columns={
            "sgg_name": "시군구",
            "risk_index": "위험지수",
            "accident_count": "사고건수",
            "fatality_rate": "사망사고비율",
            "ems_response_min": "평균출동(분)",
            "ems_distance_km": "응급기관거리(km)",
        }
    )
    st.dataframe(top, use_container_width=True, hide_index=True)
