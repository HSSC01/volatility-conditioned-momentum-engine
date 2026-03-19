import os

from src.data.download import download_data
from src.data.prices import get_prices
from src.data.build_features import build_features

from src.diagnostics.summary_stats import build_summary_stats
from src.diagnostics.rv_distribution import plot_rv_distribution_by_regime
from src.diagnostics.rv_vs_threshold import plot_rv_vs_threshold
from src.diagnostics.high_vol_regimes import plot_price_with_high_vol_regimes
from src.diagnostics.regime_summary import build_regime_summary
from src.diagnostics.regime_diagnostics import (
    build_annual_regime_means,
    build_annual_momentum_regime_means,
    build_distribution_stats,
    build_regime_persistence,
    build_regime_diagnostics_table,
)
from src.diagnostics.conditional_momentum_payoff import (
    build_conditional_momentum_payoff_table,
    build_conditional_momentum_spread,
)

from src.portfolio.asset_weights import build_asset_weights

from src.backtest.engine import build_asset_performance_summary
from src.backtest.portfolio import (
    build_portfolio_returns,
    build_portfolio_summary,
    plot_equity_curves,
    build_crisis_performance,
    plot_crisis_heatmaps,
    build_oos_split_table,
    build_hac_table,
    build_capm_table,
)


def ensure_dirs() -> None:
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("outputs/tables", exist_ok=True)
    os.makedirs("outputs/figures", exist_ok=True)
    os.makedirs("outputs/figures/equity_curves", exist_ok=True)
    os.makedirs("outputs/figures/crisis_heatmaps", exist_ok=True)
    os.makedirs("outputs/figures/high_vol_regimes", exist_ok=True)
    os.makedirs("outputs/figures/rv_vs_threshold", exist_ok=True)


def run_pipeline() -> None:
    ensure_dirs()

    # Download once
    raw_data = download_data()

    # Build once
    prices = get_prices(raw_data=raw_data)
    panel = build_features(prices=prices)

    # Save core processed data
    prices.to_csv("data/processed/prices.csv")
    panel.to_csv("data/processed/full_features.csv")

    # Diagnostics tables
    build_summary_stats(prices=prices).to_csv("outputs/tables/Data_Summary_Stats.csv")
    build_regime_summary(panel=panel).to_csv("outputs/tables/regime_summary.csv")
    build_annual_regime_means(panel=panel).to_csv("outputs/tables/annual_regime_means.csv")
    build_annual_momentum_regime_means(panel=panel).to_csv("outputs/tables/annual_momentum_regime_means.csv")
    build_distribution_stats(panel=panel).to_csv("outputs/tables/distribution_stats.csv")
    build_regime_persistence(panel=panel).to_csv("outputs/tables/regime_persistence.csv")
    build_regime_diagnostics_table(panel=panel).to_csv("outputs/tables/regime_full_diagnostics.csv")
    build_conditional_momentum_payoff_table(panel=panel).to_csv("outputs/tables/conditional_momentum_payoff.csv")
    build_conditional_momentum_spread(panel=panel).to_csv("outputs/tables/conditional_momentum_spread.csv")

    # Diagnostics figures
    plot_rv_distribution_by_regime(panel=panel)
    plot_rv_vs_threshold(panel=panel)
    plot_price_with_high_vol_regimes(panel=panel)

    # Weights
    build_asset_weights(panel=panel).to_csv("outputs/tables/asset_weights.csv")

    # Asset-level backtest
    build_asset_performance_summary(panel=panel).to_csv("outputs/tables/asset_performance_summary.csv")

    # Portfolio-level backtest
    build_portfolio_returns(panel=panel).to_csv("outputs/tables/portfolio_returns.csv")
    build_portfolio_summary(panel=panel).to_csv("outputs/tables/portfolio_summary.csv")
    plot_equity_curves(panel=panel)
    build_crisis_performance(panel=panel).to_csv("outputs/tables/crisis_performance.csv")
    plot_crisis_heatmaps(panel=panel)
    build_oos_split_table(panel=panel).to_csv("outputs/tables/oos_split_table.csv")
    build_hac_table(panel=panel).to_csv("outputs/tables/hac_results.csv", index=False)
    build_capm_table(panel=panel).to_csv("outputs/tables/capm_results.csv", index=False)


if __name__ == "__main__":
    run_pipeline()