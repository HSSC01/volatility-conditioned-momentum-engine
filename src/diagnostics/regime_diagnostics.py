import numpy as np
import pandas as pd
import os
from scipy import stats

from src.data.build_features import build_features


def _get_asset_diagnostic_frame(panel: pd.DataFrame, asset: str) -> pd.DataFrame:
    """
    Extract a single asset diagnostic dataframe from the multi-asset feature panel.
    """
    df = panel[asset].copy()

    df["Next_Day_Return"] = df["Return"].shift(-1)

    return df.dropna(subset=["Vol_Regime", "Momentum_Signal", "Next_Day_Return"]).copy()


def build_annual_regime_means(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Annualised next-day mean return by volatility regime for each asset.
    """
    if panel is None:
        panel = build_features()

    results = []

    for asset in panel.columns.get_level_values(0).unique():
        df = _get_asset_diagnostic_frame(panel, asset)

        summary = (
            df.groupby("Vol_Regime")["Next_Day_Return"]
            .mean()
            .mul(252)
            .rename("Annualised_Mean_Next_Day_Return")
            .reset_index()
        )
        summary["Asset"] = asset
        results.append(summary)

    out = pd.concat(results, axis=0)
    out = out.set_index(["Asset", "Vol_Regime"]).sort_index()
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/annual_regime_means.csv")
    return out


def build_annual_momentum_regime_means(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Annualised next-day mean return by volatility regime and momentum signal for each asset.
    """
    if panel is None:
        panel = build_features()

    results = []

    for asset in panel.columns.get_level_values(0).unique():
        df = _get_asset_diagnostic_frame(panel, asset)

        summary = (
            df.groupby(["Vol_Regime", "Momentum_Signal"])["Next_Day_Return"]
            .mean()
            .mul(252)
            .unstack()
        )
        summary["Asset"] = asset
        results.append(summary.reset_index())

    out = pd.concat(results, axis=0)
    out = out.set_index(["Asset", "Vol_Regime"]).sort_index()
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/annual_momentum_regime_means.csv")
    return out


def _dist_stats(x: pd.Series) -> pd.Series:
    return pd.Series(
        {
            "Mean": x.mean() * 252,
            "Std": x.std(),
            "Skew": stats.skew(x, bias=False),
            "Kurtosis": stats.kurtosis(x, fisher=False, bias=False),
        }
    )


def build_distribution_stats(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Distribution stats of next-day returns by volatility regime and momentum signal for each asset.
    """
    if panel is None:
        panel = build_features()

    results = []

    for asset in panel.columns.get_level_values(0).unique():
        df = _get_asset_diagnostic_frame(panel, asset)

        summary = (
            df.groupby(["Vol_Regime", "Momentum_Signal"])["Next_Day_Return"]
            .apply(_dist_stats)
            .unstack()
        )

        summary["Asset"] = asset
        results.append(summary.reset_index())

    out = pd.concat(results, axis=0)
    out = out.set_index(["Asset", "Vol_Regime", "Momentum_Signal"]).sort_index()
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/distribution_stats.csv")
    return out


def build_regime_persistence(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Regime persistence probabilities and average cluster lengths for each asset.
    """
    if panel is None:
        panel = build_features()

    results = []

    for asset in panel.columns.get_level_values(0).unique():
        df = panel[asset].copy().dropna(subset=["Vol_Regime"]).copy()

        reg = df["Vol_Regime"]
        reg_tm1 = reg.shift(1)

        p_high_high = (
            ((reg == "High") & (reg_tm1 == "High")).sum() / (reg_tm1 == "High").sum()
            if (reg_tm1 == "High").sum() > 0
            else np.nan
        )
        p_low_low = (
            ((reg == "Low") & (reg_tm1 == "Low")).sum() / (reg_tm1 == "Low").sum()
            if (reg_tm1 == "Low").sum() > 0
            else np.nan
        )

        run_id = (reg != reg_tm1).cumsum()
        runs = df.groupby(run_id).agg(
            Regime=("Vol_Regime", "first"),
            Length=("Vol_Regime", "size"),
        )
        mean_cluster_length = runs.groupby("Regime")["Length"].mean()

        result = pd.DataFrame(
            {
                "Persistence_Prob": {
                    "High": p_high_high,
                    "Low": p_low_low,
                },
                "Avg_Duration_Days": {
                    "High": mean_cluster_length.get("High", np.nan),
                    "Low": mean_cluster_length.get("Low", np.nan),
                },
            }
        )

        result["Asset"] = asset
        results.append(result.reset_index(names="Vol_Regime"))

    out = pd.concat(results, axis=0)
    out = out.set_index(["Asset", "Vol_Regime"]).sort_index()
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/regime_persistence.csv")
    return out


def build_regime_diagnostics_table(panel: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Combined regime diagnostics table per asset and regime:
    - % of sample
    - mean realised volatility
    - persistence probability
    - average duration
    """
    if panel is None:
        panel = build_features()

    results = []

    for asset in panel.columns.get_level_values(0).unique():
        df = panel[asset].copy().dropna(subset=["RV_20", "Vol_Regime"]).copy()

        regime_summary = df.groupby("Vol_Regime")["RV_20"].agg(
            Mean_RV="mean",
            Count="count",
        )
        regime_summary["%_Sample"] = regime_summary["Count"] / len(df) * 100

        reg = df["Vol_Regime"]
        reg_tm1 = reg.shift(1)

        p_high_high = (
            ((reg == "High") & (reg_tm1 == "High")).sum() / (reg_tm1 == "High").sum()
            if (reg_tm1 == "High").sum() > 0
            else np.nan
        )
        p_low_low = (
            ((reg == "Low") & (reg_tm1 == "Low")).sum() / (reg_tm1 == "Low").sum()
            if (reg_tm1 == "Low").sum() > 0
            else np.nan
        )

        run_id = (reg != reg_tm1).cumsum()
        runs = df.groupby(run_id).agg(
            Regime=("Vol_Regime", "first"),
            Length=("Vol_Regime", "size"),
        )
        mean_cluster_length = runs.groupby("Regime")["Length"].mean()

        regime_summary["Persistence_Prob"] = [
            p_high_high if r == "High" else p_low_low for r in regime_summary.index
        ]
        regime_summary["Avg_Duration_Days"] = [
            mean_cluster_length.get(r, np.nan) for r in regime_summary.index
        ]

        regime_summary["Asset"] = asset
        results.append(regime_summary.reset_index())

    out = pd.concat(results, axis=0)
    out = (out.set_index(["Asset", "Vol_Regime"])[["%_Sample", "Mean_RV", "Persistence_Prob", "Avg_Duration_Days"]].sort_index())
    os.makedirs("outputs/tables", exist_ok=True)
    out.to_csv("outputs/tables/regime_full_diagnostics.csv")
    return out


if __name__ == "__main__":
    build_regime_diagnostics_table()