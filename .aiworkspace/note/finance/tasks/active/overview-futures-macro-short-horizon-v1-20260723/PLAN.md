# Overview Futures Macro Short-Horizon V1 Plan

Status: Implementation planning complete; execution mode selection pending
Roadmap: 0/4 implementation stages complete
Last Updated: 2026-07-23

## 이걸 하는 이유?

현재 Futures Macro는 일봉 갱신 때 17개 선물의 10년 이력을 반복 수집하고 전체 조건부 전망을 다시 계산해 40~50초가 걸린다. 첫 화면도 현재 관측, 미래 5D/20D, 2D 경로, 60D 이력을 한 번에 보여줘 단기 방향을 빠르게 판단하기 어렵다.

이번 작업은 `최근 1거래일 새 충격 -> 최근 5거래일 단기 방향 -> 향후 5거래일 검증 결론`을 첫 판단 흐름으로 만들고, 6개 family를 `핵심 4 + 확인 2`로 설명한다. routine refresh는 저장 이력을 재사용해 10년 전체 다운로드를 반복하지 않는다.

## Roadmap

1. 승인된 단기 판단 흐름, `NO_EDGE` 사용자 문구, `핵심 4 + 확인 2` payload/UI 계약을 구현한다.
2. bootstrap과 routine daily refresh를 분리해 routine 경로가 17개 전 종목의 10년 이력을 반복 다운로드하지 않게 한다.
3. refresh 전후 저장 일봉 fingerprint가 같으면 전망 materialization을 재실행하지 않고 compatible latest-good snapshot을 재사용한다.
4. Python/React 회귀, 성능 측정, desktop/mobile actual Browser QA와 durable docs 정렬을 완료한다.

## Scope

- 최근 1/5/20거래일 관측 역할 분리
- 향후 5거래일 검증 결론만 primary future surface에 표시
- `NO_EDGE`를 `방향 예측 근거 부족`으로 번역하고 baseline 의미를 평문으로 설명
- 4개 핵심 방향과 2개 확인 신호를 분리해 family 6/6을 빠짐없이 설명
- 17개 수집, 15개 family 직접 입력, DXY 공유, 은 원본 관찰 역할을 secondary disclosure에 표시
- 기존 5D/20D backend validation과 immutable forecast evidence 보존
- routine daily overlap collection과 unchanged-input materialization fast path
- 관련 서비스, payload, React, tests, production static bundle, task/durable docs

## Out Of Scope

- 6개 family 산식, 가중치, threshold 변경
- DXY 또는 은을 신규 family 입력으로 추가
- 미래 20D 모델과 historical artifact 삭제
- publication gate 완화, `NO_EDGE`를 방향 신호로 변환
- provider 교체, futures DB schema 변경, live order/trading signal
- 첫 화면에 run/row/failure 중심 운영 진단 패널 추가
- 경제 사이클이나 Market Movers 화면 개편

## Stop Condition

- 첫 화면에서 최근 1/5/20거래일의 역할과 향후 5거래일 검증이 혼동되지 않는다.
- 핵심 4개와 확인 2개가 모두 실제 stored family payload에서 계산되고 hardcoded market conclusion을 사용하지 않는다.
- `NO_EDGE`는 관측 실패나 반대 방향 신호가 아니라 baseline 대비 추가 정확도 부재로 설명된다.
- routine refresh가 `10y/1d`를 17개 전 종목에 반복 요청하지 않는다.
- 입력 일봉이 바뀌지 않은 refresh는 full pattern outlook 계산을 건너뛴다.
- 입력이 바뀐 refresh는 기존 point-in-time, 5D gate, latest-good snapshot 계약을 보존한다.
- 관련 자동 회귀와 desktop/mobile Browser QA가 통과한다.

## Current Stage

- 전체 roadmap 중 설계 승인과 상세 implementation plan 작성까지 완료했다.
- 제품 코드, 수집 동작, React bundle은 아직 변경하지 않았다.
- 다음 단계는 `IMPLEMENTATION_PLAN.md`를 기준으로 inline 또는 subagent-driven 방식 중 하나를 선택해 1~4차를 순서대로 구현하는 것이다.
