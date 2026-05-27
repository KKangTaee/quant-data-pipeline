# Practical Validation Helper Boundary Risks

Status: Complete
Created: 2026-05-27

## Closeout

No open risk remains for Task 6. Task 7 should still avoid mixing diagnostics helper extraction with calculation changes.

## Active Risks

| Risk | Mitigation |
| --- | --- |
| Import path update misses a docs or service reference | Run `rg` for old module paths after edits |
| Provider context helper import triggers DB access during import | Keep loader calls inside functions and run service import contract test |
| File move is mistaken for behavior change | Avoid changing helper internals; verify tests and boundary lint |
| Browser QA is skipped despite a visible break | Run Python imports/contract tests; use browser only if visible flow or displayed shape changes |
