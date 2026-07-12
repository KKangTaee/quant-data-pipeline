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

- Implementation tests: not run because implementation has not started.
- Browser QA: not applicable during design review.
