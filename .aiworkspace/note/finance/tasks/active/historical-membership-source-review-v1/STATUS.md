# Historical Membership Source Review V1 Status

Status: Complete
Created: 2026-05-28

## Checklist

- [x] Review official source candidates
- [x] Verify public current files are reachable
- [x] Separate subscription source from free-source path
- [x] Recommend next Phase 8 implementation slice
- [x] Sync phase / roadmap / logs

## Result

The next implementation should be `symbol-directory-snapshot-ingestion-v1`.

It should ingest Nasdaq public current symbol directory files as DB lifecycle `listing_observed` partial evidence.
This does not solve complete historical membership by itself, but it is the correct free / official foundation before computed snapshot evidence or paid corporate action feeds.
