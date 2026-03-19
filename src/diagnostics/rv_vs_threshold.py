import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator

from src.data.build_features import build_features
from config.config import REALISED_VOLATILITY_WINDOW, MVT_WINDOW


def plot_rv_vs_threshold(panel=None, asset: str | None = None):
    """
    Plot realised volatility vs median volatility threshold.

    - If asset is None → stacked plot for all assets
    - If asset is provided → single asset plot
    """
    if panel is None:
        panel = build_features()

    rv_col = f"RV_{REALISED_VOLATILITY_WINDOW}"
    mvt_col = f"MVT_{MVT_WINDOW}"

    assets = (
        [asset]
        if asset is not None
        else panel.columns.get_level_values(0).unique()
    )
    
    os.makedirs("outputs/figures/rv_vs_threshold", exist_ok=True)

    for a in assets:
        df = panel[a]
        fig, ax = plt.subplots(figsize=(16,5))
        df[rv_col].plot(ax=ax, label=rv_col)
        df[mvt_col].plot(ax=ax, label=mvt_col)

        ax.set_title(a, fontsize=12)
        ax.set_ylabel("Daily Volatility")

        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.YearLocator(1))

        ax.yaxis.set_major_locator(MaxNLocator(6))
        ax.tick_params(axis="both", labelsize=9)

        ax.legend(frameon=False, fontsize=9)

        plt.tight_layout()
        plt.savefig(f"outputs/figures/rv_vs_threshold/rv_vs_threshold_{a}.png", dpi=300)
        plt.close(fig)


if __name__ == "__main__":
    plot_rv_vs_threshold()