# =========================================
# 台股康波 × 共振模型（Kondratieff Wave）
# 回測年數：100 年（固定）
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
K_WAVE_WINDOW = 240   # 康波平滑（月）
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
# 康波計算（長週期趨勢）
# =====================
if len(monthly_close) >= K_WAVE_WINDOW:
    k_wave = savgol_filter(
        monthly_close.values,
        window_length=K_WAVE_WINDOW if K_WAVE_WINDOW % 2 == 1 else K_WAVE_WINDOW + 1,
        polyorder=SMOOTH_POLY
    )
else:
    k_wave = np.full(len(monthly_close), np.nan)

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
    height=600,
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

if len(k_wave) > 0 and not np.isnan(k_wave[-1]):
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
st.caption(f"月資料筆數：{len(monthly_close)}")
st.caption(f"康波 window（月）：{K_WAVE_WINDOW}")
