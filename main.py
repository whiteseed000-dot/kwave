import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =====================
# Streamlit 設定
# =====================
st.set_page_config(
    page_title="台股康波 × 共振模型",
    layout="wide"
)

st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# =====================
# 參數
# =====================
TICKER = "^TWII"
WINDOW_MONTHS = 240  # 康波 window（月）

# =====================
# 下載資料（日線）
# =====================
@st.cache_data
def load_data():
    df = yf.download(
        TICKER,
        start="1980-01-01",
        auto_adjust=True,
        progress=False
    )
    return df

df = load_data()

if df.empty or "Close" not in df.columns:
    st.error("❌ 無法取得台股資料")
    st.stop()

# =====================
# 月線（關鍵修正版）
# =====================
monthly_close = (
    df["Close"]
    .dropna()
    .resample("M")
    .ffill()
)

# 防呆：一定要有資料
if monthly_close.notna().sum() < 10:
    st.error("❌ 月線資料不足")
    st.stop()

# =====================
# 康波趨勢（超穩定版）
# =====================
log_price = np.log(monthly_close)

k_wave = (
    log_price
    .rolling(WINDOW_MONTHS, min_periods=30)
    .mean()
    .pipe(np.exp)
)

# =====================
# Plotly 繪圖
# =====================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=monthly_close.index,
    y=monthly_close.values,
    mode="lines",
    name="TAIEX（月線）",
    line=dict(width=2)
))

fig.add_trace(go.Scatter(
    x=k_wave.index,
    y=k_wave.values,
    mode="lines",
    name="康波趨勢（K-Wave）",
    line=dict(width=3, dash="dash")
))

fig.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_title="Date",
    yaxis_title="Index",
    legend=dict(x=0.8, y=0.95)
)

st.plotly_chart(fig, use_container_width=True)

# =====================
# 狀態提示（保底）
# =====================
latest_k = k_wave.dropna().iloc[-1]
latest_p = monthly_close.iloc[-1]

if latest_p > latest_k:
    phase = "🌱 Spring（長期偏多）"
else:
    phase = "❄️ Winter（長期偏空）"

st.subheader("🧠 康波決策提示")
st.success(phase)

st.caption(f"📊 月線資料筆數：{len(monthly_close)}")
st.caption(f"📈 康波 window（月）：{WINDOW_MONTHS}")
