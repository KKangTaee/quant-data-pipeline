# Overview Market Context Section Flow V1 Design

Status: Active
Created: 2026-06-15

## Current Structure

`Workspace > Overview > Market Context` currently renders a page heading and one `.ov-macro-cockpit` surface. Inside that single surface are headline, 5-cell tape, sector pressure map, event timeline, market brief, interpretation cues, historical analog, source confidence, and boundary copy.

## Target Structure

```text
Market Context page
-> top dashboard: headline, tape, sector pressure map, event timeline
-> reading flow: market brief
-> reading flow: interpretation variables
-> reading flow: historical analog reference
-> reading flow: source confidence / boundary
```

## Design Direction

- Do not create nested cards.
- Use full-width section bands with stronger section titles and left accent rails.
- Keep the top dashboard visually compact.
- Make `시장 브리프` read like the primary explanation section, with larger value/detail text and clearer numbered rows.
- Keep `해석할 때 같이 볼 변수` and `과거 유사 맥락 참고` visually secondary but no longer buried inside the top cockpit.

## Boundaries

The UI remains context-only. This change does not create predictions, investment recommendations, validation gates, Final Review decisions, monitoring signals, broker orders, auto rebalance, registry writes, saved setup writes, provider fetches, or DB schema changes.
