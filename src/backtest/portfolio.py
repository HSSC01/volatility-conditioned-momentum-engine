import os

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import statsmodels.api as sm

from matplotlib.ticker import FuncFormatter
from matplotlib import colors
from src.backtest.engine import build_asset_strategy_returns, summarise, max_drawdown
from src.data.build_features import build_features
from src.portfolio.asset_weights import build_asset_weights


def build_portfolio_returns(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None) -> pd.DataFrame:
    """
    Build portfolio-level returns by combining asset-level strategy returns
    with static cross-asset weights.

    Parameters
    ----------
    panel : pd.DataFrame | None
        Multi-asset feature panel with MultiIndex columns (asset, feature).
    bps_list : list[float] | None
        Round-trip transaction cost assumptions expressed in decimal form.
        Defaults to [0.0, 0.0002, 0.0010].

    Returns
    -------
    pd.DataFrame
        Portfolio return series with MultiIndex columns:
        level 0 -> Strategy
        level 1 -> RoundTripCost
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    # Asset-level returns: columns = (Asset, Strategy, RoundTripCost)
    ret_df = build_asset_strategy_returns(panel=panel, bps_list=bps_list)

    # Static cross-asset weights: index = Asset
    weights_df = build_asset_weights(panel=panel)
    asset_weights = weights_df["weight"]

    results: dict[tuple[str, float], pd.Series] = {}

    strategies = ret_df.columns.get_level_values("Strategy").unique()
    costs = ret_df.columns.get_level_values("RoundTripCost").unique()

    for strategy in strategies:
        for rt in costs:
            # Extract matrix with columns = assets and rows = dates
            strat_returns = ret_df.xs(
                (strategy, rt),
                level=("Strategy", "RoundTripCost"),
                axis=1,
            )

            # Align cross-asset weights to the available assets
            w = asset_weights.reindex(strat_returns.columns).fillna(0.0)

            # Weighted portfolio return across assets
            # min_count=1 prevents all-NaN rows from turning into artificial zeros
            port_ret = strat_returns.mul(w, axis=1).sum(axis=1, min_count=1)

            results[(strategy, rt)] = port_ret

    out = pd.DataFrame(results)
    out.columns = pd.MultiIndex.from_tuples(
        out.columns,
        names=["Strategy", "RoundTripCost"],
    )
    out = out.sort_index(axis=1)

    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/portfolio_returns.csv", index=True)

    return out


def build_portfolio_summary(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None) -> pd.DataFrame:
    """
    Compute performance summary at the portfolio level.

    Parameters
    ----------
    panel : pd.DataFrame | None
        Multi-asset feature panel.
    bps_list : list[float] | None
        Round-trip transaction cost assumptions.

    Returns
    -------
    pd.DataFrame
        Portfolio performance summary indexed by (Strategy, RoundTripCost).
    """
    port_ret = build_portfolio_returns(panel=panel, bps_list=bps_list)

    rows = []

    for col in port_ret.columns:
        s = summarise(port_ret[col])
        s.name = col
        rows.append(s)

    summary = pd.DataFrame(rows)
    summary.index = pd.MultiIndex.from_tuples(
        summary.index,
        names=["Strategy", "RoundTripCost"],
    )
    summary = summary.sort_index()

    os.makedirs("outputs/tables", exist_ok=True)
    summary.to_csv("outputs/tables/portfolio_summary.csv")

    return summary


def build_equity_curves(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None, initial_capital: float = 1_000_000) -> dict[float, pd.DataFrame]:
    """
    Build portfolio-level equity curves for each strategy and cost level.

    Parameters
    ----------
    panel : pd.DataFrame | None
        Multi-asset feature panel.
    bps_list : list[float] | None
        Round-trip transaction cost assumptions.
    initial_capital : float
        Starting portfolio capital.

    Returns
    -------
    dict[float, pd.DataFrame]
        Dictionary keyed by round-trip cost, where each value is a DataFrame
        containing the equity curves for all strategies.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    ret_df = build_portfolio_returns(panel=panel, bps_list=bps_list)
    equity_curves: dict[float, pd.DataFrame] = {}

    for c in bps_list:
        eq = pd.DataFrame(
            {
                "BH": (1 + ret_df[("BH", c)]).cumprod() * initial_capital,
                "TSMOM": (1 + ret_df[("TSMOM", c)]).cumprod() * initial_capital,
                "VC_FLAT": (1 + ret_df[("VC_FLAT", c)]).cumprod() * initial_capital,
                "VC_CONTRARIAN": (1 + ret_df[("VC_CONTRARIAN", c)]).cumprod() * initial_capital,
            }
        )
        equity_curves[c] = eq

    return equity_curves


def plot_equity_curves(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None, initial_capital: float = 1_000_000) -> dict[float, pd.DataFrame]:
    """
    Plot and save portfolio-level equity curves for each transaction cost level.

    Parameters
    ----------
    panel : pd.DataFrame | None
        Multi-asset feature panel.
    bps_list : list[float] | None
        Round-trip transaction cost assumptions.
    initial_capital : float
        Starting portfolio capital.

    Returns
    -------
    dict[float, pd.DataFrame]
        Equity curve DataFrames keyed by round-trip cost.
    """
    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    equity_curves = build_equity_curves(
        panel=panel,
        bps_list=bps_list,
        initial_capital=initial_capital,
    )

    os.makedirs("outputs/figures/equity_curves", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)

    for c, eq in equity_curves.items():
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(eq.index, eq["BH"], label="Buy & Hold")
        ax.plot(eq.index, eq["TSMOM"], label="Unconditional TSMOM")
        ax.plot(eq.index, eq["VC_FLAT"], label="Vol-Conditioned (flat)")
        ax.plot(eq.index, eq["VC_CONTRARIAN"], label="Vol-Conditioned (contrarian)")

        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"£{x / 1e6:,.1f}m"))
        ax.set_title(f"Equity Curves (Net, round-trip cost = {c * 1e4:.0f} bps)")
        ax.set_ylabel("Portfolio Value")
        ax.legend(frameon=False)

        plt.tight_layout()
        plt.savefig(f"outputs/figures/equity_curves/equity_curves_{int(c * 1e4)}bps.png", dpi=300)

        final_values = eq.tail(1).T
        final_values.columns = [c]
        if c == bps_list[0]:
            final_table = final_values
        else:
            final_table = final_table.join(final_values, how="outer")

    final_table.columns = [f"{int(c * 1e4)}bps" for c in final_table.columns]
    final_table = final_table.map(lambda x: f"{x:,.2f}")
    
    final_table.to_csv("outputs/tables/final_equity_values.csv")

    return equity_curves

CRISIS_WINDOWS = {
    "GFC (2008-2009)": ("2008-09-01", "2009-06-30"),
    "COVID (2020)": ("2020-02-15", "2020-06-30"),
    "Inflation Bear (2022)": ("2022-01-01", "2022-12-31"),
}

def window_report(daily_ret: pd.Series, start: str, end: str) -> pd.Series:
    x = daily_ret.loc[start:end].dropna()

    if len(x) == 0:
        return pd.Series({"CumRet": np.nan, "MaxDD": np.nan, "Obs": 0})

    eq = (1 + x).cumprod()

    return pd.Series({
        "CumRet": eq.iloc[-1] - 1.0,
        "MaxDD": max_drawdown(eq),
        "Obs": len(x),
    })

def build_crisis_performance(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None) -> pd.DataFrame:
    """
    Compute crisis window performance for portfolio strategies.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    ret_df = build_portfolio_returns(panel=panel, bps_list=bps_list)

    rows = []

    for c in bps_list:
        for window_name, (start, end) in CRISIS_WINDOWS.items():

            row = {}

            for strat in ["BH", "TSMOM", "VC_FLAT", "VC_CONTRARIAN"]:
                stats = window_report(ret_df[(strat, c)], start, end)

                row[(strat, "CumRet")] = stats["CumRet"]
                row[(strat, "MaxDD")] = stats["MaxDD"]
                row[(strat, "Obs")] = stats["Obs"]

            row["Window"] = window_name
            row["Cost_bps"] = int(c * 1e4)

            rows.append(row)

    out = pd.DataFrame(rows)
    out = out.set_index(["Window", "Cost_bps"])

    out.columns = pd.MultiIndex.from_tuples([col for col in out.columns if isinstance(col, tuple)], names=["Strategy", "Metric"])
    out = out.sort_index()

    # Save
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/crisis_performance.csv")

    return out


# === Crisis Heatmap Plotting ===
def _plot_single_crisis_heatmap(table: pd.DataFrame, cost_bps: int, metric: str, save_dir: str) -> None:
    """
    Plot one crisis-window heatmap for a given metric and transaction cost.
    """
    heat = table.xs(cost_bps, level="Cost_bps")
    heat = heat.xs(metric, level="Metric", axis=1)
    heat = heat[["BH", "TSMOM", "VC_FLAT", "VC_CONTRARIAN"]]

    if metric in {"CumRet", "MaxDD"}:
        values = heat.astype(float) * 100.0
        fmt = lambda x: f"{x:.1f}%"
        cmap = "RdYlGn"
        vmax = float(np.nanmax(np.abs(values.to_numpy())))
        vmax = 1.0 if vmax == 0 or np.isnan(vmax) else vmax
        norm = colors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    else:
        values = heat.astype(float)
        fmt = lambda x: f"{x:.0f}"
        cmap = "Blues"
        vmax = float(np.nanmax(values.to_numpy()))
        vmax = 1.0 if vmax == 0 or np.isnan(vmax) else vmax
        norm = colors.Normalize(vmin=0.0, vmax=vmax)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    im = ax.imshow(values.to_numpy(), aspect="auto", cmap=cmap, norm=norm)

    ax.set_xticks(range(len(values.columns)))
    ax.set_xticklabels(values.columns)
    ax.set_yticks(range(len(values.index)))
    ax.set_yticklabels(values.index)
    ax.set_title(f"Crisis Window {metric} Heatmap ({cost_bps} bps)")

    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            val = values.iat[i, j]
            if pd.notna(val):
                ax.text(j, i, fmt(val), ha="center", va="center")

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(metric)

    plt.tight_layout()
    plt.savefig(f"{save_dir}/crisis_heatmap_{metric.lower()}_{cost_bps}bps.png", dpi=300)
    plt.close(fig)


def plot_crisis_heatmaps(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None, save_dir: str = "outputs/figures/crisis_heatmaps",
) -> pd.DataFrame:
    """
    Plot crisis-window heatmaps for cumulative return and max drawdown
    across strategies and cost levels.
    """
    table = build_crisis_performance(panel=panel, bps_list=bps_list)

    os.makedirs(save_dir, exist_ok=True)

    cost_levels = table.index.get_level_values("Cost_bps").unique()

    for cost_bps in cost_levels:
        _plot_single_crisis_heatmap(table=table, cost_bps=cost_bps, metric="CumRet", save_dir=save_dir)
        _plot_single_crisis_heatmap(table=table, cost_bps=cost_bps, metric="MaxDD", save_dir=save_dir)

    return table


# === In-sample vs Out-of-sample Split Table ===
def split_summary(daily_ret: pd.Series, split: str = "2008-01-01") -> pd.DataFrame:
    """
    Split a return series into in-sample and out-of-sample periods and
    compute summary statistics for each segment.
    """
    ins = daily_ret.loc[:split].dropna()
    oos = daily_ret.loc[split:].dropna()

    return pd.DataFrame(
        {
            "In-Sample": summarise(ins),
            "Out-Of-Sample": summarise(oos),
        }
    )


def build_oos_split_table(panel: pd.DataFrame | None = None, bps_list: list[float] | None = None, split: str = "2008-01-01", strategies: list[str] | None = None) -> pd.DataFrame:
    """
    Build in-sample vs out-of-sample performance tables for selected
    portfolio strategies and transaction cost assumptions.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    if strategies is None:
        strategies = ["VC_FLAT", "VC_CONTRARIAN"]

    ret_df = build_portfolio_returns(panel=panel, bps_list=bps_list)

    rows = []

    for strategy in strategies:
        for c in bps_list:
            tmp = split_summary(ret_df[(strategy, c)], split=split).copy()
            tmp = tmp.reset_index().rename(columns={"index": "Metric"})
            tmp["Strategy"] = strategy
            tmp["Cost_bps"] = int(c * 1e4)
            rows.append(tmp)

    oos_table = pd.concat(rows, ignore_index=True)

    oos_table = oos_table.pivot_table(
        index="Metric",
        columns=["Strategy", "Cost_bps"],
        values=["In-Sample", "Out-Of-Sample"],
        aggfunc="first",
    )

    oos_table = oos_table.sort_index(axis=1)

    os.makedirs("outputs/tables", exist_ok=True)
    oos_table.to_csv("outputs/tables/oos_split_table.csv")

    return oos_table


def print_oos_split_table(
    panel: pd.DataFrame | None = None,
    bps_list: list[float] | None = None,
    split: str = "2008-01-01",
    strategies: list[str] | None = None,
) -> pd.DataFrame:
    """
    Build and print the in-sample vs out-of-sample summary table.
    """
    table = build_oos_split_table(
        panel=panel,
        bps_list=bps_list,
        split=split,
        strategies=strategies,
    )

    print(f"\n=== In-sample vs Out-of-sample summary (split = {split}) ===")
    print(table)

    return table


# === HAC t-test of mean daily return ===
def hac_ttest_mean(daily_ret: pd.Series, lags: int = 20) -> dict[str, float]:
    """
    HAC/Newey-West t-test of the mean daily return for a single return series.
    """
    y = daily_ret.dropna().astype(float)

    if len(y) == 0:
        return {"mean_daily": np.nan, "t": np.nan, "p": np.nan}

    X = np.ones((len(y), 1))
    res = sm.OLS(y.values, X).fit(cov_type="HAC", cov_kwds={"maxlags": lags})

    return {
        "mean_daily": res.params[0],
        "t": res.tvalues[0],
        "p": res.pvalues[0],
    }



def build_hac_table(
    panel: pd.DataFrame | None = None,
    bps_list: list[float] | None = None,
    strategies: list[str] | None = None,
    lags: int = 20,
) -> pd.DataFrame:
    """
    Build HAC/Newey-West t-test results for portfolio strategy returns.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    if strategies is None:
        strategies = ["BH", "TSMOM", "VC_FLAT", "VC_CONTRARIAN"]

    ret_df = build_portfolio_returns(panel=panel, bps_list=bps_list)

    rows = []

    for strat in strategies:
        for c in bps_list:
            out = hac_ttest_mean(ret_df[(strat, c)], lags=lags)
            rows.append(
                {
                    "Strategy": strat,
                    "Cost_bps": int(c * 1e4),
                    "Mean_daily": out["mean_daily"],
                    "Mean_annual_%": out["mean_daily"] * 252 * 100,
                    "t_stat": out["t"],
                    "p_value": out["p"],
                }
            )

    df = pd.DataFrame(rows)
    df["Mean_daily"] = df["Mean_daily"].round(6)
    df["Mean_annual_%"] = df["Mean_annual_%"].round(2)
    df["t_stat"] = df["t_stat"].round(2)
    df["p_value"] = df["p_value"].round(3)
    df = df.sort_values(["Strategy", "Cost_bps"]).reset_index(drop=True)

    os.makedirs("outputs/tables", exist_ok=True)
    df.to_csv("outputs/tables/hac_results.csv", index=False)

    return df



def print_hac_table(
    panel: pd.DataFrame | None = None,
    bps_list: list[float] | None = None,
    strategies: list[str] | None = None,
    lags: int = 20,
) -> pd.DataFrame:
    """
    Build and print the HAC/Newey-West mean return table.
    """
    table = build_hac_table(
        panel=panel,
        bps_list=bps_list,
        strategies=strategies,
        lags=lags,
    )
    
    return table


# === CAPM alpha / beta table ===
def capm_alpha_beta(
    strategy_ret: pd.Series,
    benchmark_ret: pd.Series,
    lags: int = 20,
) -> dict[str, float]:
    """
    Estimate HAC-adjusted CAPM alpha and beta for a strategy return series
    against a benchmark return series.
    """
    df = pd.concat([strategy_ret, benchmark_ret], axis=1).dropna()

    if len(df) == 0:
        return {
            "alpha_ann": np.nan,
            "beta": np.nan,
            "t_alpha": np.nan,
            "p_alpha": np.nan,
        }

    y = df.iloc[:, 0].astype(float)
    x = sm.add_constant(df.iloc[:, 1].astype(float))

    res = sm.OLS(y, x).fit(cov_type="HAC", cov_kwds={"maxlags": lags})

    alpha_daily = res.params["const"]
    beta = res.params[df.columns[1]]
    t_alpha = res.tvalues["const"]
    alpha_annual = alpha_daily * 252

    return {
        "alpha_ann": alpha_annual,
        "beta": beta,
        "t_alpha": t_alpha,
        "p_alpha": res.pvalues["const"],
    }



def build_capm_table(
    panel: pd.DataFrame | None = None,
    bps_list: list[float] | None = None,
    strategies: list[str] | None = None,
    lags: int = 20,
) -> pd.DataFrame:
    """
    Build CAPM alpha / beta results for portfolio strategy returns using
    portfolio Buy & Hold as the benchmark.
    """
    if panel is None:
        panel = build_features()

    if bps_list is None:
        bps_list = [0.0, 0.0002, 0.0010]

    if strategies is None:
        strategies = ["TSMOM", "VC_FLAT", "VC_CONTRARIAN"]

    ret_df = build_portfolio_returns(panel=panel, bps_list=bps_list)

    rows = []

    for c in bps_list:
        bh = ret_df[("BH", c)]

        for strat in strategies:
            out = capm_alpha_beta(ret_df[(strat, c)], bh, lags=lags)
            rows.append(
                {
                    "Strategy": strat,
                    "Cost_bps": int(c * 1e4),
                    "Alpha_annual_%": out["alpha_ann"] * 100,
                    "Beta": out["beta"],
                    "t_alpha": out["t_alpha"],
                    "p_alpha": out["p_alpha"],
                }
            )

    df = pd.DataFrame(rows)
    df["Alpha_annual_%"] = df["Alpha_annual_%"].round(4)
    df["Beta"] = df["Beta"].round(4)
    df["t_alpha"] = df["t_alpha"].round(4)
    df["p_alpha"] = df["p_alpha"].round(4)
    df = df.sort_values(["Strategy", "Cost_bps"]).reset_index(drop=True)

    os.makedirs("outputs/tables", exist_ok=True)
    df.to_csv("outputs/tables/capm_results.csv", index=False)

    return df



def print_capm_table(
    panel: pd.DataFrame | None = None,
    bps_list: list[float] | None = None,
    strategies: list[str] | None = None,
    lags: int = 20,
) -> pd.DataFrame:
    """
    Build and print the CAPM alpha / beta table.
    """
    table = build_capm_table(
        panel=panel,
        bps_list=bps_list,
        strategies=strategies,
        lags=lags,
    )

    print("\n=== CAPM alpha / beta table ===")
    print(table)

    return table



