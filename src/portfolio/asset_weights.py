import numpy as np
import pandas as pd
from pathlib import Path

from src.diagnostics.conditional_momentum_payoff import build_conditional_momentum_spread


def apply_weight_cap(raw_weights: pd.Series, max_weight: float = 0.4) -> pd.Series:
    """
    Iteratively cap weights and redistribute excess across uncapped assets.
    """
    weights = raw_weights.copy().astype(float)

    if len(weights) == 0:
        return weights

    if weights.sum() <= 0:
        return pd.Series(1 / len(weights), index=weights.index)

    weights = weights / weights.sum()
    capped_weights = pd.Series(0.0, index=weights.index)
    remaining = weights.index.tolist()
    remaining_total = 1.0

    while remaining:
        scaled = weights.loc[remaining] / weights.loc[remaining].sum() * remaining_total
        over_cap = scaled > max_weight

        if not over_cap.any():
            capped_weights.loc[remaining] = scaled
            break

        capped_now = scaled[over_cap]
        capped_weights.loc[capped_now.index] = max_weight
        remaining_total -= max_weight * len(capped_now)
        remaining = [idx for idx in remaining if idx not in capped_now.index]

        if remaining_total <= 0:
            break

    return capped_weights / capped_weights.sum()


def build_asset_weights(panel=None, min_p: float = 0.01, long_only: bool = True, max_weight: float = 0.4) -> pd.DataFrame:
    """
    Build cross-asset weights based on regime-dependent momentum strength.
    """
    spread = build_conditional_momentum_spread(panel)
    df = spread.copy()

    df["p_adj"] = df["p_value"].clip(lower=min_p)
    df["score"] = df["Mean_Annualised"] / df["p_adj"]

    if long_only:
        df["score"] = df["score"].clip(lower=0)

    if df["score"].sum() == 0:
        df["weight"] = 1 / len(df)
    else:
        raw_weights = df["score"] / df["score"].sum()
        df["weight"] = apply_weight_cap(raw_weights, max_weight=max_weight)

    df = df[["Mean_Annualised", "p_value", "p_adj", "score", "weight"]].sort_values(
        "weight", ascending=False
    )

    df.to_csv("src/portfolio/asset_weights.csv", index=True)
    return df


if __name__ == "__main__":
    build_asset_weights()