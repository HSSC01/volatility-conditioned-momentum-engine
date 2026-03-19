import pandas as pd
import yfinance as yf
from config.config import START_DATE, END_DATE, TICKERS

def download_data(tickers=None, start=START_DATE, end=END_DATE):
    if tickers is None:
        tickers = TICKERS

    raw_data = yf.download(tickers=tickers, start=start, end=end, multi_level_index=False, auto_adjust=True)
    raw_data.to_csv("data/raw/raw_data.csv")

    return raw_data


if __name__ == "__main__":
    download_data()