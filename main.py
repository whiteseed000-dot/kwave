import streamlit as st
import plotly.graph_objects as go

from data import load_twii_monthly
from kwave import detect_k_wave_phase, k_wave_score

twii = load_twii_monthly()

k_phase, k_method = detect_k_wave_phase(twii['Close'])
k_score = k_wave_score(k_phase)

st.metric("目前康波階段", k_phase)
st.caption(f"康波計算方式：{k_method}")



st.set_page_config(layout="wide")
st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")



st.subheader("🌍 宏觀康波狀態")
st.metric("目前康波階段", k_phase)
st.metric("康波分數", k_score)

# =========================
# 模擬你的「原本共振分數」
# （實際上請換成你自己的）
# =========================
base_resonance_score = 2.5  # 👈 假設值

final_score = calc_total_resonance(
    base_resonance_score,
    k_score,
    weight=0.25
)

st.subheader("🎯 共振分數整合結果")
st.write(f"原始共振分數：{base_resonance_score}")
st.write(f"最終共振分數（含康波）：{final_score:.2f}")

# =========================
# 視覺化
# =========================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=twii.index,
    y=twii['Close'],
    name="TAIEX",
    line=dict(color="white")
))

fig.update_layout(
    template="plotly_dark",
    height=500,
    title="TAIEX Index"
)

st.plotly_chart(fig, use_container_width=True)
