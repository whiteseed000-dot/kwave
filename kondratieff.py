import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


def preprocess(df):
df = df[['Close']].dropna()
df['log_price'] = np.log(df['Close'])
return df

def bandpass_filter(series, low=1/60, high=1/40):
b, a = butter(
N=2,
Wn=[low, high],
btype='bandpass'
)
return filtfilt(b, a, series)

def detect_phase(cycle):
slope = np.gradient(cycle)
curve = np.gradient(slope)


phase = []
for s, c in zip(slope, curve):
if s > 0 and c > 0:
phase.append('Spring') # 復甦
elif s > 0 and c < 0:
phase.append('Summer') # 繁榮
elif s < 0 and c < 0:
phase.append('Autumn') # 泡沫
else:
phase.append('Winter') # 衰退
return phase
