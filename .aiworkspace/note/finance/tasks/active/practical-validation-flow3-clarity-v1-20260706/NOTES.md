# Notes

## 2026-07-06 - Initial Assessment

- User confirmed Flow 3 should show whether Final Review movement is possible and then the validation conclusion / first fix work.
- Screenshot showed repeated source/profile/replay/readiness numbering, repeated `2차 검증 결론`, repeated blocked state, and large metrics before the actual work queue.
- The fix should not change gate semantics. It should change information architecture and visual hierarchy only.

## 2026-07-06 - Design Decision

Flow 3 will use the workspace read model as the single first-read owner:

- `page.py` keeps the Flow 3 section boundary and technical expander.
- `workspace_panel.py` owns the final-review readiness surface.
- The React component shows conclusion + top fix queue + compact evidence summary.

## 2026-07-06 - Implementation Note

Flow 3 no longer renders the Python validation control center before the workspace panel. The React Fix Queue is now the first-read surface:

- `Final Review 이동 판단`
- compact counts for first fixes / Final Review review items / evidence groups
- max 3 visible fix items
- compact core evidence summary

Detailed module rows remain available through the existing technical detail expander and Flow 4 evidence workbench.
