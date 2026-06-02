# Status

## 2026-06-01

- Started after user approved tightening the workflow gate.
- Found mismatch: Practical Validation module gate allowed `REVIEW` modules to move, while Final Review selected-route policy can still block selected storage for selection-critical evidence gaps.
- Added `app/services/backtest_selected_route_preflight.py` and connected it to Practical Validation result generation.
- `Selected-route Preflight` is now a required Practical Validation module. If Final Review selection policy outcome is `blocked` or `hold_or_re_review`, the Practical Validation `final_review_gate.can_save_and_move` becomes `False`.
- Final Review source picker now re-runs the same selected-route preflight for legacy Practical Validation rows that do not yet store `selected_route_preflight`, so old `READY_WITH_REVIEW` rows with selected-route gaps are hidden.
- Browser QA confirmed the existing two Practical Validation rows are hidden and Final Review shows no candidates.
