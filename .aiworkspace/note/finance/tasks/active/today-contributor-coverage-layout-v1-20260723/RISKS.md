# Today Contributor Coverage / Review Layout V1 Risks

## Resolved Risks

- Valid rows are no longer silently omitted by a top/bottom slice.
- Partial live overlay coverage uses `기여 계산 N/M개` instead of claiming full coverage.
- Equal-height panels remain visually paired while review rows align to the top with measured 8px gaps.

## Remaining Observation

- The actual QA portfolio had five active items. The product allows up to ten, so a ten-item group will intentionally make the contributor panel taller and require more vertical scrolling; no hidden collapse is introduced.
