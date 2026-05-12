# Phase 23 Backtest Report Archive

## 목적

이 폴더는 `Phase 23 Quarterly And Alternate Cadence Productionization`에서 나온
검증용 backtest report를 모아 두는 archive다.

여기 report는 기본적으로 투자 후보를 고르는 문서가 아니다.
quarterly / alternate cadence 기능이 실제 DB-backed backtest, compare, history, replay 흐름에서
재현 가능한 제품 기능으로 동작하는지 확인하기 위한 개발 검증 문서다.

## 현재 문서

- `PHASE23_QUARTERLY_CONTRACT_SMOKE_VALIDATION_FIRST_PASS.md`
  - quarterly strict 3개 family가 non-default portfolio handling contract를 받은 상태로
    실제 DB-backed runtime에서 실행되는지 확인한 smoke validation report
  - `Weighting`, `Rejected Slot Handling`, `Risk-Off`, `Defensive Tickers` 값이
    result bundle meta에 남는지도 같이 확인한다
