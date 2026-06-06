# Risk-On Momentum 5D V1 Plan

Status: Active

## Goal

`Backtest > Backtest Analysis > Single Strategy`에 단기 스윙 연구 전략 `Risk-On Momentum 5D`를 추가한다.

## 이걸 하는 이유?

기존 Backtest 흐름은 월말 / 리밸런싱 중심 전략이 많다. 이번 작업은 장마감 후 후보를 고르고 다음 거래일 시가에 진입 / 청산하는 단기 스윙 연구 기능을 추가해, 기존 DB 가격 / 재무 / futures macro 데이터를 활용한 짧은 보유기간 전략 검증을 가능하게 한다.

## Scope

- `close_based` 실행 모드와 `fixed_pct` 청산을 1차 실행 대상으로 구현한다.
- 기본 universe는 미국 주식 `Top1000`이다.
- macro filter는 futures macro thermometer의 `Mean Z` 기준 hard filter로 적용한다.
- 거래 로그와 후보 스캐너 상세 row는 generated run artifact로 저장하고, history에는 compact pointer만 남긴다.
- 투자 추천, live approval, broker order, auto rebalance 기능은 추가하지 않는다.

## Stop Condition

- Single Strategy에서 `Risk-On Momentum 5D` 실행 가능
- 결과 화면에서 성과, benchmark 비교, 거래 로그, 후보 스캐너 확인 가능
- history load/run again에 핵심 설정이 보존됨
- focused tests와 compile/diff checks 통과 또는 남은 검증 공백 기록
