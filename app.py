import streamlit as st
import pandas as pd

from src.config import GRID_FEATURES_PATH
from src.ui import citizen, policy, about

st.set_page_config(page_title="BlindZone — 보이지 않던 위험지대", layout="wide")


@st.cache_data
def load_features():
    return pd.read_parquet(GRID_FEATURES_PATH)


features = load_features()

st.sidebar.title("BlindZone")
mode = st.sidebar.radio(
    "모드",
    ["시민 모드", "정책 시뮬레이터", "About"],
    label_visibility="collapsed",
)

if mode == "시민 모드":
    citizen.render(features)
elif mode == "정책 시뮬레이터":
    policy.render(features)
else:
    about.render()
