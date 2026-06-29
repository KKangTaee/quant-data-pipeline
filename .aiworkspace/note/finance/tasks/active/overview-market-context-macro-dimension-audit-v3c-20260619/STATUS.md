# Status

Status: Complete
Last Updated: 2026-06-19

## Progress

- Opened the 3차-C task record for the approved Overview Market Context macro dimension audit.
- Confirmed existing 3A/3B task records and data docs keep this inside the Overview historical analog service/UI boundary.
- Confirmed this worktree is already isolated on `codex/sub-dev`.
- Added failing service/UI contract tests for `macro_dimension_audit`, including the local QA case where broad proxy coverage is insufficient.
- Added `macro_dimension_audit` under `macro_conditioned_analog` with used, reference, insufficient/unavailable, and deferred dimension statuses.
- Rendered compact `맥락 차원 상태` inside the existing `Macro 조건 포함 pilot` block.
- Updated roadmap, project map, data-flow note, root handoff logs, and task docs.
- Completed compile, full service contracts, Streamlit run, and Browser QA screenshot.

## Completed Scope

- Add additive `macro_dimension_audit` payload under `macro_conditioned_analog`.
- Render compact `맥락 차원 상태` inside the existing `Macro 조건 포함 pilot` UI block.
- Preserve broad analog, GLD condition, and futures condition behavior.

## Actual Conditions / Dimensions

- 실제 사용 조건: sector ETF vs SPY relative strength, GLD price proxy safe-haven / gold context, Rate Pressure futures proxy (`ZN=F` / `ZB=F`).
- 참고 preview: stored FRED `T10Y3M`, `VIXCLS`, `BAA10Y` availability, current bucket, coverage, and broad-anchor preview count.
- 보류 / annotation: Events calendar and CNN / AAII sentiment history.

## Not Doing

- No new collection, schema, provider, loader, registry/saved write, or render-time external fetch.
- No FRED / events / sentiment hard conditioning.
- No Backtest / Practical Validation / Final Review / Operations logic change.
