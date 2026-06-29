# Overview Market Context Historical Analog V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch: `codex/sub-dev`.
- Base commit: `352d31c8 Overview Market Context 이벤트 신뢰도 보강`.
- Pre-existing dirty/generated files include `finance/.DS_Store` and old `*-qa.png`; do not stage them.

## Design Decisions

- Use sector ETF proxy prices instead of current constituent membership replay to avoid overstating historical PIT correctness.
- Keep current leadership metadata as the selector only; historical analog computation starts from ETF proxy price history.
- Use a new small Streamlit-free service file because `app/services/overview_market_intelligence.py` is already over 6k lines.
- Keep Market Context display compact and subordinate to the market brief.
- Treat sample / data / PIT / survivorship caveats as first-class output, not footnotes hidden from the user.

## Coverage Probe

- Current `Overview > Sector / Industry` daily leadership on local DB: `Industrials` rank 1, market-cap-weighted return `+3.34%`, end snapshot `2026-06-12 00:18`.
- Sector ETF coverage:
  - Long-enough local rows: `XLE`, `XLP`, `XLRE`, `XLU`, `XLV`.
  - Short local rows: `XLB`, `XLC`, `XLF`, `XLI`, `XLK`, `XLY` each currently has 63 rows from `2026-03-02` to `2026-05-29`.
- Benchmark / comparison coverage:
  - `SPY`, `QQQ`, `TLT`, `GLD`, `IWM`, `LQD`: 5080 rows from `2006-03-21` to `2026-05-29`.
  - `HYG`: 4126 rows from `2010-01-04` to `2026-05-29`.
  - `UUP`: 63 rows, checked but not included in MVP default comparison set.
- Live analog state: current `Industrials -> XLI` returns `INSUFFICIENT_DATA`; UI shows `자료 부족` with the 63-row coverage reason.

## Initial Limitations To Surface

- Past statistics are not a future forecast.
- Sector ETF proxy is an approximation of sector leadership.
- Current sector/industry leadership metadata is not historical PIT sector membership.
- Sparse sample or short ETF history lowers reliability.
- Transaction cost and slippage are not reflected.
