# Backtest Quarterly Productionization V1

Status: Implemented / QA passed
Started: 2026-07-08

## Why

Strict quarterly Quality / Value / Quality+Value strategies executed, but the product contract still labeled them as `Prototype / contract-smoke`.
The user wants to make quarterly eligible for the same kind of formal workflow as strict annual, not by renaming labels only, but by adding readiness, repair, runtime parity, validation evidence, and compatibility gates.

## Scope

- Single Strategy and Portfolio Mix Builder quarterly strict forms.
- Strict factor runtime wrappers and result metadata.
- Factor readiness / statement shadow / price repair UI contracts.
- Strategy evidence inventory, bridge eligibility, tests, and durable docs.

## Out Of Scope

- Live approval, broker order, account sync, or auto rebalance.
- Paid official historical index membership ingestion.
- Full provider replacement for symbols with persistent no-data gaps.
- Rewriting existing registries, saved setup JSONL, or run history artifacts.

## Development Roadmap

### 1차: Post-Run Quarterly Readiness

- Goal: Readiness should be based on actual backtest period / universe contract / result metadata, not only the pre-run preset.
- Files: `app/runtime/backtest/runners/strict_factor.py`, `app/web/backtest_result_display.py`, related readiness services/components.
- Done when: quarterly result bundle carries actionable readiness evidence for missing price, statement shadow, provider gap, and first active date.

### 2차: Repair Actions

- Goal: If the problem is resolvable data, the screen should offer a targeted action; if it is provider/source no-data, it should not present repeated refresh as a fix.
- Files: `app/services/backtest_price_refresh.py`, statement refresh action path, `app/web/backtest_common.py`, Factor Readiness component path.
- Done when: price and statement repair actions are scoped to affected symbols and unresolved provider gaps are explained as manual Data Trust / universe issues.

### 3차: Runtime Contract Parity

- Goal: Quarterly wrappers should accept and preserve annual-like investability / cost / benchmark / promotion / guardrail contracts where applicable.
- Files: `app/runtime/backtest/runners/strict_factor.py`, `app/services/backtest_execution.py`, compare catalog/page, saved replay/history helpers.
- Done when: quarterly payload, meta, history replay, and saved replay preserve the same contract fields as strict annual where the runtime supports them.

### 4차: Validation Evidence

- Goal: Replace contract-smoke-only evidence with repeatable validation checks for quarterly strict families.
- Files: tests, validation reports under `.aiworkspace/note/finance/reports/backtests/validation/`.
- Done when: focused tests cover quarterly readiness metadata, contract parity, and catalog/evidence state before promotion.

### 5차: Product Promotion

- Goal: Promote quarterly variants from `Prototype` to formal `Strict Quarterly` while keeping legacy keys compatible.
- Files: strategy catalog, evidence inventory, bridge/read model, UI labels, docs.
- Done when: user-facing labels no longer imply prototype, old strategy keys still dispatch, and docs/tests describe the new formal contract.

## Acceptance Notes

- 1차~4차 checks were implemented and verified before catalog/UI promotion.
- Legacy `_prototype` strategy keys remain for saved history/replay compatibility, but user-facing labels now read `Strict Quarterly`.
