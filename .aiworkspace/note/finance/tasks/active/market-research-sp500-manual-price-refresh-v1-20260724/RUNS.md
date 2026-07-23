# Market Research S&P 500 Manual Price Refresh V1 Runs

Status: Completed
Last Updated: 2026-07-24

## Diagnosis

- Browser DOM: S&P 500 header `기준일 2026-07-16` 재현
- DB query: `^GSPC=2026-07-16`, `SPY=2026-07-22`
- NYSE calendar: latest completed session `2026-07-23`
- read-only provider probe: `^GSPC` / `SPY` latest `2026-07-23`
- run history: `collect_sp500_valuation_context` 0건
- automation dry-run: `sp500_valuation` due, last run 없음
- system check: project launchd/cron registration 없음

## Design

- finance task intake와 active task document contract 확인
- user-approved manual-only flow를 PLAN/DESIGN/STATUS/NOTES/RUNS/RISKS로 기록

## 2026-07-24 Implementation Planning

- `rg --files`와 대상 source/test 검색으로 실제 소유 파일과 build command 확인
- `app/services/nyse_calendar.py` public API 확인 후 계획의 거래일 gap 계산을 `previous_nyse_trading_day()` 기준으로 확정
- plan placeholder scan: red flag 없음
- Markdown fence check: 100개, balanced
- `git diff --check -- IMPLEMENTATION_PLAN.md`: pass

## 2026-07-24 Implementation And Automated Verification

- baseline focused suite: 89 tests passed
- freshness contract: 7 tests passed
- market context valuation + freshness: 37 tests passed
- refresh action + stock regression: 15 tests passed
- market context event/component contract: 34 tests passed
- React focused tests and full market context suite: pass
- initial `npm run build`: failed because component-local `node_modules` and `vite` executable were absent
- `npm ci`: 112 packages installed, 0 vulnerabilities
- production `npm run build`: Vite 6.4.3, 171 modules, pass

## 2026-07-24 Actual Browser QA

- isolated app: `http://localhost:8511/overview?overview_tab=sp500`
- stale 화면에서 최신 완료 장 `2026-07-23`, 저장 가격일 `2026-07-16`, 수동 action 노출 확인
- 실제 button 1회 실행 중 disabled `갱신 중` 상태 확인
- 실행 결과: `overview_sp500_price_refresh`, success, 42 rows, 0 failures, 2.971 seconds
- DB postcondition: `^GSPC=2026-07-23`, `SPY=2026-07-23`
- 성공 화면: `가격 기준일 2026-07-23`, PER 28.31, Z-score 1.14, gap +6.5%
- reload: READY 상태에서 action/completion bar 숨김
- 420px viewport: horizontal overflow와 clipping 없이 통과
- generated screenshots: `sp500-manual-price-refresh-stale-qa.png`, `sp500-manual-price-refresh-current-qa.png`; commit 제외

## 2026-07-24 Final Verification

- S&P focused regression: 97 tests, pass
- changed Python module compile: pass
- market-context-valuation production build: Vite 6.4.3, 171 modules, pass
- `git diff --check`: pass
- finance refinement hygiene: pass; generated run history와 QA artifact는 unstaged 유지
- broad `tests.test_service_contracts`: 966 tests 중 기존 baseline 11 failures / 7 errors 재현. 실패는 Practical Validation, Futures Macro, Sentiment 등 이번 S&P 변경 범위 밖이며 이전 main-dev merge 기록의 18 failures와 동일하다.
- UI/engine boundary check: 기존 `app/services/backtest_workflow_shell.py -> app.web.backtest_workflow_routes` 1건 재현. 이번 변경 파일에는 신규 boundary violation이 없다.
