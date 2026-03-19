import matplotlib.pyplot as plt
import os
from src.data.build_features import build_features

def plot_rv_distribution_by_regime(panel=None, n_assets=None):
    if panel is None:
        panel = build_features()
    
    all_assets = panel.columns.get_level_values(0).unique()
    assets = all_assets if n_assets is None else all_assets[:n_assets]

    n_cols = 5
    n_rows = (len(assets) + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 4 * n_rows))
    axes = axes.flatten()

    for ax, asset in zip(axes, assets):
        rv = panel[asset]["RV_20"]
        regime = panel[asset]["Vol_Regime"]

        low = rv[regime == "Low"]
        high = rv[regime == "High"]

        ax.hist(low, bins=30, alpha=0.6, density=True, label="Low")
        ax.hist(high, bins=30, alpha=0.6, density=True, label="High")

        ax.set_title(asset)
        ax.legend()

    for ax in axes[len(assets):]:
        ax.set_visible(False)

    plt.tight_layout()

    os.makedirs("outputs/figures", exist_ok=True)
    plt.savefig("outputs/figures/rv_distribution.png", dpi=300)


if __name__ == "__main__":
    plot_rv_distribution_by_regime()
