# Overview Futures Macro Short-Horizon V1 Runs

Last Updated: 2026-07-24

## Read-only diagnosis

- Loaded the compatible stored snapshot from `finance_meta.futures_macro_snapshot`.
- Observed snapshot metadata: as-of `2026-07-22`, schema `futures_macro_snapshot_v2`, algorithm `pattern_outlook_v5_same_state_nested_hybrid`.
- Observed daily coverage: 17/17 standardized, 22,448 stored rows in the current compact macro read, max data days 1,321.
- Derived direct score inputs from code: 15 symbols across six families.
- Read Git history: initial Macro Thermometer family definitions date to 2026-06-02; DXY was added to the shared core preset on 2026-07-17; five active asset pathways were introduced on 2026-07-18 without growth.

## Visual QA

- Rendered the approved 4+2 mockup from actual 2026-07-22 family values.
- DOM confirmed the three-step flow, four core rows, two confirmation cards, calculation scope, and approval controls.
- Browser warning/error log was empty.
- User selected `approve-core4-confirm2`.

## Implementation verification

- Baseline focused suite: 49 passed, 15 subtests passed.
- Integrated Futures Macro suite after session/fingerprint changes: 67 passed, 15 subtests passed.
- React/Vite production bundle build passed after the approved UI change.
- `git diff --check` passed before implementation commits.

## Actual refresh diagnosis and timing

- Coverage plan query: 17 routine symbols, 0 bootstrap symbols, one-year routine overlap.
- Provider/DB before-after comparison: 4,397 recent rows compared; only 17 rows changed, all dated `2026-07-22`, one per symbol.
- Slow path actual: 4,284 rows, download/normalize 6.845s, UPSERT 0.155s, input compare 2.938s, nested materialization 54.842s, total 64.859s.
- After finalized-session fix and compatible current replacement: same 4,284-row refresh, download/normalize 9.755s, UPSERT 0.156s, input compare 2.941s, nested materialization 0s, total 12.936s, snapshot status `reused_pending`.
- cProfile on a genuinely changed completed input: 420,936,066 calls in profiler mode; nested horizon selection/forecast and analog distance ranking dominate. This remains a separate deeper model-performance boundary.

## Final verification and Browser QA

- `py_compile` passed for the Futures Macro helper, action/ingestion jobs, pattern/snapshot services, collector, and loader.
- Final focused suite: 69 passed, 15 subtests passed.
- Futures Macro service-contract subset: 26 passed, 840 deselected.
- Vite production build: 177 modules transformed; CSS 25.26 kB, JS 335.84 kB.
- Actual Browser QA at the local sub-dev Streamlit app confirmed the three-step decision flow, all core 4 + confirmation 2 families, `방향 예측 근거 부족`, baseline explanation, calculation scope, pending-session disclosure, and secondary `최근 체제 이력`.
- 420px QA: outer client/scroll width 420/420; workbench main client/scroll width 377/377; no console warning/error.
- Representative generated screenshot: `futures-macro-short-horizon-v1-qa.png` (untracked, not staged).

## Confirmation matrix follow-up

- TDD RED: `test_confirmation_signals_use_explicit_recent_window_headers` failed against the former card footer because no explicit confirmation window headers existed.
- GREEN: the full focused source-contract file passed with 10 tests after `DirectionHeaders` became label-configurable and confirmation reused `DirectionRow`.
- Vite production build passed with 177 transformed modules; generated CSS 25.02 kB and JS 335.86 kB.
- Actual desktop DOM: one confirmation block, headers `신호 / 최근 1D / 최근 5D / 최근 20D`, and exactly two signal rows.
- Actual 420px QA: outer width 420/420, component frame 377/377, confirmation block 327/327 client/scroll width; no horizontal overflow.
- The reload-only Streamlit `WebSocket onclose` warnings were isolated from the feature; a clean initial-load tab rendered the confirmation matrix with zero warning/error.
- Representative generated screenshot: `futures-macro-confirmation-matrix-qa.png` (untracked, not staged).

## Spec self-review

- Placeholder scan: no `TBD`, `TODO`, or incomplete requirement remains.
- Consistency: retained 60D regime history as secondary content instead of inferring deletion from the approved primary mockup.
- Scope: kept family/model formulas, DXY/silver membership, DB schema, and backend 20D history out of the implementation change.
- Ambiguity: fixed routine overlap to `1y/1d` and defined unchanged-input fingerprint fields and rebuild conditions.

## Implementation-plan self-review

- Added exact files, red/green commands, verification criteria, and coherent Korean commit boundaries for five execution units.
- Confirmed the existing fingerprint comparison occurs after both builders and planned the comparison before builder invocation.
- Preserved backend 20D evidence and the secondary 60D ribbon while removing them only from the primary short-horizon decision surface where approved.
- Added actual backend timing evidence for download/normalize, UPSERT, input comparison, and materialization; no run diagnostics panel is introduced.
- Placeholder scan found no `TODO`, `TBD`, incomplete code ellipsis, or unresolved product choice.

## On-demand daily finalization follow-up

- Baseline before follow-up: 79 passed, 15 subtests passed.
- TDD checkpoints: final-aware loader/resolver 67 passed; exact ET aggregate 17 passed; schema/storage 27 passed plus Futures Market contracts 7 passed; integrated follow-up 108 passed, 15 subtests passed.
- Additive schema sync created and verified nine nullable columns: six `final_*`, `finalization_basis`, `final_source_ref`, `finalized_at`.
- Actual first run at 2026-07-23 19:53 ET: raw rows 4,284, failed symbols 0, finalization `finalized` 17/17, snapshot `materialized`, as-of 2026-07-23, fingerprint `8302d35b62aa0115704e1a9737972ca6639e67be4633518996f4b9d2245cc8e6`, total 75.645s.
- Actual stored evidence: 17 final rows, one shared exact EDT source window, non-null final close for every symbol, algorithm `pattern_outlook_v7_same_state_nested_hybrid_session_aggregate`, session status FINAL.
- Actual immediate rerun: finalization `reused`, snapshot `reused`, identical fingerprint, materialization 0s, total 8.659s.
- Browser QA: hero/command 기준일 2026-07-23, 관측 완료, pending disclosure absent, desktop console error 0. At 420px outer 420/420 and component 377/377 client/scroll width; both action buttons 160/160 and unclipped.
- Representative generated screenshot: `futures-macro-daily-finalization-qa.png` (untracked, not staged).
