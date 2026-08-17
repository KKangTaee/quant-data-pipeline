# Market Research Flat Navigation V1 Design

Approved design: `docs/superpowers/specs/2026-08-17-market-research-flat-navigation-design.md`

Approved mobile parity follow-up:
`docs/superpowers/specs/2026-08-17-market-research-mobile-desktop-parity-design.md`

The existing Python route/session boundary remains authoritative. `inflation-policy` becomes a canonical sibling view but reuses the DB-backed economic analysis transport with an explicit controlled selected view. The React workbench no longer owns a duplicate inner tab selection.

The follow-up keeps that information architecture intact and replaces the rejected mobile-only compact rail with the same family underline and view pill presentation used on desktop. Only navigation presentation is in scope; mobile header and research body responsiveness remain unchanged.
