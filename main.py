import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="台股康波 × 共振模型",
    layout="wide"
)

st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

TICKER = "^TWII"
START_DATE = "1985-01-01"
THEORETICAL_K_WAVE_YEARS = 50

# =============================
# 下載資料
# =============================
@st.cache_data
def load_data():
    df = yf.download(
        TICKER,
        start=START_DATE,
        auto_adjust=False,
        progress=False
    )
    df.index = pd.to_datetime(df.index)
    return df.sort_index()

df = load_data()

if df.empty:
    st.error("❌ 無法下載台股資料")
    st.stop()

# =============================
# 價格欄位安全選擇（修正版）
# =============================
price = None

if "Close" in df.columns and df["Close"].dropna().shape[0] > 0:
    price = df["Close"]
elif "Adj Close" in df.columns and df["Adj Close"].dropna().shape[0] > 0:
    price = df["Adj Close"]
else:
    st.error("❌ 找不到有效價格欄位（Close / Adj Close）")
    st.stop()

# =============================
# 月線
# =============================
monthly_close = (
    price
    .dropna()
    .resample("M")
    .last()
)

st.caption(f"📊 月線資料筆數：{len(monthly_close)}")

# =============================
# 康波 window
# =============================
theoretical_window = THEORETICAL_K_WAVE_YEARS * 12
adaptive_window = int(min(theoretical_window, len(monthly_close) * 0.7))

st.caption(f"🧮 康波 window（月）：{adaptive_window}")

# =============================
# 康波計算
# =============================
log_price = np.log(monthly_close)

k_trend = log_price.rolling(
    window=adaptive_window,
    min_periods=adaptive_window // 2
).mean()

k_slope = k_trend.diff()
k_curve = k_slope.diff()

# =============================
# 康波階段
# =============================
latest_slope = float(k_slope.dropna().iloc[-1])
latest_curve = float(k_curve.dropna().iloc[-1])

def detect_phase(slope, curve):
    if slope > 0 and curve > 0:
        return "Spring 🌱"
    elif slope > 0 and curve < 0:
        return "Summer 🔥"
    elif slope < 0 and curve < 0:
        return "Autumn 🍂"
    else:
        return "Winter ❄️"

phase = detect_phase(latest_slope, latest_curve)

# =============================
# Plotly
# =============================
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=monthly_close.index,
    y=monthly_close.values,
    mode="lines",
    name="TAIEX（月線）"
))

fig.add_trace(go.Scatter(
    x=k_trend.index,
    y=np.exp(k_trend),
    mode="lines",
    name="康波趨勢（K-Wave）",
    line=dict(dash="dash", width=3)
))

fig.update_layout(
    template="plotly_dark",
    height=550,
    xaxis_title="Date",
    yaxis_title="Index"
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# 決策提示
# =============================
st.subheader("🧠 康波決策提示")

if "Spring" in phase:
    st.success("🌱 康波 Spring：長期佈局期")
elif "Summer" in phase:
    st.warning("🔥 康波 Summer：趨勢延續，控風險")
elif "Autumn" in phase:
    st.info("🍂 康波 Autumn：高檔震盪")
else:
    st.error("❄️ 康波 Winter：防禦為主")

st.markdown(f"""
**目前康波狀態： `{phase}`**

- 理論康波年期： `{THEORETICAL_K_WAVE_YEARS} 年`
- 使用 window： `{adaptive_window} 月`
- 最新斜率： `{latest_slope:.6f}`
- 最新曲率： `{latest_curve:.6f}`
""")
