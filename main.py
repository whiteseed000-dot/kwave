import streamlit as st
import plotly.graph_objects as go

from data import load_twii_monthly
from kwave import detect_k_wave_phase, k_wave_score
from resonance import calc_total_resonance


# =========================
# Streamlit 設定
# =========================
st.set_page_config(
    page_title="台股康波 × 共振模型（Kondratieff Wave）",
    layout="wide"
)

st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")


# =========================
# 讀取台股（月資料）
# =========================
with st.spinner("載入台股資料中..."):
    twii = load_twii_monthly()

st.success(f"資料期間：{twii.index.min().date()} ~ {twii.index.max().date()}")


# =========================
# 康波分析
# =========================
k_phase, k_method = detect_k_wave_phase(twii["Close"])
k_score = k_wave_score(k_phase)


# =========================
# 顯示康波狀態
# =========================
st.subheader("🌍 宏觀康波狀態")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("目前康波階段", k_phase)

with col2:
    st.metric("康波分數", k_score)

with col3:
    st.metric("計算方式", k_method)


# =========================
# （示範）你的原本共振分數
# 👉 實務上請換成你真實的共振計算
# =========================
st.subheader("🎯 共振分數整合（示範）")

base_resonance_score = st.number_input(
    "原始共振分數（示範用）",
    value=2.5,
    step=0.1
)

K_WEIGHT = st.slider(
    "康波權重",
    min_value=0.0,
    max_value=0.5,
    value=0.25,
    step=0.05
)

final_score = calc_total_resonance(
    base_resonance_score,
    k_score,
    weight=K_WEIGHT
)

st.write(f"🔹 原始共振分數：**{base_resonance_score}**")
st.write(f"🔹 最終共振分數（含康波）：**{final_score:.2f}**")


# =========================
# 視覺化：台股月線
# =========================
st.subheader("📊 台股加權指數（月線）")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=twii.index,
        y=twii["Close"],
        name="TAIEX（月線）",
        line=dict(width=2)
    )
)

fig.update_layout(
    height=500,
    xaxis_title="Date",
    yaxis_title="Index",
    template="plotly_dark",
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)


# =========================
# 決策提示（實戰用）
# =========================
st.subheader("🧠 康波決策提示")

if k_phase == "Winter":
    st.error(
        "❄️ 康波 Winter：\n"
        "• 建議降低交易頻率\n"
        "• 嚴格風控\n"
        "• 避免追高策略"
    )
elif k_phase == "Spring":
    st.success(
        "🌱 康波 Spring：\n"
        "• 結構性復甦階段\n"
        "• 適合中長期佈局\n"
        "• 共振策略成功率提升"
    )
elif k_phase == "Summer":
    st.warning(
        "🔥 康波 Summer：\n"
        "• 趨勢仍在，但需留意過熱\n"
        "• 停利與風控重要"
    )
else:  # Autumn
    st.warning(
        "🍂 康波 Autumn：\n"
        "• 泡沫化風險上升\n"
        "• 避免追逐高估值"
    )


# =========================
# Footer
# =========================
st.caption(
    "⚠️ 本模型為長週期結構分析工具（非短線預測）。"
)
