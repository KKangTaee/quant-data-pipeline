# Risks

## Residual

- `context_findings` and `next_checks` remain in the service payload for compatibility, so future UI work should not re-enable them as a default action checklist.
- `근거: 자료 기준 / 출처 상태` still contains lower-level source wording and may need a later copy polish pass, but it is intentionally a collapsed evidence footer rather than the main brief.

## Not Changed

- No hard conditioning was added to historical analog.
- No new data collection path or provider fetch was added.
- No validation, monitoring, or trading semantics were added.
