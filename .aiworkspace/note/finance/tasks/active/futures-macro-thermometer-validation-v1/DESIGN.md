# Futures Macro Thermometer Validation V1 Design

## Read Model Contract

`app/services/futures_macro_validation.py` owns historical validation. It reads:

- `finance_price.futures_ohlcv` for core futures daily OHLCV and futures target returns.
- `finance_price.nyse_price_history` for ETF proxy target returns when a preferred futures target is unavailable.

It returns DataFrames and compact dictionaries only. It does not write registries, saved setup, run history, or DB rows.

## Point-In-Time Rule

For each validation date:

1. Use only candles with `date <= validation_date`.
2. Require enough lookback to compute 60D volatility.
3. Call the same score and scenario functions used by the current snapshot.
4. Compare the scenario / scores with target forward returns that begin after the validation date.

This is still a stored-provider historical reconstruction. yfinance continuous futures roll behavior can differ from tradable contract history, so UI and docs must show that caveat.

## Target Preference

| Validation family | Preferred futures | ETF proxy fallback |
| --- | --- | --- |
| Risk assets | `ES=F`, `NQ=F`, `RTY=F` | `SPY`, `QQQ`, `IWM` |
| Rates / duration | `ZN=F`, `ZB=F` | `TLT` |
| Gold | `GC=F` | `GLD` |
| Dollar pressure | FX basket from `6E=F`, `6J=F`, `6B=F`, `6A=F`, `6C=F` | `UUP` |

## Confidence Inputs

- Daily data coverage
- 60D standardized symbol count
- strong evidence count
- weak evidence count
- missing symbol count
- conflicting score count
- latest daily candle age
- current scenario directional historical sample size / hit rate when the scenario has a directional rule
- current scenario occurrence count when the scenario is mixed and should not be forced into risk-on / risk-off

Confidence labels:

- `High Confidence`
- `Medium Confidence`
- `Low Confidence`
- `Not Enough History`

## UI Contract

Macro Thermometer should show:

- Current scenario and cautious interpretation
- Interpretation Confidence card
- Historical Validation Summary card
- Current scenario directional sample size / hit rate, or occurrence count with hit-rate N/A for mixed scenarios
- Strong evidence / weak evidence / conflicting evidence sections
- Caveats that validation is historical consistency evidence, not a prediction guarantee
