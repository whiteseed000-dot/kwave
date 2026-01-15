import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

# =========================
# 嘗試 Band-pass（40–60 年）
# =========================
def bandpass_filter_monthly(series, low_year=60, high_year=40, order=2):
    low = 1 / (low_year * 12)
    high = 1 / (high_year * 12)

    b, a = butter(order, [low, high], btype="bandpass")

    # filtfilt 最小需求長度
    padlen = 3 * max(len(a), len(b))

    if len(series) <= padlen:
        raise ValueError("資料長度不足，無法安全使用 band-pass")

    return filtfilt(b, a, series)


# =========================
# 安全的康波近似（Fallback）
# 使用「超長期趨勢去除」
# =========================
def long_cycle_fallback(series, window_year=50):
    """
    用 50 年移動平均當康波近似
    絕對穩、不會炸
    """
    window = window_year * 12
    trend = pd.Series(series).rolling(window, min_periods=1).mean()
    cycle = series - trend.values
    return cycle


# =========================
# 康波相位判定（主入口）
# =========================
def detect_k_wave_phase(close_series):
    log_price = np.log(close_series.values)

    # ① 先嘗試 band-pass
    try:
        cycle = bandpass_filter_monthly(log_price)
        method = "band-pass"
    except Exception:
        # ② 自動降級（這才是實務正解）
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
