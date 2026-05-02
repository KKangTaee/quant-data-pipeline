# Phase 19 Rejected Slot Handling Contract First Slice

## 무엇을 바꿨는가
- strict annual family의 trend rejection 처리 옵션을
  두 개 독립 boolean에서
  하나의 explicit contract로 정리했다.

## 기존 문제
- 사용자는 아래 두 값을 같이 이해해야 했다.
  - `rejected_slot_fill_enabled`
  - `partial_cash_retention_enabled`
- 즉 실제 의미는 4가지 조합인데,
  UI에서는 두 checkbox를 머릿속으로 조합해야 했다.
- history / payload / runtime warning도 같은 개념을
  boolean 언어로 흩어 읽어야 했다.

## 새 contract
- `Reweight Survivors`
  - trend rejection 이후 남은 종목에 다시 100% 재배분
- `Retain Unfilled Slots As Cash`
  - trend rejection 이후 남은 빈 슬롯을 현금으로 유지
- `Fill Then Reweight Survivors`
  - 먼저 다음 순위의 추세 통과 종목으로 보충한 뒤
    최종 생존 종목에 다시 재배분
- `Fill Then Retain Unfilled Slots As Cash`
  - 먼저 다음 순위 종목으로 보충한 뒤
    끝까지 안 채워진 슬롯만 현금으로 유지

## 구현 위치
- `finance/sample.py`
  - explicit mode constant / compatibility helper 추가
- `app/web/runtime/backtest.py`
  - runtime wrapper가 explicit mode를 받되
    내부 전략 호출은 legacy booleans로 계속 연결
- `app/web/pages/backtest.py`
  - single / compare strict annual form
  - history prefill
  - load-into-form
  - help popover
  - payload sync

## 왜 이렇게 구현했는가
- 전략 엔진을 한 번에 크게 흔들지 않고
  operator-facing contract만 먼저 정리하고 싶었기 때문이다.
- 그래서 current strategy logic은 그대로 두고,
  explicit mode -> legacy booleans 변환 계층을 먼저 추가했다.

## 호환성
- old run payload:
  - booleans만 있어도 explicit mode를 복원
- new run payload:
  - explicit mode와 legacy booleans를 같이 저장

## 이번 slice에서 확인한 것
- `py_compile` 통과
- `.venv` import smoke 통과
- broad rerun은 이번 slice 범위에 포함하지 않음

## 남은 일
- history / interpretation 텍스트를 더 operator-friendly하게 정리
- next structural contract cleanup slice 선택
