# Status

## 2026-06-15

- Started after the user approved adding historical analog data repair while making the V3 lower flow visibly different.
- Added generalized historical analog coverage gaps and repair action metadata.
- Added `run_overview_historical_analog_ohlcv` in the Overview action facade, reusing the existing OHLCV collection job with a managed-safe profile.
- Updated Market Context UI:
  - `참고: 과거 유사 맥락` now shows a visible gap panel with missing ETF ticker, row count, window, and `보조 갱신` guidance.
  - `보조 갱신` now exposes a `부족 ETF 가격 이력 보강` button when the model reports missing historical analog inputs.
  - `근거: 자료 기준 / 출처 상태` now shows normal / review / missing counts and key source pills in the collapsed summary.
- Browser QA confirmed live data was not fixed to Technology / XLK. Current live leadership was Communication Services, so the repair target was `XLC`.
- Completed code, contract tests, static checks, Browser QA screenshot, and doc sync.
