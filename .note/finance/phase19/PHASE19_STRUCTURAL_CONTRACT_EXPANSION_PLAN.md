# Phase 19. Structural Contract Expansion And Interpretation Cleanup

## 목적
- `Phase 18`에서 열린 strict annual structural redesign lane을
  operator가 계속 써도 헷갈리지 않는 contract로 정리한다.
- deep backtest를 다시 크게 열기 전에
  구조 옵션, history 복원, 해석 문구를 먼저 안정화한다.

## 쉽게 말하면
- 구조 레버는 이미 조금씩 생겼다.
- 이제는 그것을
  - 폼에서 읽기 쉽고
  - payload/history에서 복원 가능하고
  - 경고 문구와 interpretation도 일관된
  "usable contract"로 정리하는 단계다.

## 왜 필요한가
- 지금 구조 옵션이 커지는데 UI와 payload가 booleans 조합 중심이면
  이후 검증과 후보 비교가 더 헷갈려진다.
- broad rerun보다 먼저
  contract semantics를 정리해야 deep validation의 해석도 덜 흔들린다.

## 현재 구현 우선순위
1. rejected-slot handling explicit contract
2. risk-off / weighting interpretation cleanup
3. history / compare / prefill / meta alignment
4. minimal validation 고정

## 이번 phase의 운영 원칙
- 구현 우선
- broad rerun 보류
- compile / import smoke / minimal representative validation만 수행
- 기존 payload와 history는 가능한 한 계속 읽히도록 legacy compatibility 유지

## 첫 slice
- `Rejected Slot Handling Contract`
- 목표:
  - 기존 `rejected_slot_fill_enabled + partial_cash_retention_enabled` 조합을
    사용자 입장에서 하나의 명시적 contract로 읽히게 만든다
- current mode:
  - `reweight_survivors`
  - `retain_unfilled_as_cash`
  - `fill_then_reweight`
  - `fill_then_retain_cash`

## 다음에 확인할 것
- history / compare / load-into-form에서 explicit mode가 자연스럽게 복원되는지
- runtime warning이 선택한 handling mode와 같은 언어로 읽히는지
- legacy run payload도 문제없이 다시 열리는지
