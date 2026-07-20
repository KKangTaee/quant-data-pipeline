# Portfolio Monitoring Position Events V1 Status

Status: Implementation Plan Ready
Updated: 2026-07-20

## Roadmap

- 전체 roadmap: `1/3차 설계 승인 완료`
- 1차 계약 확정: complete
- 2차 DB/service/UI 구현: not started
- 3차 regression/Browser QA/docs closeout: not started

## Current

- 현재 기능에는 최초 등록 이후 수량 수정 및 추가매수·일부매도 원장이 없음을 확인했다.
- append-only revision chain, DB 종가 default + actual execution price override, buy=입금, partial sell=출금 계약을 사용자와 확정했다.
- 적용 범위는 direct U.S. stock + fixed shares로 제한하고 ETF, strategy, fixed notional과 quant backtest를 제외했다.
- detailed implementation plan을 8개 TDD task와 4개 review checkpoint로 작성하고 self-review했다.
- implementation code와 production schema는 아직 변경하지 않았다.

## Next

- 사용자가 execution mode를 선택하면 Task 1 additive schema/repository RED부터 시작한다.
- 전체 `2차`는 Tasks 1-7, `3차`는 Task 8 migration/regression/Browser QA/docs다.
