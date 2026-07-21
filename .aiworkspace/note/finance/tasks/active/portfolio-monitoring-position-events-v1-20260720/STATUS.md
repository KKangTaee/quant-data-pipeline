# Portfolio Monitoring Position Events V1 Status

Status: Complete
Updated: 2026-07-20

## Roadmap

- 전체 roadmap: `3/3차 완료`
- 1차 계약 확정: complete
- 2차 DB/service/UI 구현: complete
- 3차 regression/Browser QA/docs closeout: complete

## Current

- direct U.S. stock + fixed shares 선택 상세에 최초 수량 정정, 추가매수·일부매도, 거래 수정·취소와 보유수량·누적 입출금·현금흐름 조정 손익을 구현했다.
- append-only root/revision event projection, root-stable same-day `event_order`, split-first 수량 검증과 partial-sell 최소 1주 계약을 적용했다.
- exact-date DB close 자동 입력과 manual override provenance를 page/React rerun 경계까지 연결했다.
- buy=외부 입금, partial sell=외부 출금, daily Modified Dietz `0.5` 현금흐름 가중치와 group flow-neutral aggregation을 구현했다.
- 운영 `finance_meta`에는 새 table만 additive 적용했고 기존 group/item/command `1/2/5`건과 registry/saved checksum을 보존했다. 새 event row는 Browser QA 전후 `0`건이다.
- Python 138, React 30, typecheck/build/py_compile/diff check와 actual read-only route, isolated desktop/900/420 Browser QA를 통과했다.

## Boundaries

- ETF, selected strategy, fixed notional, quant backtest는 기존 동작을 유지한다.
- 전량매도는 기존 tracking end가 소유하며 tax lot/FIFO, realized/unrealized cost basis, group cash, broker/account sync는 제공하지 않는다.
- QA screenshot은 generated artifact `portfolio-monitoring-position-events-v1-qa.png`로 남기고 commit하지 않았다.
