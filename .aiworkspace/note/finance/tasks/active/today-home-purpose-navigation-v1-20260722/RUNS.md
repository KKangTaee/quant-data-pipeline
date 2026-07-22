# Runs

- 2026-07-22: finance docs INDEX/ROADMAP/PROJECT_MAP, approved research recommendation, app shell, Overview component token, Portfolio Monitoring read-model boundaries 확인.
- 2026-07-22: actual DB read-only smoke로 Economic Cycle LIMITED, S&P 500 READY, Futures Macro MISSING, Sentiment OK, Events 1 upcoming, default portfolio READY payload 확인.
- 2026-07-22: TDD RED — Today service import 4 failures, renderer missing 2 failures, old navigation contract 5 failures를 순서대로 확인했다.
- 2026-07-22: header as-of가 future event `2026-07-29`를 선택하던 회귀를 failing test로 재현하고 저장 evidence/portfolio date만 사용하도록 수정했다.
- 2026-07-22: focused regression `109 passed, 67 subtests`, navigation service contract `1 passed`, target `py_compile`, `git diff --check`를 통과했다. 표시된 3개 warning은 edgar package deprecation이다.
- 2026-07-22: 독립 리뷰에서 Operations loader의 `ensure_default_group` write 가능성, session-selected group drift, partial 과대 집계, storage failure `EMPTY` 오분류를 발견했다. 신규 5개 failing test로 모두 재현했다.
- 2026-07-22: 전용 read-only default-group builder, `default_only` projection, exact READY/available 분리, storage failure `UNAVAILABLE` 정책을 구현했다. Today tests `15 passed`, focused regression `113 passed, 67 subtests`를 통과했다.
- 2026-07-22: 재리뷰에서 S&P `INSUFFICIENT_HISTORY` no-value 상태의 READY 오분류를 재현하고 `UNAVAILABLE`로 수정했다. 최종 독립 재리뷰는 Critical/Important issue 0, merge ready로 판정했다.
- 2026-07-22: 마지막 수정 뒤 최종 focused regression `130 passed, 67 subtests`, navigation service contract `1 passed`, 5개 target `py_compile`, `git diff --check`를 통과했다.
- 2026-07-22: actual Browser root `/`에서 `3/5 READY · 5/5 available` partial Today와 default group `디폴트`를 확인했다. desktop 1280, 760px, 420px 모두 horizontal overflow 0이며 clean session console error/warning 0이다.
- 2026-07-22: 세 Today owner link와 `/institutional-portfolios`, `/backtest`, `/ingestion`, `/reference`를 포함한 기존 7개 목적지의 렌더링 연속성을 확인했다. `/today` direct URL은 Streamlit default-page 규칙상 root `/`로 fallback하므로 canonical 주소를 문서에 `/`로 고정했다.
- 2026-07-22: QA screenshot `today-home-b-browser-qa.png`를 생성했으며 generated artifact로 stage하지 않는다.
