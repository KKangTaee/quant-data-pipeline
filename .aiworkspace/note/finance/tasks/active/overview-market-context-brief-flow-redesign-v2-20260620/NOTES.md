# Overview Market Context Brief Flow Redesign V2 Notes

## User Feedback Captured

- The previous V1 result looked like cards were moved around, not redesigned.
- `다음 맥락 체크` still felt like guide cards rather than useful market reading.
- `시장 브리프` was not sufficiently improved or merged with `오늘의 시장 맥락`.
- `Macro 조건 포함 pilot` still looked nested, small, and hard to distinguish from broad analog.
- Other Overview surfaces already use wider, clearer Streamlit UI; Market Context should follow that standard.

## Implementation Notes

- Keep the top cockpit card because it acts as a primary market brief frame.
- Remove card-like backgrounds and left rules from the supporting reading sections.
- Move brief rows into the top cockpit so the user does not read a separate duplicated `시장 브리프` section.
- Use rail/list structure for next checks.
- Use `Macro 조건 포함 비교` as the visible title while keeping service model `macro_conditioned_analog` unchanged.
