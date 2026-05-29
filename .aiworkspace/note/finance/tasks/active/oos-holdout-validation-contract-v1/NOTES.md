# OOS Holdout Validation Contract V1 Notes

Status: Complete
Created: 2026-05-29

## Notes

- OOS helper reuses the same monthly alignment helper as walk-forward validation.
- The helper intentionally does not persist raw split curves or user-facing memo state.
- Short shared history is `NEEDS_INPUT`, because split validation cannot be inferred from a tiny sample.
- Proxy-only portfolio / benchmark source downgrades to `REVIEW` even when numeric metrics pass.
- Benchmark parity not `PASS` also downgrades OOS source strength to `REVIEW`.
