# Inflation Policy Core Engines Design

## Module Boundary

| Module | Responsibility |
|---|---|
| `finance/inflation_path.py` | Core PCE index math, state definition, probabilistic monthly/Q4 path |
| `finance/policy_path.py` | SEP/economic/decision component와 policy path probability |
| `finance/yield_resistance.py` | confirmed pivot, dynamic zone, state transition, driver lens |
| `finance/inflation_policy_simulation.py` | forward path join과 reverse conditional reweighting |
| `finance/inflation_policy_validation.py` | chronological metric, baseline, calibration/publication gate |
| `finance/inflation_policy_pipeline.py` | strict loader bundle에서 current/replay snapshot 조립 |

## Safety Decisions

- 연말 Core PCE는 월별 변화율 합계가 아니라 index Q4 평균으로 계산한다.
- SEP state boundary는 release별 분포에서 파생하고 model version에 저장한다.
- SEP 금리 점과 Core PCE histogram은 marginal distribution으로만 사용한다.
- 정책 path는 25bp 횟수를 10년물 bp와 1:1로 연결하지 않는다.
- resistance pivot은 오른쪽 확인일 이후에만 known 상태가 된다.
- break probability는 validation evidence가 없으면 숫자를 만들지 않는다.
- reverse result는 목표를 만족한 simulated path의 조건부분포이며 유일 필요조건이 아니다.
- 새 모듈은 `economic_cycle_*` module/table을 import·query·fallback하지 않는다.

## Publication Contract

- `READY`: 최소 origin·baseline lift·coverage·calibration 조건을 모두 통과
- `LIMITED`: 계산은 가능하지만 정밀 probability 공개 근거가 부족
- `NOT_AVAILABLE`: critical input 또는 target-support path 부재
- `FAILED`: schema/simplex/non-finite 또는 실행 계약 위반
