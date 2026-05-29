# Recheck Comparison Review Signal Policy V1 Risks

Status: Active
Created: 2026-05-29

## Risks

- Review Signals and Recheck Comparison can drift if thresholds remain duplicated.
- DB / provider data gaps can look less important if signal board only shows performance deltas.
- Session-state recheck evidence can be mistaken for durable monitoring history.

## Mitigation

- Make Recheck Comparison the only owner of performance deterioration threshold rows.
- Include preflight and provider routes in Review Signal Policy.
- Keep execution boundary read-only and no auto monitoring log write.
