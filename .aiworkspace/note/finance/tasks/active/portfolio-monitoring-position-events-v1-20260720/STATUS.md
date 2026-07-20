# Portfolio Monitoring Position Events V1 Status

Status: Design Approved
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

## Next

- 사용자가 written design을 검토·승인하면 detailed implementation plan을 작성한다.
- 구현은 plan 승인 이후 test-first로 시작한다.
