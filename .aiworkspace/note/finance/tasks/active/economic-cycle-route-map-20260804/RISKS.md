# Risks

- Removing the quadrant means exact level/momentum geometry is no longer visible in the map;
  existing numeric metrics must remain prominent above it.
- Direction arc can be mistaken for a forecast unless `예측 아님` remains visible.
- Current-observed and anchor-based transition directions can differ; each reference basis must
  remain explicit.
- Asset checkpoint and ribbon regressions must be checked separately from route-map tests.

## Closeout Assessment

- Exact coordinate geometry is intentionally absent; users must read level/momentum from the observed-state card.
- Structural direction can still be misread if detached from its copy, so the visible `예측 아님` boundary remains part of the UI contract.
- Current observed direction and anchor-based transition detail may differ by design; both reference bases remain visible side by side.
- No open implementation or verification blocker remains.
