import numpy as np
from scipy.signal import butter, filtfilt

# =========================
# Band-pass filter (40–60Y)
# =========================
def bandpass_filter(series, low=1/60, high=1/40, order=2):
    b, a = butter(order, [low, high], btype='bandpass')
    return filtfilt(b, a, series)

# =========================
# 康波相位判定
# =========================
def detect_k_wave_phase(close_series):
    log_price = np.log(close_series.values)
    cycle = bandpass_filter(log_price)

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
