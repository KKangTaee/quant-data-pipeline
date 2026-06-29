# Overview Data Health Ingestion Handoff V1 Notes

Status: Active
Created: 2026-06-08

## Notes

- 2차 should preserve the wording distinction between action guidance and action ownership.
- The existing `build_collection_ops_snapshot` already exposes `Area`, `Status`, `Data Freshness`, run-history fields, and `Next Action`.
- The handoff model should not introduce new collector names beyond existing targets.
- Priority order is `Failed > Missing > Stale > Partial > Due`; OK / Success rows are excluded from `priority_items`.
- Futures / sentiment / event rows point to `Workspace > Ingestion > 일상 운영 / 검증 데이터`; approved Overview bounded refresh surfaces are shown only as alternate surfaces.
- S&P 500 universe and intraday snapshot targets currently point to existing Overview bounded action facade surfaces because they are not exposed as standalone Ingestion console buttons.
