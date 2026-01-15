# app.py  ——【最終穩定版・可直接用・一定出線】

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="台股康波 × 共振模型", layout="wide")
st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# ========= 參數 =========
TICKER = "^TWII"
WINDOW_MONTHS = 1200

# ========= 下載資料 =========
@st.cache_data
def load_data():
    df = yf.download(
        TICKER,
        start="1980-01-01",
        progress=False,
        auto_adjust=True
    )
    return df

df = load_data()

# ========= 強制取 Close（避免 MultiIndex 問題） =========
if isinstance(df.columns, pd.MultiIndex):
    close = df["Close"].iloc[:, 0]
else:
    close = df["Close"]

close = close.dropna()

# ========= 月線 =========
monthly_close = close.resample("M").last().dropna()

# ========= 防呆（絕對不會再炸） =========
if int(monthly_close.shape[0]) < 50:
    st.error("❌ 月線資料不足")
    st.stop()

# ========= 康波（穩定算法） =========
log_price = np.log(monthly_close.values)
k_wave = (
    pd.Series(log_price, index=monthly_close.index)
    .rolling(WINDOW_MONTHS, min_periods=24)
    .mean()
)
k_wave = np.exp(k_wave)

# ========= 畫圖 =========
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=monthly_close.index,
    y=monthly_close.values,
    name="TAIEX（月線）",
    mode="lines",
    line=dict(width=2)
))

fig.add_trace(go.Scatter(
    x=k_wave.index,
    y=k_wave.values,
    name="康波趨勢（K-Wave）",
    mode="lines",
    line=dict(width=3, dash="dash")
))

fig.update_layout(
    template="plotly_dark",
    height=600,
    xaxis_title="Date",
    yaxis_title="Index",
    legend=dict(x=0.02, y=0.98)
)

st.plotly_chart(fig, use_container_width=True)

# ========= 決策提示 =========
latest_price = monthly_close.iloc[-1]
latest_k = k_wave.dropna().iloc[-1]

st.subheader("🧠 康波決策提示")

if latest_price > latest_k:
    st.success("🌱 Spring：長期偏多，回檔分批")
else:
    st.error("❄️ Winter：長期偏空，風險控管")

st.caption(f"📊 月線筆數：{len(monthly_close)}")
st.caption(f"📈 康波 window（月）：{WINDOW_MONTHS}")
