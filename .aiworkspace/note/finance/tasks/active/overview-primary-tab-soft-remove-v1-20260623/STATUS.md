# Overview Primary Tab Soft Remove V1 Status

## 2026-06-23

- User approved removing `Futures Monitor` and `Sector / Industry` from Overview after deciding their standalone value is unclear.
- Scope is 1차 soft-remove: primary navigation cleanup and documentation alignment.
- Completed: 1차 soft-remove implementation, docs alignment, focused contract tests, compile, diff hygiene, and Browser QA.

## Roadmap Position

- 1차: remove unclear primary tabs and preserve Market Context fallback.
- 2차: later review whether Market Context has enough absorbed futures / sector evidence.
- 3차: later decide whether to physically delete or repurpose unused helper UI.

## Verification

- RED/GREEN contract confirmed for Overview primary selector and removed-tab fallback.
- OverviewAutomationContractTests full class passed.
- `py_compile` passed for Overview dashboard modules.
- `git diff --check` passed.
- Browser QA passed on `http://localhost:8502`.
