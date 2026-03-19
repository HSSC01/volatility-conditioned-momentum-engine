import numpy as np
import pandas as pd
import statsmodels.api as sm
import os

from src.data.build_features import build_features


def _prepare_asset_frame(panel: pd.DataFrame, asset: str) -> pd.DataFrame:
    """
    Prepare a single-asset dataframe for conditional momentum payoff diagnostics.
    """
    df = panel[asset].copy()

    df["Next_Day_Return"] = df["Return"].shift(-1)
    df["Mom_Payoff_Proxy"] = df["Next_Day_Return"] * df["Momentum_Signal"]

    return df.dropna(subset=["Vol_Regime", "Momentum_Signal", "Next_Day_Return", "Mom_Payoff_Proxy"]).copy()


def build_conditional_momentum_payoff_table(
    panel: pd.DataFrame | None = None,
    hac_lags: int = 20,
) -> pd.DataFrame:
    """
    Build conditional momentum payoff table for every asset.

    Output index:
        (Asset, Regime)

    Regime rows:
        - High
        - Low
        - Low - High

    Columns:
        - Mean_Daily
        - Std_Daily
        - N
        - Mean_Annualised
        - t_stat
        - p_value
    """
    if panel is None:
        panel = build_features()

    results = []

    assets = panel.columns.get_level_values(0).unique()

    for asset in assets:
        df = _prepare_asset_frame(panel, asset)

        if df.empty:
            continue

        grp = df.groupby("Vol_Regime")["Mom_Payoff_Proxy"]
        summary = grp.agg(
            Mean_Daily="mean",
            Std_Daily="std",
            N="count",
        )

        # Ensure both regimes exist if possible
        summary = summary.reindex(["High", "Low"])
        summary["Mean_Annualised"] = summary["Mean_Daily"] * 252

        # Default empty diff row
        diff_row = pd.Series(
            {
                "Mean_Daily": np.nan,
                "Std_Daily": np.nan,
                "N": np.nan,
                "Mean_Annualised": np.nan,
                "t_stat": np.nan,
                "p_value": np.nan,
            },
            name="Low - High",
        )

        # HAC test only if both regimes are present
        if df["Vol_Regime"].nunique() == 2:
            d_high = (df["Vol_Regime"] == "High").astype(int).rename("D_high")
            y = df["Mom_Payoff_Proxy"].astype(float)
            X = sm.add_constant(d_high)

            res = sm.OLS(y, X, missing="drop").fit(
                cov_type="HAC",
                cov_kwds={"maxlags": hac_lags},
            )

            diff_row["Mean_Daily"] = summary.loc["Low", "Mean_Daily"] - summary.loc["High", "Mean_Daily"]
            diff_row["Mean_Annualised"] = diff_row["Mean_Daily"] * 252
            diff_row["t_stat"] = -res.tvalues["D_high"]
            diff_row["p_value"] = res.pvalues["D_high"]

        final_table = pd.concat([summary, diff_row.to_frame().T], axis=0)

        if "t_stat" not in final_table.columns:
            final_table["t_stat"] = np.nan
        if "p_value" not in final_table.columns:
            final_table["p_value"] = np.nan

        final_table["Asset"] = asset
        final_table["Regime"] = final_table.index

        results.append(final_table.reset_index(drop=True))

    out = pd.concat(results, axis=0)
    out = out.set_index(["Asset", "Regime"])[["Mean_Daily", "Std_Daily", "N", "Mean_Annualised", "t_stat", "p_value"]].sort_index()

    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/conditional_momentum_payoff.csv")

    return out

def build_conditional_momentum_spread(panel=None, hac_lags: int = 20) -> pd.DataFrame:
    table = build_conditional_momentum_payoff_table(panel=panel, hac_lags=hac_lags)
    table = table.xs("Low - High", level="Regime").sort_index()
    table.to_csv("outputs/tables/conditional_momentum_spread.csv")
    return table

