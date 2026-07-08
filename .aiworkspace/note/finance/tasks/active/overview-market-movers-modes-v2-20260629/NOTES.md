# Overview Market Movers Modes V2 Notes

- `mover_views` intentionally keeps `rows` and `volume_rows` compatibility fields unchanged for old callers.
- `Unusual Volume` is context-only. It is relative volume evidence, not a breakout prediction or trading signal.
- If 10-day volume baseline rows are unavailable, the view returns `INSUFFICIENT_DATA` with an explanation rather than inventing a value.
- `Sector Leaders` reuses existing group leadership row shape. A fuller sector/heatmap/breadth UX remains 4차 scope.
- Why It Moved is still a manual investigation start point in 2차. Full selected-symbol detail integration remains 3차 scope.
