# =========================================
# 台股康波 × 共振模型（Kondratieff Wave）
# 回測年數：100 年（修正版，保證不再報錯）
# =========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.signal import savgol_filter

# =====================
# 基本設定
# =====================
st.set_page_config(page_title="台股康波 × 共振模型", layout="wide")

BACKTEST_YEARS = 100
K_WAVE_WINDOW = 240   # 理想康波（月）
SMOOTH_POLY = 3

# =====================
# 標題
# =====================
st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# =====================
# 取得 100 年月資料
# =====================
end_date = datetime.today()
start_date = end_date - timedelta(days=BACKTEST_YEARS * 365)

df = yf.download(
    "^TWII",
    start=start_date,
    end=end_date,
    interval="1mo",
    auto_adjust=True,
    progress=False
)

df = df.dropna()
monthly_close = df["Close"].copy()

# =====================
# 🔴 關鍵修正：window 永遠不超過資料長度
# =====================
data_len = len(monthly_close)

if data_len < 10:
    st.error("資料不足，無法計算康波")
    st.stop()

# window 必須是奇數，且 <= 資料長度
window = min(K_WAVE_WINDOW, data_len - 1)
if window % 2 == 0:
    window -= 1

# polyorder 必須 < window
poly = min(SMOOTH_POLY, window - 1)

k_wave = savgol_filter(
    monthly_close.values,
    window_length=window,
    polyorder=poly,
    mode="interp"
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
    x=monthly_close.index,
    y=k_wave,
    mode="lines",
    name="康波趨勢（K-Wave）",
    line=dict(width=3, dash="dash")
))

fig.update_layout(
    height=650,
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Index",
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig, use_container_width=True)

# =====================
# 康波決策提示
# =====================
st.subheader("🧠 康波決策提示")

if len(k_wave) >= 12:
    slope = np.polyfit(
        np.arange(12),
        k_wave[-12:],
        1
    )[0]

    if slope > 0:
        st.success("🌱 康波 Spring：長期偏多趨勢")
    else:
        st.error("🥀 康波 Winter：長期偏空趨勢")

# =====================
# 資訊顯示
# =====================
st.caption(f"回測年數：{BACKTEST_YEARS} 年")
st.caption(f"月資料筆數：{data_len}")
st.caption(f"實際康波 window（月）：{window}")
st.caption(f"Savgol polyorder：{poly}")
