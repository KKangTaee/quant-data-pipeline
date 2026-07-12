# Status

## 2026-07-10

- Started after user approved removing `Step 1 / Candidate Board` as a separate Final Review section.
- Current scope: integrate candidate review queue / target selector / detail into the Decision Desk first-read area, and remove duplicate 4-card Candidate Board summary.

## Current Step

- Implementation, documentation sync, QA, and commit preparation completed.

## Completed Scope

- Added a source contract test that fails while `Step 1 / Candidate Board` and duplicate lane cards remain.
- Replaced the standalone Candidate Board renderer with a compact candidate selection panel.
- Removed numbered `Step` eyebrows from the active Final Review path and changed section markers to role-based labels.
- Durable docs now describe Final Review candidate selection as Decision Desk-integrated, not a separate Step 1.
- Browser QA confirmed `후보 현황과 다음 판단`, `Review Queue`, `검토 대상`, `후보 비교 상세`, and `Final Review 투자 검토서` render together while `Step 1`, `Candidate Board`, and Final Review market sentiment panel copy are absent.

## Next

- Commit the scoped code / docs / tests change. Generated QA screenshot stays untracked.
