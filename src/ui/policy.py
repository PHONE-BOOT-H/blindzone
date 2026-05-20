import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

from src.viz import KOREA_CENTER
from src.inference import simulate_new_ems


def render(features: pd.DataFrame):
    st.title("정책 시뮬레이터")
    st.caption("가상 응급기관·분서를 추가하면 어떤 변화가 생기나?")

    if "virtual_ems" not in st.session_state:
        st.session_state.virtual_ems = []

    left, right = st.columns([1, 2])

    with left:
        st.subheader("가상 응급기관 추가")
        lon = st.number_input("경도", value=127.0, format="%.4f")
        lat = st.number_input("위도", value=37.5, format="%.4f")
        if st.button("추가"):
            st.session_state.virtual_ems.append((lon, lat))
        if st.button("초기화"):
            st.session_state.virtual_ems = []

        st.write(f"현재 추가된 가상 응급기관: {len(st.session_state.virtual_ems)}개")
        for i, (lo, la) in enumerate(st.session_state.virtual_ems, 1):
            st.write(f"{i}. ({lo:.4f}, {la:.4f})")

    with right:
        st.subheader("시뮬레이션 결과")
        result = simulate_new_ems(st.session_state.virtual_ems)

        col1, col2, col3 = st.columns(3)
        avg_delta = result["risk_delta"].mean()
        max_drop = result["risk_delta"].min()
        improved = (result["risk_delta"] < -0.001).sum()
        col1.metric("평균 위험지수 변화", f"{avg_delta:+.4f}")
        col2.metric("가장 큰 위험 감소", f"{max_drop:+.4f}")
        col3.metric("개선된 시군구 수", f"{improved}개")

        # 지도: 감소가 큰 시군구 강조
        m = folium.Map(location=KOREA_CENTER, zoom_start=7, tiles="cartodbpositron")
        for _, row in result.iterrows():
            delta = row["risk_delta"]
            radius = max(3, min(15, abs(delta) * 500))
            color = "#2ca02c" if delta < 0 else "#cccccc"
            folium.CircleMarker(
                [row["lat"], row["lon"]],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                tooltip=f"{row['sgg_name']}<br>변화: {delta:+.4f}",
            ).add_to(m)
        for lo, la in st.session_state.virtual_ems:
            folium.Marker([la, lo], icon=folium.Icon(color="red", icon="plus")).add_to(m)
        st_folium(m, width=None, height=500, returned_objects=[])

    st.divider()
    st.subheader("개선 효과 TOP 10 시군구")
    top_improved = result.nsmallest(10, "risk_delta")[
        ["sgg_name", "risk_index", "risk_index_new", "risk_delta", "ems_distance_km_new"]
    ].rename(
        columns={
            "sgg_name": "시군구",
            "risk_index": "기존 위험",
            "risk_index_new": "신규 위험",
            "risk_delta": "변화",
            "ems_distance_km_new": "신규 응급기관거리(km)",
        }
    )
    st.dataframe(top_improved, use_container_width=True, hide_index=True)
