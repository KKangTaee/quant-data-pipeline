# Monitoring Snapshot / Review Loop V2 Risks

## Open Risks

- Portfolio Monitoring UI/runtime files are large; feature-scoped helper extraction may be needed if the save/review loop becomes hard to follow.
- Pre-existing saved setup JSONL modification must not be overwritten or staged unless the user explicitly asks.
- Current snapshot comparison focuses on compact portfolio metrics. Provider freshness and preflight are fully captured on explicit save, but not recomputed on every render to avoid heavy DB reads.
- The local Streamlit executable script has a stale shebang to another worktree venv. Use `.venv/bin/python -m streamlit ...` for this worktree until the venv script is regenerated.

## Boundary Risks

- Snapshot rows must not include full holdings, full macro series, raw provider responses, broker/account details, or order instructions.
- Scenario replay success must not auto-write monitoring records.
- Review signal / drift copy must remain monitoring evidence, not investment advice or live deployment approval.
