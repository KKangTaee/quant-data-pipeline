# Overview Market Movers Statement Collection Status

## 이걸 하는 이유?

Overview > Market Movers > 기본 지표에서 연간 / 분기 재무제표 수치가 어느 공시 기준인지 보이기 시작했지만, 사용자는 "현재 받아야 할 재무제표가 있는데 DB 반영이 늦은 상태"인지도 함께 확인해야 한다.

## 범위

- 기존 EDGAR filing ledger를 loader로 읽는다.
- Market Movers research snapshot에서 최신 EDGAR 10-Q / 10-K report date와 statement shadow 반영 period를 비교한다.
- 기본 지표 하단에 재무제표 수집 상태를 표시한다.

## 완료 조건

- 최신 EDGAR filing이 statement shadow보다 앞서면 `받아야 할 재무제표 있음`으로 표시한다.
- 최신 filing이 반영되어 있으면 OK 상태로 표시한다.
- filing ledger 조회 실패나 부재는 완료로 오인하지 않고 확인 불가 / 확인 필요로 표시한다.
- 관련 service contract 테스트와 UI QA를 실행한다.
