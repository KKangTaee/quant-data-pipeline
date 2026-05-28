# NOTES - Practical Validation V2

Status: Active
Last Updated: 2026-05-28

## P2 Closeout Notes

- P2 closeout 기준은 모든 ETF / provider 완전 지원이 아니라, actual / bridge / proxy / `NOT_RUN` origin을 명확히 표시하는 것이다.
- Service contract tests cover provider context provenance, stale provider downgrade, look-through board, robustness lab, Final Review evidence expansion, and selected-route gate handling.
- Provider-backed evidence remains compact in Practical Validation / Final Review JSONL rows.
- Full provider holdings, macro observations, and raw provider payloads stay in DB / loaders, not workflow registries.
- `NOT_RUN` remains a gap disclosure and can become a critical selected-route blocker when policy marks the domain critical.

## Residual Gaps

- P3 still needs a scoped decision before implementation.
- Strategy-specific sensitivity runtime sweeps remain outside P2 closeout.
- Provider source coverage remains partial by design; unsupported ETF / stale snapshot cases must keep `REVIEW` or `NOT_RUN` disclosure.
