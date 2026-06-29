# Runs

## 2026-06-09

| Time KST | Command / Action | Result |
|---|---|---|
| 09:00 | docs / workflow boundary review | In progress |
| 09:05 | Unique-family strategy sweep | Found numeric pass candidates; 3-family Equal Weight / GTAA / GRS candidate had CAGR 13.93%, MDD -14.00% but Final Review selected-route was blocked by provider / efficacy evidence. |
| 09:16 | Cost evidence dry-runs | Added component cost / turnover / net-cost snapshots from runtime bundle metadata; Backtest Realism moved from `NEEDS_INPUT` to `REVIEW`. |
| 09:32 | `run_collect_macro_market_context(start=2026-05-01,end=2026-06-09,source_mode=csv)` | Success; wrote 77 macro rows after automatic FRED mode timed out. |
| 09:34 | Compact candidate recheck | `GTAA U3 85% / GRS Compact 10% / Risk Parity 5%` passed selected-route preflight with Final Review gate `READY_WITH_REVIEW`. |
| 09:37 | Persist Final Review / Monitoring | Saved source, Practical Validation result, Final Review decision `final_distinct_strategy_gtaa_u3_grs_risk_parity_20260609`, and Monitoring setup `selected_dashboard_portfolio_distinct_strategy_gtaa_grs_rp_20260609`. |
| 09:37 | Selected Dashboard recheck | Operation status `normal`; symbol freshness `SYMBOL_FRESHNESS_READY`; performance recheck `ok`. |
