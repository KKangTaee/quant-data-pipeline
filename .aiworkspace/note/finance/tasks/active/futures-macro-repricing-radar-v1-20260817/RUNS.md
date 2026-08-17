# Futures Macro Repricing Radar V1 Runs

| Run | Result |
|---|---|
| Worktree detection | linked worktree `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`, branch `codex/sub-dev` |
| Baseline focused test | `tests/test_overview_futures_macro_short_horizon.py`: 23 passed |
| Payload TDD RED | V6 schema, missing `market_repricing`, remaining forecast field로 expected 5 failures |
| Payload/source focused GREEN | short horizon + integration + source contract: 28 passed |
| React production build | Vite 180 modules, build success |
| Actual DB payload | 2026-08-14 completed snapshot, V7 `NEW_SHOCK`, future gate absent |
| Futures Macro regression | 145 passed, 15 subtests passed, 3 dependency deprecation warnings |
| Browser QA | narrow viewport 725px component, forecast phrase 0, repricing/new shock visible, horizontal overflow false, console errors 0 |
| Full shared service contracts | unrelated existing sentiment overlay mismatch에서 중단: expected `OK`, actual `REVIEW` (66 passed before first failure) |
| Self review | core/confirmation risk normalization, 5D→1D fallback, user-visible copy, React payload/render order, scope-only docs 검토; task-owned blocking issue 없음 |
