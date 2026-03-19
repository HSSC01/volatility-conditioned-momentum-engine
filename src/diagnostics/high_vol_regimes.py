import os
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from src.data.build_features import build_features


def plot_price_with_high_vol_regimes(panel=None, asset: str | None = None, persistence_window: int = 20):
    if panel is None:
        panel = build_features()

    assets = (
        [asset]
        if asset is not None
        else panel.columns.get_level_values(0).unique()
    )

    for a in assets:
        asset_df = panel[a].copy()

        fig, ax = plt.subplots(figsize=(16, 6))

        np.log(asset_df["Close"]).plot(ax=ax)

        ax.set_title(
            f"log({a}) with High-Volatility Regimes Shaded "
            f"({persistence_window}-day persistence)",
            fontsize=16,
        )
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("log(Price)", fontsize=12)

        high = (asset_df["Vol_Regime"] == "High").astype(int)
        high_smooth = (high.rolling(persistence_window).sum() >= persistence_window).astype(int)

        starts = asset_df.index[high_smooth.diff() == 1]
        ends = asset_df.index[high_smooth.diff() == -1]

        if len(high_smooth) > 0 and high_smooth.iloc[0] == 1:
            starts = starts.insert(0, asset_df.index[0])

        if len(high_smooth) > 0 and high_smooth.iloc[-1] == 1:
            ends = ends.insert(len(ends), asset_df.index[-1])

        for s, e in zip(starts, ends):
            ax.axvspan(s, e, alpha=0.3)

        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_minor_locator(mdates.YearLocator(1))
        ax.tick_params(axis="both", labelsize=10)

        plt.tight_layout()


        os.makedirs("outputs/figures/high_vol_regimes", exist_ok=True)
        path = f"outputs/figures/high_vol_regimes/high_vol_{a.lower()}.png"
        plt.savefig(path, dpi=300)


if __name__ == "__main__":
    plot_price_with_high_vol_regimes()