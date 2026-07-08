# Fundamental Source Migration P1 Source Contract Freeze

## 이걸 하는 이유?

EDGAR-first migration이 여러 화면과 backtest runtime을 지나가므로, 먼저 financial statement source contract를 코드와 문서에 고정한다. 이 phase의 목표는 동작 전환보다 source identity를 명시해 다음 phase에서 broad yfinance fallback과 statement shadow primary path가 조용히 섞이지 않게 하는 것이다.

## Scope

- broad yfinance fundamentals/factors loader output에 legacy source contract columns 추가
- EDGAR statement shadow fundamentals/factors loader output에 statement source contract columns 추가
- Market Movers research snapshot financial payload에 source metadata 전달
- strategy evidence inventory에 factor strategy source contract 추가
- data docs에서 broad tables를 canonical처럼 읽히지 않게 정리

## Non-Scope

- Market Movers annual source priority 전환
- quarterly 10-K/FY correction
- backtest catalog 기본 선택 변경
- yfinance collector 삭제
- DB schema 변경 또는 table drop

## Completion Criteria

- financial read model이 `financial_source`, `financial_source_mode`, `source_table`, `available_at`, `form_type`, `accession_no`를 같은 이름으로 읽을 수 있다.
- broad `nyse_fundamentals` / `nyse_factors`는 `legacy_broad_yfinance`로 표시된다.
- statement shadow `nyse_fundamentals_statement` / `nyse_factors_statement`는 `sec_edgar_statement_shadow`로 표시된다.
- focused tests and compile checks pass.
