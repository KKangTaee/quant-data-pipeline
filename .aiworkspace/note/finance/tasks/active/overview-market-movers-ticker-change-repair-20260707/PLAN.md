# Overview Market Movers Ticker Change Repair 2026-07-07

## 이걸 하는 이유?

Market Movers Top1000 / Top2000에서 `SATS -> ECHO`, `VSCO -> VSXY`처럼 회사는 정상 거래 중인데 이전 ticker로 quote를 요청해 누락되는 문제가 반복될 수 있다. 사용자가 매번 외부 조사를 요청하지 않아도, 앱이 ticker 변경 후보를 감지하고 명시적 복구 action으로 이후 snapshot 수집에 반영하게 한다.

## Roadmap

1. 1차: ticker alias 저장 기반 추가.
   - 범위: `finance_meta.market_symbol_alias` schema, writer / reader / resolver.
   - 완료 조건: old symbol -> active quote symbol mapping을 idempotent하게 저장하고 조회한다.
2. 2차: quote gap ticker 변경 후보 감지.
   - 범위: missing quote diagnostics에 alias candidate probe를 추가한다.
   - 완료 조건: `SATS -> ECHO`, `VSCO -> VSXY` 같은 고신뢰 후보를 grouped missing model에 표시할 수 있다.
3. 3차: Market Movers 복구 action 추가.
   - 범위: Coverage trust / refresh action facade / UI dispatch.
   - 완료 조건: 사용자가 `티커 변경 복구 적용`을 눌러 alias를 저장할 수 있다.
4. 4차: intraday snapshot 수집에 alias 적용.
   - 범위: Top coverage quote snapshot target resolution.
   - 완료 조건: 저장된 alias가 있으면 quote는 새 ticker로 조회하되 snapshot row는 원래 universe symbol에 연결된다.
5. 5차: docs / runbook / QA 정리.
   - 범위: data docs, Overview runbook, root handoff logs, focused tests.
   - 완료 조건: 반복 운영 절차와 데이터 의미가 durable docs에 남고 검증 명령이 통과한다.

## 이번 작업에서 하지 않는 일

- ticker 변경 후보를 사용자 확인 없이 자동 적용하지 않는다.
- universe membership symbol 자체를 일괄 rewrite하지 않는다.
- paid provider나 broker / live trading semantics를 추가하지 않는다.
- registry / saved JSONL / run history generated artifact를 커밋하지 않는다.
