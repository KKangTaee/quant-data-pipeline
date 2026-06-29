# Overview Market Context Brief Flow Redesign V1 Notes

## User Feedback Summary

- `오늘의 시장 맥락` and `시장 브리프` read as overlapping sections.
- Historical analog controls appear before `시장 브리프`, making users expect the brief to replay by selected as-of.
- `다음 맥락 체크` reads like guide cards instead of helping users understand the current market flow.
- Historical analog metadata is useful but visually unstructured.
- `Macro 조건 포함 pilot` looks like another nested card and does not clearly explain broad vs macro-conditioned differences.
- `근거: 자료 기준 / 출처 상태` has the right content but needs source-ledger structure and practical refresh action.
- `보조 갱신` is too detached and unclear.

## Design Judgment

The problem is not Streamlit itself and not a repository instruction that requires cards. The issue is that cards became the default visual container rather than a purposeful tool. This task limits cards to summaries / comparisons and uses rows, ledgers, chips, and callouts for reading flow.

## Implementation Notes

- `오늘의 시장 맥락` remains the top current-market summary; `시장 브리프` now follows as the read sequence rather than competing with historical controls.
- Historical analog controls now sit between the current brief flow and the analog section. The section explicitly says selected as-of / pattern changes apply only to historical analog.
- Historical analog basis metadata is grouped into `기준`, `패턴`, `표본`, `한계` ledger blocks.
- Macro conditioned pilot is rendered as `Broad vs Macro 조건 포함` with sample funnel and condition groups instead of a nested pilot card.
- Macro dimension audit renders all dimensions grouped by usage status; it no longer silently truncates at eight dimensions.
- Source confidence opens into a source ledger with `자료 영역`, `해석 영향`, `보강 위치`, followed by `필요 자료 보강`.
- Browser QA found a selected-control timing bug: after moving controls below the current brief, selected date/pattern could lag one render. The dashboard now reloads the supporting model after controls are rendered when controls changed.
