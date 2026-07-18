# Futures Macro Pattern Outlook V1 Status

## 2026-07-18

- User requested a Futures Macro improvement after closing the economic-cycle / market-context work.
- Read-only audit confirmed that today risk evidence is useful, while 1D / 1W / 1M are disconnected return views and historical validation replays only one-day state.
- User approved the recommended boundary: overall market risk regime first, asset-family direction as supporting evidence, and 5D / 20D conditional outlook rather than long-term forecasting.
- User reviewed and approved the design contract.
- User compared three UI wireframes and selected `A · 맥락→전망형`.
- Detailed TDD implementation plan is written in `PLAN.md` with seven independently reviewable tasks.
- Current stage: inline execution started; linked worktree and baseline environment are being verified before Task 1 RED.
- Baseline investigation confirmed the repository-local runner is `unittest`; the implementation plan now records unittest equivalents instead of adding pytest.
- Task 1 complete: point-in-time 1D / 5D / 20D family features reuse existing score weights and preserve trailing-only calculations.
- Task 2 complete: current regime, transition phase, 60D path / ribbon, evidence, and change conditions are separated from future probabilities.
- Task 3 complete: 5D / 20D forward outcomes use as-of volatility, and similar dates are de-overlapped by trading-row episode spacing.
- Task 4 complete: chronological publication metrics, strict 30 / 60 episode gates, unavailable-number suppression, and latest-row cache are implemented.
- Task 5 complete: the thermometer snapshot now carries the current pattern, the tab loads the conditional outlook by default, and the V2 payload separates current observation from 5D / 20D probability estimates.
- Legacy historical-validation loading is no longer part of the active render path; refresh and reload clear the new latest-marker cache.
- Current stage: Task 6 Market Context-style React Workbench V2.
- No DB schema, provider, registry, or saved setup has been changed.

## Roadmap State

- 1차 설계 계약: approved
- 2차 상세 구현 계획: written
- 3차 service / validation implementation: in progress
- 4차 React Workbench V2: pending execution
- 5차 actual QA / docs sync: pending execution

## Next Action

Task 6에서 V1 React reading order와 lazy historical-validation panel을 A안의 horizon / path / ribbon / asset pathways / method sections로 교체한다.
