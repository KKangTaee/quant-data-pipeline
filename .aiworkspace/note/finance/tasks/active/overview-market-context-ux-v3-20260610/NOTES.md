# Overview Market Context UX V3 Notes

## Intake Notes

- Current branch/worktree: `codex/sub-dev` in `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Existing untracked QA screenshots and `finance/.DS_Store` are present before this task and should not be staged.
- Existing Market Context V1/V2 made the tab first and added summary rail, but code still contains user-visible English/technical copy such as `Overview Macro Context`, `Source Confidence`, `Freshness`, `Source REVIEW`, `Data Health N개`, `in N days`, and a primary refresh button before the cockpit.

## Decisions

- Treat the user's requested 1차~4차 as approved design scope.
- Keep refresh available but render it after the cockpit/IA guide as a secondary maintenance action.
- Do not add a new job-result or raw status diagnostic panel.
- The `현재 맥락` headline should summarize market movement / breadth / futures backdrop, while `자료 상태` separately explains whether stale/partial/missing data needs attention.
- Direct `/overview` first-load still triggers Streamlit's own Page not found modal even though Overview renders afterward. A minimal `default=True` toggle was tested and did not resolve the modal, so this should be handled as a broader Streamlit routing/navigation follow-up instead of hiding the dialog in this UX task.
