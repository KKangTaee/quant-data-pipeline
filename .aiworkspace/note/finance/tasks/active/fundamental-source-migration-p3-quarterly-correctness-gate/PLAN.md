# Phase 3. Quarterly Correctness Gate Plan

## 이걸 하는 이유?

quarterly statement shadow에 `10-K` / `10-K/A` full-year flow value가 들어오면 매출, 순이익, 현금흐름 같은 기간 flow metric이 분기값처럼 보일 수 있다. Phase 3는 synthetic Q4를 만들기 전에 이 오염이 Market Movers / backtest / factor runtime에서 usable quarterly row로 소비되는 길을 차단한다.

## 범위

- `finance/data/fundamentals.py`: 새 quarterly shadow 생성 시 unsafe filing의 flow metric sanitize.
- `finance/loaders/fundamentals.py`: quarterly statement fundamentals shadow read gate.
- `finance/loaders/factors.py`: factor shadow read gate와 `nyse_fundamentals_statement` form type join.
- `finance/financial_source_policy.py`: quarterly statement source policy helper.
- `tests/test_service_contracts.py`: 10-K quarterly flow 혼입 방지 계약 테스트.
- `docs/data/*`: schema 변경이 아니라 policy layer 변경임을 문서화.

## 완료 조건

- quarterly `10-K` / `10-K/A` row의 flow metrics가 신규 shadow 생성 경로에서 분기 flow로 유지되지 않는다.
- quarterly statement fundamentals / factors loaders는 `10-Q` / `10-Q/A` row만 반환한다.
- annual strict path와 legacy broad compatibility path는 바꾸지 않는다.
- DB table drop, schema 확장, paid provider 추가를 하지 않는다.
