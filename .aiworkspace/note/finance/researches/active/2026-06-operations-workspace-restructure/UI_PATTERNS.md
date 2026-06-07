# UI And Workflow Patterns

## Product Goal

Make `Operations` read as an operating console rather than a drawer of unrelated legacy tools.

## Pattern 1. Stage Separation

- `Workspace` should mean build, research, validate, and decide.
- `Operations` should mean monitor selected outcomes, system/data health, and recovery tools.
- `Reference` should mean explanations and durable workflow guide.

## Pattern 2. Operations Overview Before Detail

- Add a command-center style landing surface.
- Show "what needs attention now" before exposing logs, JSON, raw registries, or old run artifacts.
- Put cross-links to existing screens rather than moving all logic at once.

## Pattern 3. Portfolio Monitoring First

- Selected portfolios, open review items, stale scenarios, next rebalance review, and benchmark/risk changes are first-class operations information.
- Actual allocation and drift remain optional/manual evidence.
- Rebalance targets stay read-only review data, not order instructions.

## Pattern 4. Archive / Recovery Lane

- Backtest Run History and Candidate Library should remain available.
- Their page copy should say "reproduce, restore, recover, inspect".
- They should not look like the normal path for creating selected candidates.

## Pattern 5. System / Data Health Lane

- Ops Review and Ingestion data health are related but not identical.
- Operations should show system health status, then route to Ingestion for data collection actions.

## Pattern Conflicts With Current Boundaries

| Pattern | Conflict | Handling |
| --- | --- | --- |
| Broker-style portfolio operations | Could imply live approval, orders, account sync, auto rebalance. | Keep no-live boundary visible; do not add execution actions. |
| Automated scenario refresh / monitoring logs | Could look like scheduler-owned monitoring. | Keep explicit manual run/save semantics unless separately approved. |
| Deep navigation nesting | Streamlit top navigation may not support desired IA cleanly. | Add Operations Overview first; keep existing routes. |
| Delete legacy tools | Could lose audit/replay capability. | Demote before delete; measure usage or create replacement archive first. |

## Product-Specific Pattern Proposal

```text
Operations
  Overview / Command Center
    - Portfolio monitoring status
    - System/data health status
    - Open review items
    - Where to go next
  Portfolio Monitoring
    - Selected Portfolio Dashboard
    - Actual allocation / drift evidence
    - Rebalance target review
    - Decision dossier / monitoring timeline
  System & Data Health
    - Ops Review
    - Ingestion freshness summary
    - Run failures / logs / artifacts
  Archive & Recovery
    - Backtest Run History
    - Candidate Library
    - Legacy Pre-Live / proposal inspector where needed
  Reports
    - Future selected portfolio report export
    - Future monitoring review snapshots
```

## 2026-06-07 Pattern Update

Because `Operations Overview` and archive labels already exist, the next pattern is not "add a hub" but "turn the hub into the operating cockpit."

```text
Operations
  Portfolio Monitoring Cockpit
    - Current selected portfolio state
    - Stale / missing / blocked monitoring status
    - Review signal and open issue count
    - Target snapshot and optional actual allocation / drift evidence
  Evidence Health
    - DB / ingestion freshness relevant to monitoring
    - Latest run health
    - Provider / symbol freshness warnings
  Recovery Drawer
    - Backtest run restore
    - Candidate snapshot replay
    - Legacy registry bridge until retired
  Reports / Dossier
    - Manual monitoring review snapshot
    - Decision dossier handoff
```

### UI Direction

- Put portfolio monitoring status above development history, surface audit, and archive metrics.
- Keep `System / Data Health` visible, but make it the answer to "can I trust today's evidence?" rather than a generic ops log page.
- Move implementation history such as completed 1차~5차 roadmap out of the main user path. If retained, keep it in docs or a low-priority reference expander.
- Treat archive pages as recovery drawers. They can remain in top navigation for Streamlit constraints, but the page copy and Overview links should make them feel secondary.
- Do not create a new standalone `Operations` tab unless it clarifies one of the three user questions: portfolio state, evidence health, or recovery.
