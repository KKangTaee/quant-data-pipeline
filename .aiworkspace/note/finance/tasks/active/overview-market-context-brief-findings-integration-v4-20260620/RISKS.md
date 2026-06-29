# Risks

## Residual

- `context_findings` and `next_checks` remain in the service payload for compatibility, so future UI work should not re-enable them as a default action checklist.
- Events / data caveat rows can become text-heavy when source evidence is long. Current renderer caps the brief at five rows and keeps evidence in compact badges, but future copy polish may still be useful.

## Not Changed

- No hard conditioning was added to historical analog.
- No new data collection path or provider fetch was added.
- No validation, monitoring, or trading semantics were added.
