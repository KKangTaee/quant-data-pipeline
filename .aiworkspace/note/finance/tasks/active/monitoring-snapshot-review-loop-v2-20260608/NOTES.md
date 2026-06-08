# Monitoring Snapshot / Review Loop V2 Notes

## Decisions

- Use the existing optional registry target `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl`.
- Keep `SELECTED_DASHBOARD_PORTFOLIOS.jsonl` as reusable portfolio setup only.
- Treat saved monitoring snapshots as explicit user review records, not live approval or order instructions.
- Keep implementation in existing Portfolio Monitoring runtime/UI boundary unless a small helper split is needed for feature ownership.

## Discoveries

- Current active phase/task is none according to docs and task manifest.
- Research refresh lists `Monitoring Snapshot / Review Loop V2` as the top current implementation candidate.
- Existing docs already define optional selected monitoring log as explicit-user-action only.
- Worktree has pre-existing modified saved JSONL and generated/local artifacts; these are not part of this task.
- Existing `portfolio_selection_v2.py` had monitoring log append/load functions, but they needed path injection and `recorded_at` sorting for focused tests and V2 snapshots.
- Portfolio Monitoring already had read-only recheck comparison, provider evidence, review signal policy, open issue follow-up, and drift helpers; V2 snapshots reuse these compact read models instead of embedding raw scenario artifacts.
- The UI save form builds provider/preflight evidence only on explicit submit. The current unsaved comparison uses session scenario metrics without auto-writing.
- Browser QA used an existing saved test portfolio and ran only the session scenario update. It did not create `SELECTED_PORTFOLIO_MONITORING_LOG.jsonl` because the explicit snapshot submit was intentionally not clicked.
