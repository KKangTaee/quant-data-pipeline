# Status

Status: Complete
Last Updated: 2026-06-20

## Summary

`Overview > Market Context` V8 follow-up. V7 made smart refresh exclude Events caveats, but source confidence still counted Events and Data Health as unresolved `자료 확인 필요`. This task makes actionability explicit so non-actionable caveats and management meta do not look like unresolved refresh issues.

## Completed

- Started task and implementation plan.
- Added source-confidence actionability metadata so direct brief sources, reference context, and management meta are distinct.
- Made the top Market Context `자료 상태` count actionable refresh items rather than non-actionable caveats.
- Reclassified Events estimate limitations as `참고 제한` and Data Health rows as `관리 메타`.
- Split the source confidence disclosure into `브리프 자료` and `참고 / 관리 메타`.
- Verified focused tests, full service contract tests, py_compile, diff check, and Browser QA screenshot.

## Pending

- none

## Boundary

- No provider fetch during UI render.
- No schema / loader / registry / saved JSONL changes.
- No trading / validation / monitoring semantics.
