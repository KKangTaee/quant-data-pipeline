# Overview Market Context Cardless Brief Layout V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch: `codex/sub-dev`.
- Base commit before this task: `215c0434 Overview 과거 유사 맥락 MVP 추가`.
- Pre-existing dirty/generated files include `finance/.DS_Store` and old `*-qa.png`; do not stage them.

## Design Decisions

- The issue is not Streamlit capability. Streamlit can render compact rows, tables, expanders, metrics, and custom HTML/CSS.
- The current problem is product/UI structure: too many visual containers with similar weight.
- Keep calculations and read model semantics stable; reduce visual weight and nesting in the renderer.
- Favor dense row/list scan patterns over repeated card grids.
- The outer Market Context cockpit remains a single brief surface, but internal sections no longer use nested card grids.
- Source Confidence stays as a collapsed disclosure so data provenance is available without dominating the primary market read.
- Historical analog still exposes insufficient-data limitations; only the empty-state chrome changed from card to note row.
