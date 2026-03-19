# Research Note  
## From Academic Strategy to Multi-Asset Systematic Implementation  

---

## 1. Purpose  

This repository develops a volatility-conditioned momentum framework into a **fully implemented, multi-asset systematic trading strategy**.

The original concept—summarised in `volatility-conditioned momentum framework.png`—establishes that momentum returns are **regime-dependent**, with volatility acting as a state variable governing whether continuation or reversal dynamics dominate.

However, that framework is conceptual in nature. It does not address how such a signal behaves when:

- applied across multiple asset classes  
- aggregated into a portfolio  
- exposed to transaction costs  
- evaluated using rigorous statistical testing  

The purpose of this project is therefore to **bridge concept and implementation**—transforming a regime-based trading idea into a **scalable, testable, and empirically validated portfolio strategy**.

---

## 2. From Assignment to Research Extension  

The academic work demonstrated that:

- Momentum returns are **state-dependent**, not unconditional  
- Volatility acts as a **regime variable governing return dynamics**  
- Momentum performs well in **low-volatility environments**  
- Momentum weakens or reverses in **high-volatility regimes**  

However, the assignment was constrained by:

- Single asset (SPY proxy)  
- No portfolio aggregation  
- No transaction cost robustness  
- No cross-asset validation  
- Limited statistical inference  

This repository extends the framework across all these dimensions.

---

## 3. Core Contributions of This Project  

### 3.1 Cross-Asset Generalisation  

The strategy is applied across a diversified universe including:

- Equities  
- Government bonds  
- Commodities  
- FX  

This allows testing whether regime-dependent momentum is:

- **Asset-specific**, or  
- **A structural feature of financial markets**

---

### 3.2 Portfolio Construction Layer  

Unlike the assignment, which focused on a single return series, this project introduces:

- Asset-level signals  
- Portfolio aggregation via weights  
- Capital allocation across asset classes  

This transforms the strategy from a **signal-level concept** into a **deployable portfolio system**.

---

### 3.3 Realistic Implementation  

The framework incorporates several practical considerations:

- Transaction costs: **0, 2, and 10 bps (round-trip)**  
- Daily rebalancing with no look-ahead bias  
- Out-of-sample (OOS) validation  
- HAC (Newey-West) inference for mean returns  
- CAPM alpha testing vs Buy & Hold  

This moves the strategy closer to **institutional-grade evaluation standards**.

---

## 4. Strategy Evolution  

The initial strategy framework proposed a **binary regime-switching rule**:

- Low volatility → momentum (trend-following)  
- High volatility → no position (flat exposure)  

This original formulation (as shown in `volatility-conditioned momentum framework.png`) served as a **conceptual starting point**, designed to eliminate momentum crash risk during high-volatility regimes.

This repository extends that framework into two practical implementations:

| Strategy | Description |
|--------|------------|
| **VC_FLAT** | Momentum in low volatility, flat (no position) in high volatility |
| **VC_CONTRARIAN** | Momentum in low volatility, reversal (−signal) in high volatility |

Additionally, an unconditional benchmark is retained:

| Strategy | Description |
|--------|------------|
| **TSMOM** | Unconditional momentum (baseline) |

This evolution reflects a progression from:

- Conceptual design (flat exposure in stress regimes)  
- Risk-controlled implementation (VC_FLAT)  
- Full regime exploitation via reversal dynamics (VC_CONTRARIAN)  

---

## 5. Key Empirical Findings  

### 5.1 Performance Across Costs  

- **VC_CONTRARIAN dominates at low transaction costs (0–2 bps)**  
- **Buy & Hold dominates at high costs (10 bps)**  
- **Unconditional TSMOM is consistently weak**  

Interpretation:

> Momentum without regime conditioning is structurally fragile.

---

### 5.2 Crisis Performance  

Across major stress periods:

- Global Financial Crisis (2008–09)  
- COVID shock (2020)  
- Inflation bear market (2022)  

Findings:

- **VC strategies significantly outperform during crises**  
- **VC_FLAT achieves the lowest drawdowns**  
- **VC_CONTRARIAN delivers the strongest crisis returns**  

Example insight:

- During the GFC:
  - VC_FLAT: strong positive returns with minimal drawdown  
  - VC_CONTRARIAN: highest cumulative returns (~30–36%)  

Interpretation:

> Regime conditioning improves **downside protection and crisis convexity**, not just average returns.

---

### 5.3 Drawdown Characteristics  

- VC_FLAT:
  - Extremely low drawdowns across all crises  
  - Acts as a **defensive overlay**  

- VC_CONTRARIAN:
  - Second-best drawdowns  
  - Strong upside during rebounds  

- Buy & Hold / TSMOM:
  - Large drawdowns (−40% to −50% range in GFC)  

---

## 6. Economic Interpretation  

The results reinforce the theoretical mechanism proposed in the assignment:

- **Low volatility regimes**:
  - Gradual information diffusion  
  - Institutional flow persistence  
  - Trend continuation dominates  

- **High volatility regimes**:
  - Deleveraging and liquidity shocks  
  - Funding constraints tighten  
  - Rapid reversals and overshooting  

This aligns with:

- Underreaction → continuation  
- Overreaction → reversal  

Key extension:

> The multi-asset evidence suggests that regime-dependent momentum is not equity-specific, but reflects a broader **market-wide behavioural and risk-based mechanism**.

---

## 7. Limitations  

Despite strong empirical results, several limitations remain:

- Volatility may proxy for:
  - Liquidity stress  
  - Funding constraints  
  - Risk aversion shifts  

- Regime classification:
  - Based on median threshold (arbitrary choice)  

- Binary exposure:
  - Ignores signal strength and magnitude  

- No volatility scaling or leverage  
- No cross-sectional momentum integration  
- No machine learning regime detection  

---

## 8. Future Extensions  

Potential improvements include:

- Volatility-managed position sizing  
- Continuous (non-binary) regime modelling  
- Cross-sectional + time-series hybrid strategies  
- Regime detection via ML or macro factors  
- Capacity and turnover optimisation  

---

## 9. Positioning  

This repository transforms a theoretical MSc-level study into a **fully implemented, multi-asset systematic trading framework**.

It demonstrates:

- How academic asset pricing insights can be operationalised  
- How regime-dependent signals behave under realistic constraints  
- How strategy performance changes under transaction costs and crisis conditions  

The project sits at the intersection of:

- **Academic research (asset pricing & behavioural finance)**  
- **Quantitative implementation (Python, backtesting, portfolio construction)**  
- **Practical strategy evaluation (costs, robustness, statistical testing)**  

---

## 10. Relationship to Academic Work  

The academic foundation for this project can be found in:

- `volatility-conditioned momentum framework.png`  

This research note serves as a **bridge between conceptual framework and full implementation**, demonstrating how an initial academic idea can be developed into a **scalable, multi-asset quantitative system**.

---