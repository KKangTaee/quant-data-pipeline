# Today Contributor Coverage / Review Layout V1 Notes

## 2026-07-23 Decisions

- Completeness is preferred over a hidden expand interaction.
- Existing contributor cards, metric meanings, and detail-panel two-column structure remain.
- Contributor ordering is absolute portfolio impact, not signed descending value.
- Missing contribution data is disclosed through coverage copy and is never coerced to zero.

## 2026-07-23 Implementation Result

- The missing-stock symptom was a presentation projection bug, not absent prices or contribution calculations: the old positive top-2 / negative bottom-2 policy silently discarded valid rows.
- EOD and live contributors now share one tone and deterministic ordering policy.
- Coverage copy is derived from displayed contributor count versus `active_item_count`, so partial live quote availability remains explicit.
- Equal outer panel height remains; only review content's inner grid is top-aligned and compacted.
