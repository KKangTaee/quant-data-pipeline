# Notes

## 2026-08-04 Decisions

- Replace the four-quadrant checkpoint chart with the selected Cycle Route option.
- Keep current phase and adjacent structural direction as the map's only primary jobs.
- Replace plotted checkpoints with one compact history sentence.
- Keep exact level/momentum in the existing current-observed card.
- Keep monthly detail in the existing 12-month ribbon.
- Preserve the transition panel and asset checkpoint surface.
- Unknown runtime transition statuses fail closed and do not render a directional arc.
- CONFIRMED uses the solid anchor-to-target arc without applying WATCH-only next-node styling to the current target.

## Closeout

- The route map is a structural reading aid, not a coordinate projection or forecast probability display.
- Exact level and momentum remain in the existing `현재 관측 국면` metrics rather than the route geometry.
- `MarketImplicationCard`, asset copy/order/CSS, and ribbon implementation have no scoped diff.
- Canonical doc change 없음: product promise, ownership boundary, data contract, and workflow priority did not change.
