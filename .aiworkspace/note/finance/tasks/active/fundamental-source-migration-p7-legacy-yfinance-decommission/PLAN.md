# Fundamental Source Migration P7 - Legacy yfinance Decommission

## 이걸 하는 이유?

EDGAR statement shadow가 canonical financial statement path가 된 뒤에도 Ingestion UI에 broad yfinance fundamentals / factors 실행 카드가 남아 있으면, 사용자가 새 source 준비 경로로 오해할 수 있다. 8차는 table / function / package를 삭제하지 않고, active UI entry만 내리고 saved/history replay compatibility를 명시한다.

## Scope

- Remove active Ingestion UI cards that start broad yfinance financial statement collection or factor calculation.
- Keep legacy action handlers for old run history / saved replay compatibility.
- Mark broad `Quality Snapshot` as archived compatibility in the backtest form.
- Keep `nyse_fundamentals` / `nyse_factors`, loader functions, and yfinance package installed.

## Out Of Scope

- Table drop or schema deletion.
- Removing yfinance package.
- Rewriting old run history or saved setup JSONL.
- Replacing every internal compatibility function.

## Done Criteria

- New user-facing Ingestion flow starts from EDGAR annual refresh / statement shadow path for financial statements.
- Legacy broad jobs are not exposed as active collection cards.
- Compatibility handlers remain callable for old history / explicit replay.
- Tests, source audit, and Browser QA pass.
