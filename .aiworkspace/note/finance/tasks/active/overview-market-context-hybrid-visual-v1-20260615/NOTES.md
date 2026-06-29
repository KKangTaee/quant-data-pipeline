# Overview Market Context Hybrid Visual V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch: `codex/sub-dev`.
- Prior implementation commit: `dde4a78c Overview 시장맥락 카드리스 브리프 정리`.
- Pre-existing generated/local files include `.DS_Store`, `.superpowers/`, and prior QA screenshots; do not stage them unless explicitly requested.

## Design Notes

- The approved direction is not card-first.
- Reuse existing helpers:
  - `build_overview_breadth_heatmap_summary()` for sector pressure rows.
  - `build_overview_macro_week_lane()` for recent/upcoming event timeline rows.
- The first pass should be visually stronger but still conservative in semantics.
- The cockpit summary rail now intentionally behaves like a market tape: `자료 상태`, `Top Mover`, `Breadth`, `Macro`, `Next Event`.
- The board avoids nested cards by using a single cockpit surface, row-like tape cells, a heatmap-style sector grid, and a timeline list.
- Event timeline generation now accepts either internal event `Type` codes or user-facing `Type Label` values such as `CPI` / `FOMC`.
