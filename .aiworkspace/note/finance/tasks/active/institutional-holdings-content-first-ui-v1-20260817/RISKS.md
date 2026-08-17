# Institutional Holdings Content-First UI V1 Risks

State: complete
Last Updated: 2026-08-17

## Resolved Risks

- manager result list can be long; the picker must bound its own height without reintroducing a
  page-height rail.
- horizontal research tabs must remain discoverable at 420px while preventing page overflow.
- tracked production component assets can drift from source if build verification is skipped.
- pending selection must preserve the current body without making a stale manager label appear to
  belong to the incoming CIK.

All four risks were covered by source/runtime tests and actual desktop/mobile Browser QA.

## Blockers

- None.
