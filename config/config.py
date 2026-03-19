import pandas as pd
START_DATE = "1993-01-01"
END_DATE = "2025-12-31"
TRADING_DAYS = 252
REALISED_VOLATILITY_WINDOW = 20
MVT_WINDOW = 252
MOMENTUM_WINDOW = 60
TICKERS = pd.read_csv("data/raw/universe.csv", header=None, usecols=[0])[0].to_list()