import folium
import pandas as pd

KOREA_CENTER = [36.5, 127.8]


def build_risk_map(features: pd.DataFrame, selected_sgg: str | None = None) -> folium.Map:
    m = folium.Map(location=KOREA_CENTER, zoom_start=7, tiles="cartodbpositron")

    qmin, qmax = features["risk_index"].quantile([0.05, 0.95])

    def color(val):
        if pd.isna(val):
            return "#cccccc"
        norm = (val - qmin) / (qmax - qmin + 1e-9)
        norm = max(0.0, min(1.0, norm))
        # 위험 높을수록 진한 빨강
        r = int(255 * norm)
        g = int(200 * (1 - norm))
        return f"#{r:02x}{g:02x}40"

    for _, row in features.iterrows():
        is_selected = selected_sgg and row["sgg_name"] == selected_sgg
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=12 if is_selected else 5,
            color="#000000" if is_selected else color(row["risk_index"]),
            weight=2 if is_selected else 1,
            fill=True,
            fill_color=color(row["risk_index"]),
            fill_opacity=0.7,
            tooltip=(
                f"<b>{row['sgg_name']}</b><br>"
                f"위험지수: {row['risk_index']:.3f}<br>"
                f"사고: {int(row['accident_count'])}건<br>"
                f"평균 응급도착: {row['ems_response_min']:.1f}분"
            ),
        ).add_to(m)

    return m
