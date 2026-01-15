import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt


def preprocess(df):
df = df[['Close']].dropna()
df['log_price'] = np.log(df['Close'])
return df
