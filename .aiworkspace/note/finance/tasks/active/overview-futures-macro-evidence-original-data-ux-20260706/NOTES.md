# Futures Macro Evidence / Original Data UX Notes

## 2026-07-06

- Existing React workbench already owns command strip, brief, scores, 1W / 1M flow, validation state, and evidence drawer.
- Existing lower expander still uses `근거 해석 / 원본 데이터`, repeats current evidence framing when React is available, then shows historical validation summary, data management, and raw tables.
- User concern is not lack of a guide. The target is to make the information itself carry enough context: what the row/section is, what it says, and how it connects to current interpretation.
- Phase 2 wording decision: avoid treating occurrence count as a signal. Use `비슷한 과거 상태` for historical frequency and explicitly say whether 5D directional consistency is applicable.
- Phase 3 raw table decision: preserve every dataframe, but rename disclosures around calculation steps so the user can connect current score, score contributors, actual daily moves, and historical sample tables.
