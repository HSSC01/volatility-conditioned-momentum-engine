import pandas as pd
from src.data.build_features import build_features
from config.config import REALISED_VOLATILITY_WINDOW

def build_regime_summary(panel=None):
    if panel is None:
        panel = build_features()

    rv = panel.xs("RV_20", axis=1, level=1)
    regime = panel.xs("Vol_Regime", axis=1, level=1)

    stacked = (
        rv.stack()
        .rename("RV_20")
        .to_frame()
        .join(regime.stack().rename("Vol_Regime"))
        .dropna()
    )

    summary = (
        stacked
        .groupby([stacked.index.get_level_values(1), "Vol_Regime"])["RV_20"]
        .agg(Mean="mean", Median="median", Std="std", Count="count")
    )

    summary["Percent_of_Sample"] = (
        summary["Count"] / summary.groupby(level=0)["Count"].transform("sum") * 100
    )

    summary.index.names = ["Asset", "Vol_Regime"]

    summary = summary.sort_index()

    summary.to_csv("outputs/tables/regime_summary.csv")

    return summary


if __name__ == "__main__":
    build_regime_summary()