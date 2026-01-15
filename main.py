# =========================================
# 台股康波 × 共振模型（Kondratieff Wave）
# 回測年數：100 年
# ❗ 終極防呆版（不可能再出 savgol 錯）
# =========================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.signal import savgol_filter

# =====================
# Streamlit 設定
# =====================
st.set_page_config(page_title="台股康波 × 共振模型", layout="wide")
st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# =====================
# 參數
# =====================
BACKTEST_YEARS = 100
K_WAVE_WINDOW = 240
SMOOTH_POLY = 3

# =====================
# 下載資料（100 年）
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

if "Close" not in df or len(df) < 12:
    st.error("資料不足，無法計算")
    st.stop()

monthly_close = df["Close"].astype(float)
data_len = len(monthly_close)

# =====================
# 🧨 終極防呆 Savitzky–Golay
# =====================
# 規則：
# 1. window < data_len
# 2. window 為奇數
# 3. window >= 3
# 4. poly < window
# 5. 不合法 → 改用 rolling mean

use_savgol = True

window = min(K_WAVE_WINDOW, data_len - 1)

if window < 3:
    use_savgol = False

if window % 2 == 0:
    window -= 1

poly = min(SMOOTH_POLY, window - 1)

if poly < 1 or window <= poly:
    use_savgol = False

if use_savgol:
    try:
        k_wave = savgol_filter(
            monthly_close.values,
            window_length=window,
            polyorder=poly,
            mode="interp"
        )
    except Exception:
        use_savgol = False

# =====================
# 備援方案（永遠不會錯）
# =====================
if not use_savgol:
    k_wave = (
        monthly_close
        .rolling(window=max(6, data_len // 10), min_periods=1)
        .mean()
        .values
    )

# =====================
# 繪圖
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
# 康波判斷
# =====================
st.subheader("🧠 康波決策提示")

if len(k_wave) >= 12:
    slope = np.polyfit(
        np.arange(12),
        k_wave[-12:],
        1
    )[0]

    if slope > 0:
        st.success("🌱 康波 Spring：長期上升週期")
    else:
        st.error("🥀 康波 Winter：長期下降週期")

# =====================
# 狀態資訊
# =====================
st.caption(f"回測年數：{BACKTEST_YEARS} 年")
st.caption(f"月資料筆數：{data_len}")
st.caption(f"實際 window：{window if use_savgol else 'Rolling Mean'}")
st.caption(f"polyorder：{poly if use_savgol else 'N/A'}")
