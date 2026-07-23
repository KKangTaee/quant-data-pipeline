# Market Research S&P 500 Manual Price Refresh V1 Runs

Status: Active
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
