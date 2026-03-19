import numpy as np
import pandas as pd
from src.data.prices import get_prices
from config.config import REALISED_VOLATILITY_WINDOW, MVT_WINDOW, MOMENTUM_WINDOW

def build_features(prices: pd.DataFrame | None = None) -> pd.DataFrame:
    if prices is None:
        prices = get_prices()
    
    prices = prices.sort_index().copy()

    returns = prices.pct_change()
    log_returns = np.log(prices / prices.shift(1))

    realised_vol = log_returns.rolling(window=REALISED_VOLATILITY_WINDOW).std().shift(1)
    mvt = realised_vol.rolling(window=MVT_WINDOW).median().shift(1)
    log_momentum = log_returns.rolling(window=MOMENTUM_WINDOW).sum().shift(1)
    momentum = np.exp(log_momentum) - 1
    momentum_signal = np.sign(momentum).replace(0, np.nan).ffill().fillna(0)

    valid_mask = realised_vol.notna() & mvt.notna() & log_momentum.notna()

    returns = returns.where(valid_mask)
    log_returns = log_returns.where(valid_mask)
    realised_vol = realised_vol.where(valid_mask)
    mvt = mvt.where(valid_mask)
    log_momentum = log_momentum.where(valid_mask)
    momentum = momentum.where(valid_mask)
    momentum_signal = momentum_signal.where(valid_mask)


    vol_regime = pd.DataFrame(
        np.where(realised_vol < mvt, "Low", "High"),
        index=prices.index,
        columns=prices.columns
    ).where(valid_mask)

    feature_map = {
        "Close": prices,
        "Return": returns,
        "Log_Return": log_returns,
        f"RV_{REALISED_VOLATILITY_WINDOW}": realised_vol,
        f"MVT_{MVT_WINDOW}": mvt,
        f"Log_Momentum_{MOMENTUM_WINDOW}": log_momentum,
        f"Momentum_{MOMENTUM_WINDOW}": momentum,
        "Momentum_Signal": momentum_signal,
        "Vol_Regime": vol_regime
    }

    panel = pd.concat(feature_map, axis=1)
    panel = panel.swaplevel(0, 1, axis=1).sort_index(axis=1)
    panel = panel.dropna()
    panel.to_csv("data/processed/full_features.csv")
    return panel

if __name__ == "__main__":
    print(build_features().head())
