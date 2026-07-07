# Backtest PIT Universe V1 Plan

## 이걸 하는 이유?

Quality / Value strict annual 백테스트가 현재 market-cap Top-N을 과거 전체 기간에 고정해서 쓰면 survivorship bias와 universe look-ahead가 발생한다. 월말 기준 point-in-time universe snapshot을 DB에 저장하고 백테스트가 그 snapshot을 읽게 만들어, 2016년 실행은 2016년 당시의 근사 large-cap universe를 사용하도록 개선한다.

## Roadmap

1. 1차: PIT universe schema / loader 계약
2. 2차: 월말 snapshot builder
3. 3차: Quality / Value runner 연결
4. 4차: Backtest UI / Data Trust 표시 정리
5. 5차: 문서 sync / QA / closeout

## Scope

- In scope: `finance_meta` schema, DB read/write helper, strict annual Quality / Value / Quality+Value runtime contract, Backtest UI contract label / guidance, Data Trust metadata.
- Out of scope: paid official historical Russell / S&P membership ingestion, broker execution, live monitoring automation.

## Completion Criteria

- PIT monthly snapshot tables can store `as_of_date`, rank, approximate market cap, liquidity, and exclusion evidence.
- Strict annual family can use a PIT monthly snapshot contract instead of current static Top-N.
- UI clearly distinguishes Current Base Universe, Approx Dynamic PIT, and PIT Monthly Snapshot.
- Tests and docs explain that DB-built PIT is still an approximation unless official historical membership / float data is added.
