# Overview Primary Tab Soft Remove V1 Design

## Current Structure

- `app/web/overview_dashboard.py` owns the Overview primary selector through `OVERVIEW_DEEP_TAB_OPTIONS`.
- `render_overview_dashboard()` dispatches selected labels to tab renderers lazily.
- `app/web/overview_dashboard_helpers.py` contains the IA closeout guide listing owning deep tabs.
- Durable docs currently still describe `Futures Monitor` and `Sector / Industry` as primary Overview tabs.

## Implementation Direction

1. Update contract tests first so the intended primary selector contains only:
   - `Market Context`
   - `Market Movers`
   - `Sentiment`
   - `Events`
2. Keep the old renderer functions in code for now, but remove them from primary dispatch. This is a soft-remove, not physical deletion.
3. Make removed labels fallback through existing `_overview_active_tab_label()` behavior by excluding them from `OVERVIEW_DEEP_TAB_OPTIONS`.
4. Update IA guide and durable docs to say futures / sector evidence remains absorbed under `Market Context` rather than exposed as standalone primary tabs.

## User Flow After Change

The user opens `Workspace > Overview` and chooses among a smaller set of decision surfaces. Futures/macro and sector pressure remain part of `Market Context` evidence, but the user is not asked to maintain separate tabs whose product question is unclear.

## Tradeoff

Leaving helper functions in place keeps the removal low-risk and reversible. The cost is some unused UI code until a later cleanup confirms whether those surfaces should be deleted or repurposed.
