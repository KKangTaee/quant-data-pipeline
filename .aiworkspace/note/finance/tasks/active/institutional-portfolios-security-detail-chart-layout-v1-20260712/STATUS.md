# Institutional Portfolios Security Detail Chart Layout V1 Status

Status: Completed
Started: 2026-07-12

## Progress

- 2026-07-12: User requested 1차부터 3차까지 sequential implementation for broker-like selected-security chart/detail layout.
- 2026-07-12: Added RED source-contract tests for market-like chart lower area, 2-row selected-security layout, and scrollable holder list.
- 2026-07-12: Implemented selected-security overview cards, full-width chart row with OHLC/volume strip, volume bars, chart navigator, and lower holder-list scroll panel.
- 2026-07-12: Browser QA confirmed `종목 분석 > 종목 상세` after selecting visible KO top holding: selected security card, portfolio-position context, stored price chart, navigator, and holder-list DOM rendered.

## Closeout

- Current active task returns to none.
- Follow-up candidates: a dedicated chart library such as `lightweight-charts`, better page-level scroll capture in Browser QA, and true multi-quarter holding-duration metrics if the user asks for deeper ticker analytics.
