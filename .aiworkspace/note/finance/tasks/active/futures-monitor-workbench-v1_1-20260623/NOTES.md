# Futures Monitor Workbench V1.1 Notes

## Decisions

- Treat the user request as approved scope for implementation; no separate UX approval gate is needed inside the specified boundaries.
- Use service / helper contracts for TDD because full Streamlit rendering is not practical in unit tests.
- Keep refresh actions explicit and user-triggered; the UI can group them, but must not fetch providers while rendering.
- Preserve raw tables as collapsed source material rather than removing them.
- Context bar `다음 행동` reports state only (`갱신 필요`, `자료 양호`, `확인 필요`) and no longer repeats the refresh button label.
- The refresh module owns actual actions: `1분봉 갱신`, `일봉 매크로 갱신`, `화면 다시 읽기`, plus compact 확인 방식.
- Historical validation summary is current-scenario-first and explicitly says mixed scenarios should not be read as directional hit-rate.

## Observations

- V1 already introduced helper seams for context bar, market brief, weekly flow, and watch strip.
- Remaining prototype-like areas are lower evidence wording, table-first validation, split refresh controls, and repeated refresh/stale phrases.
- Browser QA confirmed old phrases `근거를 어떻게 읽을까`, `갱신 설정`, `선택 선물 1분봉 갱신`, and `일봉 매크로 데이터 갱신` are absent from the rendered Futures Monitor surface.
