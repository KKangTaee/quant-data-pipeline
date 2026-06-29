# Notes

- Interpret the user constraint `mdd는 -15% 이하` as drawdown magnitude no greater than 15%, meaning runtime MDD should be no worse than `-15%`.
- Current dynamic ETF promotion policy requires liquidity evidence when `promotion_min_liquidity_clean_coverage` is active. A disabled `Min Avg Dollar Volume 20D` filter makes `liquidity_policy_status=unavailable`, which blocks `real_money_candidate`.
- The GTAA strategy already had min-price filtering, but did not carry average-dollar-volume filtering. This task aligned GTAA with the strict-family liquidity evidence pattern.
- `real_money_candidate` is still a first-pass candidate signal. It is not Practical Validation pass, Final Review selection, live approval, broker order, or auto rebalance.
