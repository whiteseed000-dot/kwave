import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# =============================
# Streamlit 基本設定
# =============================
st.set_page_config(
    page_title="台股康波 × 共振模型（Kondratieff Wave）",
    layout="wide"
)

st.title("📈 台股康波 × 共振模型（Kondratieff Wave）")

# =============================
# 參數設定
# =============================
START_DATE = "1985-01-01"
TICKER = "^TWII"

# 康波參數（年）
K_WAVE_YEARS = 50
MONTHS = K_WAVE_YEARS * 12

# =============================
# 下載台股資料（非常關鍵）
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
# 轉為月線（關鍵步驟）
# =============================
monthly_close = (
    df["Close"]
    .resample("M")
    .last()
    .dropna()
)

st.caption(f"📊 月線資料筆數：{len(monthly_close)}")

# =============================
# 康波計算（穩定版，不用 scipy）
# =============================
def calc_kondratieff(series: pd.Series, window: int):
    """
    使用 long-term moving average + 曲率判斷
    """
    log_price = np.log(series)

    # 長期趨勢（康波）
    long_trend = log_price.rolling(
        window=window,
        min_periods=window // 2
    ).mean()

    # 一階導數（趨勢方向）
    slope = long_trend.diff()

    # 二階導數（加速度 / 曲率）
    curvature = slope.diff()

    return long_trend, slope, curvature

k_trend, k_slope, k_curve = calc_kondratieff(monthly_close, MONTHS)

# =============================
# 康波相位判定
# =============================
def detect_phase(slope, curve):
    if slope > 0 and curve > 0:
        return "Spring 🌱"
    elif slope > 0 and curve < 0:
        return "Summer 🔥"
    elif slope < 0 and curve < 0:
        return "Autumn 🍂"
    else:
        return "Winter ❄️"

latest_slope = k_slope.dropna().iloc[-1]
latest_curve = k_curve.dropna().iloc[-1]
k_phase = detect_phase(latest_slope, latest_curve)

# =============================
# Plotly 繪圖
# =============================
fig = go.Figure()

# 台股月線
fig.add_trace(
    go.Scatter(
        x=monthly_close.index,
        y=monthly_close.values,
        mode="lines",
        name="TAIEX（月線）",
        line=dict(width=2)
    )
)

# 康波趨勢（指數化還原）
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
    legend=dict(x=0.01, y=0.99),
    xaxis_title="Date",
    yaxis_title="Index"
)

st.plotly_chart(fig, use_container_width=True)

# =============================
# 康波決策提示
# =============================
st.subheader("🧠 康波決策提示")

if "Spring" in k_phase:
    st.success("🌱 康波 Spring：長期佈局期，逢回可分批布局")
elif "Summer" in k_phase:
    st.warning("🔥 康波 Summer：趨勢仍在，但留意過熱與風控")
elif "Autumn" in k_phase:
    st.info("🍂 康波 Autumn：高檔震盪，適合逐步降低曝險")
else:
    st.error("❄️ 康波 Winter：系統性風險期，現金與防禦優先")

st.markdown(f"""
**目前康波狀態： `{k_phase}`**

- 康波年期： `{K_WAVE_YEARS} 年`
- 最新趨勢斜率： `{latest_slope:.5f}`
- 最新曲率： `{latest_curve:.5f}`
""")

st.caption("⚠️ 本模型為長週期趨勢分析，非短線買賣建議")
