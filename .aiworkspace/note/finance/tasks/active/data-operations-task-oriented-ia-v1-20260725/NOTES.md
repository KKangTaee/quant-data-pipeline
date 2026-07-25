# Notes

## 2026-07-25 — Approved Direction

- User approved the recommended `Task-oriented Hybrid`.
- The UI should organize collection around consumer goals, not collector names.
- Backend actions are preserved unless a later implementation finding justifies explicit deletion.

## Product Decisions

- Streamlit remains appropriate for this internal operator surface in V1.
- No new raw status dashboard is added.
- No automatic multi-step execution is added.
- No scheduler or background worker is added.
- Raw logs / failure CSV / result JSON remain backend artifacts, not default product UI.
- History defaults to Data Operations actions and does not mix generic app jobs.

## Key Design Constraint

Moving an action to Advanced is not the same as deprecating its backend.
Compatibility actions remain replay-only and are not promoted to active execution.
