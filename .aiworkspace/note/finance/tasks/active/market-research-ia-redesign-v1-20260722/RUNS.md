# Market Research IA Redesign V1 Runs

Status: Complete
Last Updated: 2026-07-22

## 2026-07-22

- finance durable docs, Today IA recommendation, Overview code ownership과 active research를 읽었다.
- local sub-dev Streamlit `http://localhost:8501/overview` actual desktop 화면을 Market Context, Market Movers, Futures Macro, Sentiment, Events별로 점검했다.
- local root Today 화면과 Market Research 상단 중복을 비교했다.
- navigation/page/module header/Market Movers handoff를 test-first로 구현하고 7개 implementation/test commit으로 분리했다.
- written spec 승인 후 `superpowers:writing-plans`로 six-task test-first implementation plan을 작성했다.
- `tests/test_market_research_navigation.py`: 14 passed.
- `tests/test_today_home.py`: 29 passed, 2 subtests passed.
- 관련 service contract 회귀: fresh run 기준 376 passed, 490 deselected, 6 subtests passed.
- 전체 `tests/test_service_contracts.py` 기준선은 848 passed, 15 failed, 3 deselected였다. 실패는 Backtest/Practical Validation 11개, Futures Macro thermometer 계산 3개, AAII header 1개이며 이 task diff가 해당 구현 파일을 변경하지 않았음을 확인했다.
- frontend: Node tests 4 passed, `npx tsc --noEmit` passed, Vite production build passed.
- 관련 Python module `py_compile`과 `git diff --check`를 통과했다.
- fresh Streamlit QA server에서 desktop·760px·420px 목적형 navigation, legacy query canonicalization, Today CTA, Market Movers SNDK → U.S. Stock handoff, overflow 0, browser warning/error 0을 확인했다.
- QA screenshot: workspace root의 generated artifact `market-research-ia-v1-qa.png`; commit에는 포함하지 않는다.
