import pandas as pd
from src.data.download import download_data
from config.config import TICKERS

def get_prices(raw_data=None):
    if raw_data is None:
        raw_data = download_data()

    if isinstance(raw_data.columns, pd.MultiIndex):
        df = raw_data['Close'].copy()
    else:
        df = raw_data[['Close']].copy()

    if isinstance(df, pd.Series):
        df = df.to_frame(name=TICKERS[0] if isinstance(TICKERS, list) else str(TICKERS))

    df.index = pd.to_datetime(df.index)

    df = df.dropna(how="all")
    df = df.ffill(limit=5)
    df = df.dropna()

    df.to_csv("data/processed/prices.csv")
    return df

if __name__ == "__main__":
    get_prices()