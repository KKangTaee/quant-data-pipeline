# Status

- 2026-06-01: Started. Read docs/index/roadmap/project map and Backtest/Portfolio Selection flows.
- 2026-06-01: Identified missing field propagation in dynamic ETF runtime/dispatch/replay, not in selected-route gate policy.
- 2026-06-01: Implemented dynamic ETF promotion policy defaults across runtime, single execution dispatch, compare defaults/overrides, Practical Validation replay, and candidate source snapshots.
- 2026-06-01: Fresh `GRS Liquid Macro Top2` run now carries `promotion_min_net_cagr_spread=-0.02`; Practical Validation stored-period replay PASS; selected-route preflight and Final Review selected gate both ready.
- 2026-06-01: Regression coverage added for proof-deficient Equal Weight-style missing net cost / turnover evidence; selected-route preflight remains blocked.
