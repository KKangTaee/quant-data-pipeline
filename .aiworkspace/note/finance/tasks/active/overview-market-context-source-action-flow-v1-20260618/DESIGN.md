# Design

Status: Complete
Last Updated: 2026-06-18

## Implementation Direction

`Overview > Market Context` stays a DB-backed context surface. The change does not add providers, schema, loaders, registry writes, validation gates, monitoring signals, or trading semantics.

## 1차 Implemented

- Service read model:
  - `build_overview_macro_context_cockpit()` now builds `data_health_handoff` from the existing collection ops snapshot.
  - `next_checks` is the user-facing checklist read model and carries `target_tab`, `title`, `reason`, `action`, `source_area`, `freshness`, `priority`, status, and tone.
  - Events review copy separates estimate, stale estimate, unconfirmed earnings, and official macro/source freshness cases.
  - Data Health collection actions are normalized into user-facing Korean action copy.
- UI renderer:
  - `다음 맥락 체크` renders `model["next_checks"]`; `interpretation_cues` remains a compatibility field only.
  - Source Confidence footer summary shows review source/action chips before expansion.
  - Historical analog meta shows `current_as_of`, `data_window`, and calculation note.
- Refresh assist:
  - `보조 갱신` remains collapsed and secondary.
  - The expander first explains which source/action motivated the refresh; raw job result rows stay inside the existing collapsed result expander.

## 2차 Follow-Up Design Note

Historical analog expansion should first design a current pattern window contract before implementation.

- Candidate windows: 5D, 20D, monthly.
- Required decision: whether replay should use stored DB snapshots only or introduce a new approved as-of storage/read path.
- Do not implement until PIT/replay boundary and storage policy are approved.

## 3차 Follow-Up Design Note

Macro-conditioned analog should remain a distribution/context pilot, not a signal.

- Candidate context inputs: sector ETF relative strength, 2Y/10Y or yield curve, gold/GLD, futures macro thermometer, events/sentiment context.
- Existing median / positive-rate / best / worst distribution table should remain.
- Required copy boundary: describe historical distributions only; do not use prediction, recommendation, buy/sell, or signal language.
