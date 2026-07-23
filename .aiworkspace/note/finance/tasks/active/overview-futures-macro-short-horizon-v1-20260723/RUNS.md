# Overview Futures Macro Short-Horizon V1 Runs

Last Updated: 2026-07-23

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

## Pending

- Spec-only diff check and commit
- Implementation commands after written-spec approval

## Spec self-review

- Placeholder scan: no `TBD`, `TODO`, or incomplete requirement remains.
- Consistency: retained 60D regime history as secondary content instead of inferring deletion from the approved primary mockup.
- Scope: kept family/model formulas, DXY/silver membership, DB schema, and backend 20D history out of the implementation change.
- Ambiguity: fixed routine overlap to `1y/1d` and defined unchanged-input fingerprint fields and rebuild conditions.
