import yfinance as yf

def load_twii_monthly():
    df = yf.download("^TWII", start="1965-01-01", progress=False)
    df = df[['Close']].dropna()
    df = df.resample("M").last()
    return df
