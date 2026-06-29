# Overview Primary Tab Soft Remove V1 Risks

## Open Risks

- A later cleanup may be needed if unused `Futures Monitor` / `Sector / Industry` helper functions become misleading to maintainers.
- Market Context still contains evidence rows whose `근거 화면` strings name `Futures Monitor` or `Sector / Industry`. That is acceptable for this 1차 soft-remove, but 2차 should decide whether those labels should become `Market Context` evidence labels instead of old tab names.

## Follow-Up Candidates

- 2차: verify whether `Market Context` gives enough futures / sector evidence without standalone tabs.
- 3차: decide whether to physically remove or repurpose the hidden renderer functions.
