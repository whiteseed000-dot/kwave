import yfinance as yf
import pandas as pd

def load_twii():
    df = yf.download("^TWII", start="1965-01-01", progress=False)
    df = df[['Close']].dropna()
    df.index = pd.to_datetime(df.index)
    return df
