# Practical Validation Required Module Polish V1 Risks

Status: Implementation complete
Created: 2026-05-30

## Risks

- Renaming the displayed benchmark module could drift from existing `Benchmark parity` check keys if not documented.
- More gate columns can make the module board dense.

## Mitigation

- Preserve internal check keys and only expand the user-facing label.
- Keep row additions concise: `Gate Effect` and `Gate Reason`.

## Remaining

- The module board has more columns now. If operators find it visually dense, the next polish should hide `Gate Reason` behind an expander or show only blocker / review rows by default.
