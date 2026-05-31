# Final Review Decision Cockpit V1 Notes

Status: Active
Created: 2026-05-31

## Initial Findings

- `Final Review` already has Investability Evidence Packet, profile-aware gate policy, selected-route save evaluation, and Decision Dossier export.
- The current screen order exposes many detailed tables before it gives a compact final-selection interpretation.
- The first slice should reorganize evidence into a candidate comparison board and a selected-candidate cockpit, not add new data collection or persistence.

## Implementation Notes

- `build_final_review_candidate_board_rows()` flattens existing source / validation / paper observation / packet evidence into a comparison table.
- `build_final_review_decision_cockpit()` summarizes selected-route state, suggested decision, blocker / review-required rows, and monitoring seed from the same gate policy used by save evaluation.
- Final Review reuses prebuilt selected candidate context so the UI and save preview read the same validation / packet evidence.
- Saved decision display copy now uses `판단 라벨` instead of `투자 가능성` to avoid implying live approval.
