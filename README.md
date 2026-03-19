# Volatility-Conditioned Momentum Strategy (Multi-Asset Portfolio)

A systematic, cross-asset momentum strategy enhanced with volatility conditioning, designed to improve robustness, reduce drawdowns, and generate statistically significant returns across multiple market regimes.

---

## Overview

This project implements and evaluates a **volatility-conditioned time-series momentum framework** across a diversified global asset universe.

The core idea:

> Momentum works — but its performance is highly state-dependent. Conditioning on volatility regimes materially improves outcomes.

The system integrates:
- Cross-asset momentum signals  
- Volatility regime classification  
- Portfolio construction with static asset weights  
- Transaction cost modelling  
- Institutional-grade backtesting and evaluation  

---

## Strategy Variants

Four strategies are evaluated:

- **Buy & Hold (BH)** — passive benchmark  
- **TSMOM** — unconditional time-series momentum  
- **VC_FLAT** — volatility-conditioned momentum (risk-reducing)  
- **VC_CONTRARIAN** — volatility-conditioned contrarian overlay  

---

## Key Results

### 1. Equity Curve Behaviour

- At **0 bps and 2 bps**, **VC_CONTRARIAN clearly dominates**, delivering the strongest terminal performance.
- **VC_FLAT and BH track closely**, with BH eventually outperforming due to a strong 2025 rally.
- At **10 bps (conservative cost assumption)**:
  - **Buy & Hold wins**
  - **VC_CONTRARIAN remains competitive (2nd)**
  - **VC_FLAT ranks 3rd**
- **Unconditional TSMOM is consistently underwhelming**, showing weak growth and no persistent edge.

**Interpretation:**  
Volatility conditioning materially improves momentum, but **transaction costs are a binding constraint**, particularly for higher-turnover strategies.

---

### 2. Crisis Performance (High Signal)

#### Cumulative Returns

- **Global Financial Crisis (2008–2009):**
  - **VC_FLAT: +28.9%**
  - **VC_CONTRARIAN: +36.4%**
  - Strong outperformance vs BH and TSMOM

- **COVID (2020):**
  - Contrarian performs best (**+11.7%**)
  - VC strategies remain resilient

- **2022 Inflation Bear:**
  - All strategies struggle
  - VC strategies outperform BH meaningfully

#### Max Drawdown

- **VC_FLAT (best risk control):**
  - GFC: **-7.4%**
  - 2022: **-5.5%**
  - COVID: **~0%**

- Other strategies:
  - COVID: **-21% to -30%**
  - GFC: **-44% to -49%**
  - 2022: **-18% to -31%**

- **VC_CONTRARIAN is second-best** in drawdown control

**Interpretation:**  
Volatility conditioning is not only return-enhancing — it is **structurally risk-reducing**, particularly in crisis regimes.

---

### 3. Statistical Significance (HAC / Newey–West)

- Returns remain statistically significant after adjusting for:
  - Autocorrelation  
  - Heteroskedasticity  

This confirms:

> The strategy is not driven by noise or sampling artefacts.

---

### 4. CAPM Alpha

- Volatility-conditioned strategies exhibit:
  - **Positive alpha vs Buy & Hold**
  - Meaningful deviation from pure beta exposure

This indicates:

> Returns are not simply compensation for market risk.

---

### 5. Out-of-Sample Validation

- Performance remains **consistent out-of-sample**
- No evidence of:
  - Overfitting  
  - Regime-specific fragility  

**Interpretation:**  
The signal is **robust across time**, not just an in-sample artefact.

---

## Economic Intuition

Momentum performance deteriorates in:
- High-volatility environments  
- Reversal regimes  
- Crisis-driven dislocations  

Volatility conditioning allows the strategy to:
- Scale down risk during unstable periods  
- Switch behaviour (trend vs contrarian) depending on regime  
- Avoid large drawdowns typical of unconditional momentum  

---

## Portfolio Construction

- Multi-asset universe:
  - Equities, bonds, commodities, FX  
- Static cross-asset weights  
- Daily rebalancing with transaction cost modelling:
  - 0 bps  
  - 2 bps  
  - 10 bps  

---

## Architecture

The system is designed as a **fully reproducible, single-run pipeline** with clear separation between data processing, diagnostics, and portfolio backtesting.

### Data Layer
- `src/data/download.py` → downloads raw market data  
- `src/data/prices.py` → cleans and structures price data  
- `src/data/build_features.py` → builds returns, volatility, and signals  

### Diagnostics Layer (Research Validation)
- `src/diagnostics/summary_stats.py`  
- `src/diagnostics/regime_summary.py`  
- `src/diagnostics/regime_diagnostics.py`  
- `src/diagnostics/conditional_momentum_payoff.py`  
- `src/diagnostics/rv_distribution.py`  
- `src/diagnostics/rv_vs_threshold.py`  
- `src/diagnostics/high_vol_regimes.py`  

Validates:
- Regime behaviour  
- Volatility clustering  
- Conditional momentum payoffs  

### Portfolio Construction
- `src/portfolio/asset_weights.py` → cross-asset allocation  

### Backtesting Layer
- `src/backtest/engine.py` → asset-level strategy returns  
- `src/backtest/portfolio.py` → portfolio aggregation and evaluation  

### Pipeline Entry Point
- `run_pipeline.py` → executes entire workflow end-to-end  

---

## Outputs

All results are automatically generated into:

```
outputs/
├── tables/
└── figures/
```

### Tables (CSV)
- Portfolio performance (`portfolio_summary.csv`)  
- Strategy returns (`portfolio_returns.csv`)  
- HAC statistical tests (`hac_results.csv`)  
- CAPM alpha (`capm_results.csv`)  
- Out-of-sample validation (`oos_split_table.csv`)  
- Crisis performance (`crisis_performance.csv`)  
- Asset-level diagnostics and regime statistics  

### Figures (PNG)
- Equity curves (by transaction cost level)  
- Crisis heatmaps (returns and drawdowns)  
- Volatility regime visualisations  
- RV vs threshold diagnostics  

All outputs are fully reproducible from a single pipeline run.

---

## How to Run

```
python run_pipeline.py
```


This will:
- Download data (once)  
- Build features  
- Run full backtest  
- Generate all tables and figures  

No terminal output — fully automated pipeline.

---

## Why This Project Matters

This project demonstrates:

- End-to-end quant research workflow  
- Multi-asset portfolio construction  
- Regime-aware strategy design  
- Transaction cost-aware backtesting  
- Statistical validation (HAC, CAPM alpha, OOS testing)  

Most importantly:

> Incorporating market state (volatility) transforms a well-known anomaly (momentum) into a significantly more robust and risk-efficient strategy.

---

## Key Takeaways

- Momentum alone is fragile  
- Volatility conditioning materially improves:
  - Drawdowns  
  - Crisis performance  
  - Stability  
- Contrarian overlays can outperform in extreme regimes  
- Transaction costs are a critical constraint  
- Results are statistically and economically meaningful  

---

## Next Extensions

- Dynamic volatility thresholds  
- Regime-switching models (Markov / ML)  
- Risk parity weighting  
- Cross-sectional momentum integration  
- Live trading implementation  

---

## Author

Sam Chung
MSc Finance, Investment & Risk  
Quantitative Finance | Systematic Strategies | Portfolio Construction