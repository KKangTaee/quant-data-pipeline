# Status

- 2026-07-11: 작업 시작. 사용자 승인에 따라 1차~6차 개발 / QA / 커밋 흐름으로 진행.
- 2026-07-11: 초기 진단 결과, change board의 `비중 증가`, `비중 감소`, `더 이상 보고 안 됨` 0은 watchlist manager별 이전 filing이 local DB에 없기 때문으로 확인.
- 2026-07-11: 상단 manager rail reset은 Streamlit component key가 selected CIK별로 바뀌어 React가 remount되는 구조와 관련 있음.

## Current Step

6차 docs sync / commit 준비.

## Completed

- 1차: current UI / loader / price DB route와 이전 filing 부재 원인 확인.
- 2차: focused tests로 schema index, performance model, selected security model, popularity ranking, stable key / scroll contract를 고정.
- 3차: `ix_report_period_cusip_cik`, popularity loader, CUSIP-level service aggregation, portfolio performance / chart read models 구현.
- 4차: React workbench에 performance panel, selected-security detail, daily/weekly/monthly chart, popularity ranking tab, scroll preserve, pending timeout fallback 연결.
- 5차: focused tests, py_compile, npm build, git diff check, UI/engine boundary scan, Browser QA 완료.
