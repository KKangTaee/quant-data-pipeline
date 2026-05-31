# Robustness Lab V1 Plan

Status: Active
Created: 2026-05-28

## 이걸 하는 이유?

현재 Practical Validation은 stress window, rolling validation, sensitivity, overfit audit를 이미 계산하지만, 사용자가 Final Review에서 "이 전략이 특정 기간, 특정 구성, 특정 비중에만 과하게 의존하는가?"를 한 번에 읽기 어렵다.

이 task는 새 저장소나 사용자 메모 기능을 추가하지 않고, 기존 검증 결과를 compact Robustness Lab board로 묶어 실전 검토 전 판단 근거를 선명하게 만드는 작업이다.

## Scope

- 기존 stress / sensitivity / rolling / overfit evidence를 compact board로 요약한다.
- board는 `robustness_validation` 아래에 넣어 새 top-level 저장 체인을 만들지 않는다.
- Practical Validation과 Final Review에 같은 board 의미를 표시한다.
- Final Review / Selected Dashboard evidence read model에서 board summary row를 펼칠 수 있게 한다.
- service contract test로 board shape와 final evidence expansion을 검증한다.

## Non-Goals

- 새 JSONL registry 추가
- run history / raw stress row / full replay artifact 저장
- strategy-specific parameter perturbation engine 신규 구현
- live approval, broker order, auto rebalance 표현 추가

## Verification Plan

- relevant Python compile
- `tests/test_service_contracts.py`
- UI-engine boundary check
- `git diff --check`
- Browser smoke for Practical Validation / Final Review
