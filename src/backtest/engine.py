import numpy as np
import pandas as pd
import os
from scipy import stats

from src.data.build_features import build_features


def build_strategy_weights(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Build lagged strategy weights for every asset.

    Output columns:
        level 0 -> asset
        level 1 -> strategy
    """
    if panel is None:
        panel = build_features()

    signal = panel.xs("Momentum_Signal", axis=1, level=1)
    regime = panel.xs("Vol_Regime", axis=1, level=1)

    w_bh = pd.DataFrame(1.0, index=signal.index, columns=signal.columns)
    w_tsmom = signal.copy()
    w_vc_flat = signal.where(regime == "Low", 0.0)
    w_vc_contrarian = signal.where(regime == "Low", -signal)

    weights = {
        "BH": w_bh,
        "TSMOM": w_tsmom,
        "VC_FLAT": w_vc_flat,
        "VC_CONTRARIAN": w_vc_contrarian,
    }

    out = pd.concat(weights, axis=1)
    out = out.swaplevel(0, 1, axis=1).sort_index(axis=1)

    # Lag to avoid look-ahead bias
    out = out.shift(1)

    return out


def apply_costs(strategy_w: pd.Series, gross_ret: pd.Series, round_trip_cost: float) -> pd.Series:
    """
    Cost_t = (round_trip_cost / 2) * |Δw_t|
    """
    dw = strategy_w.diff().abs().fillna(0.0)
    cost = (round_trip_cost / 2.0) * dw
    return gross_ret - cost


def build_asset_strategy_returns(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None) -> pd.DataFrame:
    """
    Build net strategy returns for every asset.

    Output columns:
        level 0 -> asset
        level 1 -> strategy
        level 2 -> round-trip cost
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    asset_returns = panel.xs("Return", axis=1, level=1)
    weights = build_strategy_weights(panel)

    results = {}

    assets = asset_returns.columns
    strategies = weights.columns.get_level_values(1).unique()

    for asset in assets:
        for strategy in strategies:
            w = weights[(asset, strategy)]
            gross = w * asset_returns[asset]

            for rt in bps_list:
                net = apply_costs(w, gross, rt)
                results[(asset, strategy, rt)] = net

    out = pd.DataFrame(results)
    out.columns = pd.MultiIndex.from_tuples(out.columns, names=["Asset", "Strategy", "RoundTripCost"])

    return out


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return dd.min()


def sharpe(daily_ret: pd.Series) -> float:
    mu = daily_ret.mean()
    sd = daily_ret.std(ddof=1)
    if sd == 0 or np.isnan(sd):
        return np.nan
    return (mu / sd) * np.sqrt(252)


def sortino(daily_ret: pd.Series) -> float:
    mu = daily_ret.mean()
    downside = daily_ret[daily_ret < 0].std(ddof=1)
    if downside == 0 or np.isnan(downside):
        return np.nan
    return (mu / downside) * np.sqrt(252)


def summarise(daily_ret: pd.Series) -> pd.Series:
    daily_ret = daily_ret.dropna()

    if len(daily_ret) == 0:
        return pd.Series(
            {
                "Annualised Return": np.nan,
                "Annualised Volatility": np.nan,
                "Sharpe": np.nan,
                "Sortino": np.nan,
                "Skew": np.nan,
                "Max Drawdown": np.nan,
            }
        )

    ann_ret = (1.0 + daily_ret).prod() ** (252 / len(daily_ret)) - 1.0
    ann_vol = daily_ret.std(ddof=1) * np.sqrt(252)
    eq = (1.0 + daily_ret).cumprod()

    return pd.Series(
        {
            "Annualised Return": ann_ret,
            "Annualised Volatility": ann_vol,
            "Sharpe": sharpe(daily_ret),
            "Sortino": sortino(daily_ret),
            "Skew": stats.skew(daily_ret, nan_policy="omit"),
            "Max Drawdown": max_drawdown(eq),
        }
    )


def build_asset_performance_summary(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None) -> pd.DataFrame:
    """
    Performance summary for every asset, strategy, and cost level.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    ret_df = build_asset_strategy_returns(panel=panel, bps_list=bps_list)
    weights = build_strategy_weights(panel)

    rows = []

    for (asset, strategy, rt) in ret_df.columns:
        s = summarise(ret_df[(asset, strategy, rt)])
        s.name = (asset, strategy, rt)
        rows.append(s)

    summary = pd.DataFrame(rows)
    summary.index = pd.MultiIndex.from_tuples(
        summary.index,
        names=["Asset", "Strategy", "RoundTripCost"],
    )

    for (asset, strategy, rt) in summary.index:
        w = weights[(asset, strategy)]
        summary.loc[(asset, strategy, rt), "Avg |Δw|"] = w.diff().abs().mean()

    summary = summary.sort_index()
    os.makedirs("outputs/tables", exist_ok=True)
    summary.to_csv("outputs/tables/asset_performance_summary.csv")

    return summary


if __name__ == "__main__":
    build_asset_performance_summary()