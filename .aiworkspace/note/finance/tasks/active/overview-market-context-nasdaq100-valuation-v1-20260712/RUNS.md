# Overview Market Context Nasdaq-100 Valuation V1 Runs

Last Updated: 2026-07-12

## Design Discovery

- `git status --short`, branch, recent log: confirmed `codex/sub-dev`; unrelated market-interest research folder remains untracked.
- `rg` over ETF holdings/valuation/service/tests: existing `etf_holdings_snapshot`, Invesco QQQ parser, S&P calculation and React history contracts identified.
- SEC QQQ browse-edgar Atom smoke: NPORT-P feed returned official accession links without authentication.
- SEC search coverage smoke: 27 N-PORT period endings, 2019-09-30~2026-03-31.
- SEC N-30B-2 search: annual QQQ schedules found from at least 2014-09-30 onward.
- DB current QQQ holdings: 105 distinct symbols, 2026-05-08~2026-05-29.
- DB SEC diluted EPS coverage: 91/104 current equity symbols, 96.46% current QQQ weight.

## Verification

- Baseline: `.venv/bin/python -m unittest tests.test_sp500_valuation -v` — 37 tests passed; existing edgar deprecation warnings observed.
- Baseline React: `npm run build` — Vite build passed before implementation.
- 1차 RED: new Nasdaq test module failed with expected `ModuleNotFoundError`.
- 1차 GREEN: `.venv/bin/python -m unittest tests.test_nasdaq100_valuation -v` — pure parser/identity/EPS/drift/coverage/calibration tests passed during iteration.
- N-30B-2 regression: unrelated financial-statement tables initially overparsed; fixture reproduced the issue, parser was restricted to holdings schedule tables, and the focused test passed.
- SEC fetch regression: one `requests` connection stalled; stack trace showed the connection boundary. Bounded `urllib` fetch with retry loaded all 30 filings in 5.4 seconds and its focused retry test passed.
- Actual read-only spike: 119 rows for 2016-09~2026-07; latest-60 complete `5/60`; min coverage `92.62698%`; 2026-07 coverage `94.46678%`.
- Diagnostic calibration with the coverage gate temporarily disabled: reconstructed P/E `31.91997`, fixture `31.89`, APE `0.09398%`.
- Missing-source checks: direct SEC companyfacts USD/share EPS succeeded for relevant current/delisted CIKs; yfinance returned delisted/404 for missing historical tickers; Stooq returned proof-of-work HTML rather than CSV.
- DB/schema write, service, React selector, automation, Browser QA: not run because the approved 1차 coverage stop condition fired.
