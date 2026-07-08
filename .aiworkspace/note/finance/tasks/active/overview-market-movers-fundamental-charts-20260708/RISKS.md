# Risks

- 실제 DB에 과거 statement row가 적으면 일부 지표 탭은 빈 상태나 단일 막대로 보일 수 있다.
- Browser QA는 로컬 Streamlit/DB 상태에 의존한다. 2026-07-08 QA에서는 CTSH 기준 PER annual과 FCF quarterly bar rows가 보였다.
- 2026-07-08 후속 2에서는 in-app browser URL policy가 `localhost:8510` 접근을 차단해 새 screenshot QA를 만들지 못했다. 검증은 HTML contract tests, Market Movers focused tests, `py_compile`, `git diff --check`로 대체했다.
- 후속 3 역시 live Browser QA 대신 static preview로 시각 확인했다. 실제 Streamlit theme / browser rendering은 사용자가 앱에서 최종 육안 확인해야 한다.
- 후속 4도 live Browser QA는 동일 제한으로 수행하지 못했다. 좌우 row layout은 좁은 화면에서 CSS media rule로 stack되며, 실제 앱에서는 Streamlit container 폭에 따라 각 패널 내부 horizontal scroll이 필요할 수 있다.
- 후속 5는 CSS contract test로 scroll containment를 검증했다. live Browser QA 제한은 동일하므로 실제 앱에서 분기 그래프가 각 패널 내부에서 좌우 스크롤되는지 사용자가 최종 확인해야 한다.
