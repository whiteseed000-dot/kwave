import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =============================
# Streamlit 設定
# =============================
st.set_page_config(
    page_title="台股康波 × 共振模型（Kondratieff Wave）",
    layout="wide"
)

st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# =============================
# 參數
# =============================
START_DATE = "1985-01-01"
TICKER = "^TWII"
THEORETICAL_K_WAVE_YEARS = 50

# =============================
# 載入資料
# =============================
@st.cache_data
def load_data():
    df = yf.download(
        TICKER,
        start=START_DATE,
        auto_adjust=True,
        progress=False
    )
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df

df = load_data()

if df.empty:
    st.error("❌ 無法取得台股資料")
    st.stop()

# =============================
# 月線
# =============================
monthly_close = (
    df["Close"]
    .resample("M")
    .last()
    .dropna()
)

n_months = len(monthly_close)
st.caption(f"📊 月線資料筆數：{n_months}")

# =============================
# 🔑 動態康波視窗（關鍵修正）
# =============================
theoretical_window = THEORETICAL_K_WAVE_YEARS * 12
adaptive_window = int(min(theoretical_window, n_months * 0.7))

st.caption(f"🧮 實際康波 window（月）：{adaptive_window}")

# =============================
# 康波計算
# =============================
def calc_k_wave(series: pd.Series, window: int):
    log_price = np.log(series)

    trend = log_price.rolling(
        window=window,
        min_periods=window // 2
    ).mean()

    slope = trend.diff()
    curve = slope.diff()

    return trend, slope, curve

k_trend, k_slope, k_curve = calc_k_wave(monthly_close, adaptive_window)

# =============================
# 取最新有效值
# =============================
latest_slope = float(k_slope.dropna().iloc[-1])
latest_curve = float(k_curve.dropna().iloc[-1])

# =============================
# 康波階段判定
# =============================
def detect_phase(slope: float, curve: float) -> str:
    if slope > 0 and curve > 0:
        return "Spring 🌱"
    elif slope > 0 and curve < 0:
        return "Summer 🔥"
    elif slope < 0 and curve < 0:
        return "Autumn 🍂"
    else:
        return "Winter ❄️"

k_phase = detect_phase(latest_slope, latest_curve)

# =============================
# 繪圖（現在一定會有線）
# =============================
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=monthly_close.index,
        y=monthly_close.values,
        mode="lines",
        name="TAIEX（月線）",
        line=dict(width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=k_trend.index,
        y=np.exp(k_trend),
        mode="lines",
        name="康波趨勢（K-Wave）",
        line=dict(width=3, dash="dash")
    )
)

fig.update_layout(
    height=550,
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Index",
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# 康波決策提示
# =============================
st.subheader("🧠 康波決策提示")

if "Spring" in k_phase:
    st.success("🌱 康波 Spring：長期佈局期，回檔分批")
elif "Summer" in k_phase:
    st.warning("🔥 康波 Summer：趨勢仍在，但需控風險")
elif "Autumn" in k_phase:
    st.info("🍂 康波 Autumn：高檔震盪，降低曝險")
else:
    st.error("❄️ 康波 Winter：防禦為主，現金重要")

st.markdown(f"""
**目前康波狀態： `{k_phase}`**

- 理論康波年期： `{THEORETICAL_K_WAVE_YEARS} 年`
- 實際使用 window： `{adaptive_window} 月`
- 最新趨勢斜率： `{latest_slope:.6f}`
- 最新曲率： `{latest_curve:.6f}`
""")

st.caption("⚠️ 本工具為長週期趨勢分析，非投資建議")
