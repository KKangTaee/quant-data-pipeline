# Overview Market Context Brief Flow V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch: `codex/sub-dev`.
- Pre-existing dirty/generated files include `finance/.DS_Store` and prior QA screenshots; do not stage them.
- Current V3 source still promotes `다음 확인 순서` in the cockpit rail/rendered panel and renders an Overview Map / Deep Tab disclosure below the cockpit.

## Decisions

- Keep the `현재 맥락:` headline because it summarizes movement, leadership, and futures background well.
- Replace guide-style cards/panels with brief rows and interpretation cue rows.
- Keep Data Health as a small caveat and source-state disclosure, not as a front-and-center diagnostic panel.
- Remove the `Overview Map / Deep Tab` disclosure from the Market Context first tab; tab handoff information now appears as inline `확인 위치` metadata on each brief/cue row.
- Bump the Market Context cockpit cache schema key so fresh Streamlit sessions pick up the new brief-flow read model and source-state copy.
