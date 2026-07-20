# Portfolio Monitoring Position Events V1 Plan

Status: Design Approved
Date: 2026-07-20

## 이걸 하는 이유?

Portfolio Monitoring의 직접 개별주식은 최초 등록 때만 정수 수량을 입력할 수 있다. 등록 후 최초 수량 오류를 바로잡거나 실제 추가매수·일부매도를 반영할 수 없어 현재 보유수량, 평가금액, 손익과 가치곡선이 실제 관찰 대상과 어긋날 수 있다.

## 전체 흐름

1. 1차 — 계약 확정: 최초 수량 정정과 매수·매도 이벤트의 저장, 현금흐름, 성과 계산 계약을 고정한다.
2. 2차 — 구현: DB 원장, 멱등 명령, 거래 인식 가치곡선, Python read/command bridge, 개별종목 보유내역 UI를 연결한다.
3. 3차 — 검증·정리: 기존 데이터 회귀, Python/React/DB 검증, desktop/mobile Browser QA, durable docs와 root handoff를 정렬한다.

## 범위

- 포함: 직접 등록한 미국 개별주식 중 `fixed_shares` 항목의 최초 수량 정정, 추가매수, 일부매도, 거래 수정·취소.
- 포함: 거래일 DB 종가를 기본 체결가로 자동 입력하고 사용자가 수정할 수 있는 가격 입력, 정수 수량, 선택적 수수료와 메모.
- 포함: 추가매수=외부 입금, 일부매도=외부 출금인 현금흐름 조정 손익·수익률·CAGR·MDD.
- 제외: ETF, `fixed_notional`, Final Review selected strategy, 퀀트 백테스트, 전량매도, broker/account sync, 주문, 자동 리밸런싱, 포트폴리오 공통 현금계정.

## Stop Condition

- 기존 이벤트 없는 항목의 계산 결과가 유지된다.
- 승인된 개별주식만 수량 정정과 거래 기록을 수행할 수 있다.
- 거래 수정·취소와 과거 정정 이후에도 모든 후속 매도 수량이 유효하다.
- 관련 자동 검증과 actual responsive Browser QA를 통과하고 문서가 현재 계약과 일치한다.
