# Notes

- This task should keep Overview render DB-only. Any remote refresh stays behind ingestion job wrappers.
- No DB schema change is planned; status can be derived from the existing snapshot coverage payload.
- Daily refresh state is derived in `app/services/overview_market_intelligence.py` so the UI only renders the read model.
- A stale daily snapshot is shown as refresh due, not as a data corruption signal.
