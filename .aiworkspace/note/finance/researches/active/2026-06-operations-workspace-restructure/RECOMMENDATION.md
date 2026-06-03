# Recommendation

## One-Line Recommendation

Keep `Selected Portfolio Dashboard` under `Operations`, but restructure Operations so it reads as an operating console with clear lanes: `Portfolio Monitoring`, `System/Data Health`, `Archive/Recovery`, and eventually `Reports`.

## Why This Direction

The current placement is conceptually right. A selected portfolio is no longer in the "build/test a strategy" phase; it is in the "observe, recheck, compare, and decide whether review is needed" phase. That belongs outside `Workspace > Backtest`.

The problem is not location. The problem is hierarchy. `Ops Review`, `Selected Portfolio Dashboard`, `Backtest Run History`, and `Candidate Library` are presented as peers, but only two are real primary Operations surfaces:

- `Selected Portfolio Dashboard`: user-facing portfolio monitoring.
- `Ops Review`: system/data/run health.

The other two should remain, but as secondary archive/recovery tools:

- `Backtest Run History`: reproduce old backtest runs, restore forms, resend to validation.
- `Candidate Library`: inspect saved current/pre-live candidates and rebuild result curves.

Do not delete legacy tools yet. They carry audit, reproducibility, and migration value. Instead, demote them visually and semantically.

## Recommended 1st Build Scope

### Step 1. Label The Operating Model

- Treat `Workspace` as "build and validate".
- Treat `Operations` as "monitor selected outcomes and system health".
- Treat `Reference` as "explain meaning and workflow".
- Keep Selected Dashboard in Operations.
- Add copy/guidance that Run History and Candidate Library are archive/recovery, not primary candidate selection stages.

### Step 2. Add Operations Overview

- Create one landing surface that answers "what should I check now?"
- Show lanes for Portfolio Monitoring, System/Data Health, Archive/Recovery, and Reference/Reports.
- Put Selected Portfolio Dashboard as the first Portfolio Monitoring action.
- Put Backtest Run History and Candidate Library under Archive/Recovery.
- Do not delete pages in the first slice.
- Do not change registry/saved schemas.

## Recommended Next Phase After 1st Build

| Phase | Output | Why |
| --- | --- | --- |
| Portfolio Monitoring V2 | Stronger Selected Dashboard status cockpit | Makes the correct primary Operations surface more useful. |
| Archive Demotion | Navigation or Overview cards lower Run History / Candidate Library prominence | Preserves legacy replay while reducing workflow confusion. |
| Data/System Health Alignment | Better bridge between Ops Review and Ingestion health | Clarifies where to inspect vs where to execute collection. |
| Report Export | Manual selected portfolio monitoring snapshots | Adds durable human-readable operations output after semantics stabilize. |

## What Not To Do Yet

- Do not move Selected Dashboard back to Workspace/Backtest.
- Do not delete Backtest Run History or Candidate Library immediately.
- Do not add broker/account/order/auto-rebalance behavior.
- Do not rewrite registries or saved setup.
- Do not begin with a full React/API migration.

## Decision Rules

Proceed when:

- The user agrees Operations should remain the post-selection + system-health area.
- The user agrees Run History and Candidate Library should be kept but demoted.
- The first implementation is limited to IA/read-model/UI copy, not data schema or live-trading scope.

## Final Recommendation

Approve a narrow `Operations Overview / IA V1` design task before implementation.

The first implementation should not remove pages. It should make the current system legible:

```text
Operations = Portfolio Monitoring + System/Data Health + Archive/Recovery
```

After that lands and feels right, run a second pass on Selected Dashboard monitoring summaries and a third pass on archive demotion. This keeps useful legacy tools available while shifting the user's center of gravity from "old backtest artifacts" to "selected portfolio operations".
