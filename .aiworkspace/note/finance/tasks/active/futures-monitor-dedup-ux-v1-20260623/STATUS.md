# Futures Monitor Dedup UX V1 Status

## 2026-06-23

- User approved proceeding with the deduplication UX cleanup for `Workspace > Overview > Futures Monitor`.
- Scope: reduce duplicate default-surface information and preserve the V3 read-only context boundary.
- Added RED/GREEN contracts for command center ownership, live chart summary ownership, and Macro support strip ownership.
- Implemented command center summary items so provider run rows / latest candle details stay out of the default surface.
- Removed the old Live Chart status-card strip and kept Live Chart focused on chart context plus symbol-level state.
- Removed Macro scenario duplication from the support strip; the hero owns the scenario and support cards own confidence / validation facts.
- Shortened Macro confidence card values so `근거 강도 / 낮음` does not repeat `근거 강도` in the value.
- Browser QA passed on `http://localhost:8503`; screenshot saved as `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev/futures-monitor-dedup-ux-v1-qa.png` and kept as generated artifact.
- Existing unrelated dirty artifacts remain out of scope: `finance/.DS_Store`, `.superpowers/`, generated QA screenshots.
