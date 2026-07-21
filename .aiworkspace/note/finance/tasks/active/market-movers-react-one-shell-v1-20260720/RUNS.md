# Runs

## 2026-07-20

- SP500 daily market snapshot: `OK`, ranking row 확인.
- SP500 daily sector/industry group snapshot: `OK`, current flow와 market-cap bellwether 확인.
- selected TRV research snapshot: financial factor series 확인, current valuation unavailable 확인.
- TDD/회귀: decision UI/read-model/research `24 passed`; Market Movers service contracts `126 passed`.
- React production build: Vite `170 modules transformed`, canonical `component_static/` 갱신.
- actual decision payload smoke: SP500 `OK / 20 rows / TRV`, Top1000 `OK / 20 rows / ABT`, Top2000 `OK / 20 rows / SKYQ`.
- Browser QA: sector→industry, daily→monthly, ranking `TRV→ALL`, 상세 조사, 재무 tab, 분기→연간 전환을 확인했다.
- responsive QA: 989px component에서 `604.094px / 372.906px`, 693px와 353px에서 1열; 각 폭의 `scrollWidth == clientWidth`.
- Browser console error는 0건이었다. Streamlit 자체 warning은 있었지만 one-shell interaction을 막는 오류는 없었다.
- full `tests/test_service_contracts.py` → `839 passed, 13 failed, 41 subtests passed`. 13건은 Market Movers가 아닌 Practical Validation / Final Review / Sentiment contract이며 3차 기록과 같은 failure 목록이다.
