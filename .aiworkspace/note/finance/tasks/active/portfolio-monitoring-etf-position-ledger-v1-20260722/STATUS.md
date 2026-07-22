# Status

- 상태: 전체 `3/3차` 완료
- 사용자 선택: ETF `fixed_shares`를 주식과 동일한 append-only position ledger로 지원
- 완료: command validation, valuation, selected read model을 공통 stock/ETF fixed-shares 판정으로 통합하고 비원장 항목의 빈 숫자 카드를 제거
- actual QA: QQQ 4주·$2,839.13, SOXX 6주·$3,316.14와 최초 설정 정정·매수/매도 action, clean console 확인
- 경계: fixed-notional ETF, selected strategy, quant backtest, DB schema는 변경하지 않음
