import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

# =========================
# Band-pass filter (40–60 年)
# =========================
def bandpass_filter_monthly(series, low_year=60, high_year=40, order=2):
    series = np.asarray(series).reshape(-1)  # ✅ 強制 1D

    low = 1 / (low_year * 12)
    high = 1 / (high_year * 12)

    b, a = butter(order, [low, high], btype="bandpass")

    padlen = 3 * max(len(a), len(b))
    if len(series) <= padlen:
        raise ValueError("資料長度不足，無法使用 band-pass")

    return filtfilt(b, a, series)


# =========================
# Fallback：長週期近似（穩定版）
# =========================
def long_cycle_fallback(series, window_year=50):
    series = np.asarray(series).reshape(-1)  # ✅ 關鍵修正

    window = window_year * 12
    trend = (
        pd.Series(series)
        .rolling(window=window, min_periods=1)
        .mean()
        .values
    )

    cycle = series - trend
    return cycle


# =========================
# 康波相位判定（主入口）
# =========================
def detect_k_wave_phase(close_series):
    # 保證一維
    log_price = np.log(np.asarray(close_series).reshape(-1))

    # ① 先嘗試 band-pass
    try:
        cycle = bandpass_filter_monthly(log_price)
        method = "band-pass"
    except Exception:
        # ② 自動 fallback（實務穩定解）
        cycle = long_cycle_fallback(log_price)
        method = "fallback"

    slope = np.gradient(cycle)
    curve = np.gradient(slope)

    s = slope[-1]
    c = curve[-1]

    if s > 0 and c > 0:
        phase = "Spring"
    elif s > 0 and c < 0:
        phase = "Summer"
    elif s < 0 and c < 0:
        phase = "Autumn"
    else:
        phase = "Winter"

    return phase, method


# =========================
# 康波數值化
# =========================
K_WAVE_SCORE = {
    "Spring": 1.0,
    "Summer": 0.5,
    "Autumn": -0.5,
    "Winter": -1.0
}

def k_wave_score(phase):
    return K_WAVE_SCORE.get(phase, 0)
