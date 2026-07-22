# Market Research React Navigation V1 Runs

Status: Complete
Last Updated: 2026-07-22

## 2026-07-22

- finance task intake와 current Market Research docs/code ownership을 확인했다.
- existing Today/Events/Market Movers React wrapper, Vite bundle, Streamlit event/height bridge patterns을 읽었다.
- 사용자가 A안인 full React header/navigation scope를 승인했다.
- written spec을 사용자가 승인했다.
- `writing-plans`로 Python bridge, React component, integration/QA의 3-task test-first plan을 작성했다.
- Python bridge RED: 신규 payload/event wrapper import가 없어 collection 실패함을 확인했다.
- Python bridge GREEN: focused 3 tests, py_compile, diff check 통과.
- React RED: source import가 없는 상태에서 Vitest 실패를 확인했다.
- React GREEN: Vitest `4 passed`, TypeScript typecheck, production build 통과.
- integration RED: React-first/fallback page 계약 2건 실패를 확인했다.
- integration GREEN: React-first shell과 Streamlit fallback 회귀 통과.
- live QA에서 family click 뒤 URL·본문은 바뀌지만 iframe active payload가 이전 view에 남는 문제를 재현했다.
- rerun regression RED/GREEN 후 `tests/test_market_research_navigation.py`, `tests/test_today_home.py`, 관련 Overview contract: `54 passed`, `2 subtests passed`.
- actual Browser QA: 1280·760·420px, family 3개, canonical view 7개, URL/session 선택 동기화, frame height, keyboard focus, page/frame overflow 0 확인.
- broad `tests/test_service_contracts.py`: 변경 전 기준과 동일한 비범위 Backtest/Practical Validation 13, Futures Macro 3, Sentiment/AAII 2의 18 failures가 남는다. Market Research legacy Streamlit widget contract는 fallback 대상으로 갱신했다.
- commits: `08a9bed97`, `bd034a8c2`, `4db200828`.
