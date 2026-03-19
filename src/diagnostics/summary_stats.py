import numpy as np
import pandas as pd
from scipy import stats
from src.data.prices import get_prices

def build_summary_stats(prices: pd.DataFrame | None = None) -> pd.DataFrame:
    if prices is None:
        prices = get_prices()

    prices = prices.sort_index().copy()
    log_returns = np.log(prices/prices.shift(1)).dropna()

    summary = pd.DataFrame(index=prices.columns)

    summary["Start_Date"] = prices.apply(lambda s: s.dropna().index.min())
    summary["End_Date"] = prices.apply(lambda s: s.dropna().index.max())
    summary["Observations"] = log_returns.count()

    summary["Mean_Daily_Log_Return"] = log_returns.mean()
    summary["Std_Daily_Log_Return"] = log_returns.std()

    summary["Skewness"] = log_returns.apply(lambda x: stats.skew(x, bias=False))
    summary["Kurtosis"] = log_returns.apply(lambda x: stats.kurtosis(x, fisher=False, bias=False))

    summary["Annualised_Volatility"] = summary["Std_Daily_Log_Return"] * np.sqrt(252)
    summary["Annualised_Return"] = np.exp(summary["Mean_Daily_Log_Return"] * 252) - 1

    summary = summary.sort_index()
    summary.to_csv("outputs/tables/Data_Summary_Stats.csv")

    return summary

if __name__ == "__main__":
    print(build_summary_stats().head())



