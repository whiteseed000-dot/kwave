import numpy as np
from scipy.signal import butter, filtfilt

# =========================
# Band-pass filter (40–60 年)
# 使用「月資料」
# =========================
def bandpass_filter_monthly(series, low_year=60, high_year=40, order=2):
    """
    series : log price (monthly)
    """
    # 月資料 → 1 年 = 12
    low = 1 / (low_year * 12)
    high = 1 / (high_year * 12)

    b, a = butter(order, [low, high], btype='bandpass')

    # 🚨 關鍵防炸：資料長度檢查
    padlen = 3 * max(len(a), len(b))
    if len(series) <= padlen:
        raise ValueError(f"資料長度不足做康波濾波（需要 > {padlen} 筆）")

    return filtfilt(b, a, series)

# =========================
# 康波相位判定
# =========================
def detect_k_wave_phase(close_series):
    """
    close_series: pandas Series (monthly close)
    """
    log_price = np.log(close_series.values)

    cycle = bandpass_filter_monthly(log_price)

    slope = np.gradient(cycle)
    curve = np.gradient(slope)

    s = slope[-1]
    c = curve[-1]

    if s > 0 and c > 0:
        return "Spring"
    elif s > 0 and c < 0:
        return "Summer"
    elif s < 0 and c < 0:
        return "Autumn"
    else:
        return "Winter"


K_WAVE_SCORE = {
    "Spring": 1.0,
    "Summer": 0.5,
    "Autumn": -0.5,
    "Winter": -1.0
}

def k_wave_score(phase):
    return K_WAVE_SCORE.get(phase, 0)
