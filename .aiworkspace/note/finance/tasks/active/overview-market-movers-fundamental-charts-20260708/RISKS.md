# Risks

- 실제 DB에 과거 statement row가 적으면 일부 지표 탭은 빈 상태나 단일 막대로 보일 수 있다.
- Browser QA는 로컬 Streamlit/DB 상태에 의존한다. 2026-07-08 QA에서는 CTSH 기준 PER annual과 FCF quarterly bar rows가 보였다.
- 2026-07-08 후속 2에서는 in-app browser URL policy가 `localhost:8510` 접근을 차단해 새 screenshot QA를 만들지 못했다. 검증은 HTML contract tests, Market Movers focused tests, `py_compile`, `git diff --check`로 대체했다.
