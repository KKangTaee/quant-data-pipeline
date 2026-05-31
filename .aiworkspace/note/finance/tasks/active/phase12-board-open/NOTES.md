# Phase 12 Board Open Notes

Status: Complete
Created: 2026-05-29

## Notes

- Phase 12 is not a trading automation phase.
- The target surface is `Operations > Selected Portfolio Dashboard`.
- Existing dashboard evidence already covers readiness, freshness, provider context, timeline, review signals, comparison, and optional drift, but source ownership and severity policy need a fresh source map before implementation.
- The phase should preserve the user's storage preference: DB-backed evidence is acceptable when it improves validation, but memo / preset / automatic log storage should not expand.
- `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` remains optional and explicit-user-action only.

## Immediate Question For 12-1

Which current dashboard states can incorrectly look acceptable when evidence is stale, missing, failed, partial, or session-only?
