# Design

## Problem

Flow 3 currently has three competing summary layers:

- Python control center with numbered source/profile/replay/readiness cards
- Python alert + badge strip with the same conclusion
- React Fix Queue with conclusion, metrics, fix queue, and evidence groups

This makes the first-read question unclear: `Can this move to Final Review, and what should be fixed first?`

## Direction

- Keep the five-flow page structure.
- Remove the Flow 3-specific control center call from `page.py`.
- Let `workspace_panel.py` be the only Flow 3 first-read owner.
- Remove separate alert / badge strip from the workspace panel when the React component is available.
- Keep Streamlit fallback concise for environments without the React build.
- Keep detailed module / technical gates behind the existing expander.

## UI Shape

The main Flow 3 React surface should read:

```text
Final Review 이동 판단
[status] verdict
next action

먼저 해결할 일
- top blocking items, max 3 visible

근거 요약
- core evidence groups as compact rows
```

Metric counts can remain as compact context, but they should not be the dominant visual hierarchy.

## Files

- `app/web/backtest_practical_validation/page.py`
- `app/web/backtest_practical_validation/workspace_panel.py`
- `app/web/components/practical_validation_fix_queue/frontend/src/PracticalValidationFixQueue.tsx`
- `app/web/components/practical_validation_fix_queue/frontend/src/style.css`
- generated React build assets
- focused boundary / contract tests
