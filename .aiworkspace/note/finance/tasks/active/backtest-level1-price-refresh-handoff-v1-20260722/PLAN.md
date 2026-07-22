# Plan

## 이걸 하는 이유?

Level1 백테스트가 사용자가 요청한 종료일보다 이른 공통 가격일까지 계산되어도 현재 Result Workspace는 이를 행동 가능한 문제로 보여주지 않는다. 오래된 결과가 그대로 Level2 후보가 되는 것을 막고, 사용자가 필요한 종목 가격만 DB에 보강한 뒤 같은 설정으로 다시 실행할 수 있어야 한다.

## Goal

- 요청 종료일의 마지막 완료 NYSE 거래일과 백테스트 공통 가격일을 비교한다.
- 가격 보강이 필요하면 Level1 결과 상단에 설명과 수동 최신화 action을 표시한다.
- 최신화 전과 최신화 후 재실행 전에는 Level2 인계를 차단한다.
- 최신화는 기존 ingestion job을 사용하고 자동 백테스트는 실행하지 않는다.

## Scope

- Level1 Single Strategy와 Portfolio Mix Result Workspace
- 기존 `backtest_price_refresh` plan / runner 재사용
- React Result Workspace와 Python fallback의 동일 계약
- 같은 설정 재실행 action과 결과 lifecycle 연동
- focused contract test, actual GTAA DB run, desktop / 760px Browser QA

## Out Of Scope

- provider 직접 호출 또는 새 OHLCV collector
- 자동 백테스트 재실행
- registry / saved setup 변경
- Level2 / Final Review validation 기준 변경
- provider gap을 임의 가격이나 합성 데이터로 채우는 처리

## Roadmap

1. 진단·설계: 승인 완료, written spec 검토 대기
2. 구현: freshness read model, action intent, 수집·재실행 handoff, Level2 blocker
3. 검증·정리: tests, actual GTAA, responsive Browser QA, durable docs, commit

## Stop Condition

사용자가 written spec을 승인하기 전에는 제품 코드 구현 계획이나 구현을 시작하지 않는다.
